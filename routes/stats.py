# routes/stats.py - 活动日志 / 使用统计 / 命令历史（需登录）
from datetime import datetime

from flask import Blueprint, request, jsonify

import db
from auth import token_required

bp = Blueprint('stats', __name__)


@bp.route('/api/activity_logs', methods=['GET'])
@token_required
def get_activity_logs():
    """获取活动日志"""
    limit = request.args.get('limit', 50, type=int)
    username = request.args.get('username', None)
    action = request.args.get('action', None)

    conn = db.get_db()
    query = 'SELECT * FROM activity_logs'
    params = []
    conditions = []

    if username:
        conditions.append('username = ?')
        params.append(username)
    if action:
        conditions.append('action = ?')
        params.append(action)
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify({'logs': [dict(r) for r in rows], 'count': len(rows)})


@bp.route('/api/usage_stats', methods=['GET'])
@token_required
def get_usage_stats():
    """获取使用统计数据"""
    username = request.args.get('username', None)
    conn = db.get_db()

    params = [username] if username else []
    user_cond = "AND username = ?" if username else ""

    total_logins = conn.execute(
        f"SELECT COUNT(*) as c FROM activity_logs WHERE action = 'login' {user_cond}", params
    ).fetchone()['c']

    total_uploads = conn.execute(
        f"SELECT COUNT(*) as c FROM activity_logs WHERE action = 'video_upload' {user_cond}", params
    ).fetchone()['c']

    total_commands = conn.execute(
        f"SELECT COUNT(*) as c FROM command_history {'WHERE username = ?' if username else ''}", params
    ).fetchone()['c']

    total_videos = conn.execute("SELECT COUNT(*) as c FROM videos").fetchone()['c']

    today = datetime.now().strftime('%Y-%m-%d')
    today_where = f"WHERE date(created_at) = ? {'AND username = ?' if username else ''}"
    today_params = [today] + params
    today_activities = conn.execute(
        f"SELECT COUNT(*) as c FROM activity_logs {today_where}", today_params
    ).fetchone()['c']

    total_users = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']

    online_where = f"WHERE date(last_login) = ?" if not username else f"WHERE date(last_login) = ? AND username = ?"
    online_params = [today] + (params if username else [])
    online_users = conn.execute(
        f"SELECT COUNT(*) as c FROM users {online_where}", online_params
    ).fetchone()['c']

    conn.close()

    return jsonify({
        'total_logins': total_logins,
        'total_uploads': total_uploads,
        'total_commands': total_commands,
        'total_videos': total_videos,
        'total_users': total_users,
        'today_activities': today_activities,
        'online_users_today': online_users
    })


@bp.route('/api/command_history', methods=['GET'])
@token_required
def get_command_history():
    """获取命令历史"""
    limit = request.args.get('limit', 20, type=int)
    username = request.args.get('username', None)

    conn = db.get_db()
    if username:
        rows = conn.execute(
            'SELECT * FROM command_history WHERE username = ? ORDER BY created_at DESC LIMIT ?',
            (username, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            'SELECT * FROM command_history ORDER BY created_at DESC LIMIT ?', (limit,)
        ).fetchall()
    conn.close()

    return jsonify({'commands': [dict(r) for r in rows], 'count': len(rows)})
