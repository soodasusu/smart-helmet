# routes/devices.py - 设备：登记/心跳、列表、命令下发
from datetime import datetime

from flask import Blueprint, request, jsonify

import db
import store
from auth import token_required

bp = Blueprint('devices', __name__)


@bp.route('/api/devices/register', methods=['POST'])
def register_device():
    """头盔设备注册 / 心跳上报（设备链路，无需 token）"""
    try:
        data = request.json or {}
        device_id = (data.get('device_id') or '').strip()
        if not device_id:
            return jsonify({'error': '缺少 device_id'}), 400

        name = data.get('name', '')
        status = data.get('status', 'online')
        version = data.get('version', '')
        now = datetime.now().isoformat()

        conn = db.get_db()
        c = conn.cursor()
        existing = c.execute('SELECT status FROM devices WHERE device_id = ?', (device_id,)).fetchone()

        if existing:
            c.execute(
                'UPDATE devices SET name = ?, status = ?, last_heartbeat = ?, version = ? WHERE device_id = ?',
                (name, status, now, version, device_id)
            )
            # 状态变化时记录一条状态历史
            if existing['status'] != status:
                c.execute('INSERT INTO device_status_log (device_id, status) VALUES (?, ?)', (device_id, status))
        else:
            c.execute(
                'INSERT INTO devices (device_id, name, username, status, last_heartbeat, version) VALUES (?, ?, ?, ?, ?, ?)',
                (device_id, name, '', status, now, version)
            )
            c.execute('INSERT INTO device_status_log (device_id, status) VALUES (?, ?)', (device_id, status))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'device_id': device_id}), 200

    except Exception as e:
        print(f"设备注册错误：{e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/devices', methods=['GET'])
@token_required
def get_devices():
    """查询设备列表（需登录）"""
    conn = db.get_db()
    rows = conn.execute('SELECT * FROM devices ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify({'devices': [dict(r) for r in rows], 'count': len(rows)})


@bp.route('/command_raspberry', methods=['POST'])
def command_raspberry():
    """接收命令（写入队列，供树莓派轮询）"""
    data = request.json
    command = data.get('command')
    store.command_queue.append(command)
    print(f"📢 收到命令：{command}")
    return jsonify({'success': True, 'command': command})


@bp.route('/get_command', methods=['GET'])
def get_command():
    """树莓派获取命令"""
    if store.command_queue:
        command = store.command_queue.pop(0)
        return jsonify({'command': command})
    return jsonify({'command': None})
