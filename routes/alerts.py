# routes/alerts.py - 预警事件：头盔检测到周围危险目标的上报 / 查询 / 改状态 / 删除
from datetime import datetime

from flask import Blueprint, request, jsonify

import db
from auth import token_required

bp = Blueprint('alerts', __name__)

VALID_THREAT = {'high', 'medium', 'low'}


@bp.route('/api/alerts', methods=['POST'])
def create_alert():
    """头盔上报预警事件（设备链路，无需 token）"""
    try:
        data = request.json or {}
        threat = data.get('threat_level', 'medium')
        if threat not in VALID_THREAT:
            threat = 'medium'

        conn = db.get_db()
        cur = conn.execute(
            'INSERT INTO alerts (device_id, target_type, behavior, direction, threat_level, '
            'latitude, longitude, video_id, description, source, alerted, created_at) '
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (
                data.get('device_id', ''),
                data.get('target_type', ''),
                data.get('behavior', ''),
                data.get('direction', ''),
                threat,
                data.get('latitude'),
                data.get('longitude'),
                data.get('video_id'),
                data.get('description', ''),
                data.get('source', 'device'),
                1 if data.get('alerted') else 0,
                datetime.now().isoformat()
            )
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'id': cur.lastrowid}), 200

    except Exception as e:
        print(f"预警事件上报错误：{e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    """查询预警事件（地图 / 列表），支持 source/threat_level/direction/device_id 过滤"""
    source = request.args.get('source', None)
    threat = request.args.get('threat_level', None)
    direction = request.args.get('direction', None)
    device_id = request.args.get('device_id', None)

    conn = db.get_db()
    query = 'SELECT * FROM alerts'
    params = []
    conditions = []

    if source:
        conditions.append('source = ?')
        params.append(source)
    if threat:
        conditions.append('threat_level = ?')
        params.append(threat)
    if direction:
        conditions.append('direction = ?')
        params.append(direction)
    if device_id:
        conditions.append('device_id = ?')
        params.append(device_id)
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC'

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify({'alerts': [dict(r) for r in rows], 'count': len(rows)})


@bp.route('/api/alerts/<int:alert_id>', methods=['PATCH'])
@token_required
def update_alert(alert_id):
    """更新预警事件（如标记已提醒 / 已处理）（需登录）"""
    data = request.json or {}

    conn = db.get_db()
    c = conn.cursor()

    if 'alerted' in data:
        c.execute('UPDATE alerts SET alerted = ? WHERE id = ?', (1 if data['alerted'] else 0, alert_id))
    if 'threat_level' in data and data['threat_level'] in VALID_THREAT:
        c.execute('UPDATE alerts SET threat_level = ? WHERE id = ?', (data['threat_level'], alert_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'id': alert_id})


@bp.route('/api/alerts', methods=['DELETE'])
@token_required
def delete_alerts():
    """删除预警事件（支持按 source 批量删除，需登录）"""
    source = request.args.get('source', None)

    conn = db.get_db()
    if source:
        conn.execute('DELETE FROM alerts WHERE source = ?', (source,))
    else:
        conn.execute('DELETE FROM alerts')
    conn.commit()
    conn.close()

    return jsonify({'success': True})
