# auth.py - 认证：签名 token（itsdangerous）+ 登录/注册路由 + 鉴权装饰器
from functools import wraps
from datetime import datetime

from flask import Blueprint, request, jsonify, g
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

import config
import db

bp = Blueprint('auth', __name__)

_serializer = URLSafeTimedSerializer(config.SECRET_KEY)


# ═══ token 工具 ═══
def generate_token(username):
    """为用户名签发一个带过期时间的签名 token"""
    return _serializer.dumps({'username': username})


def decode_token(token):
    """解析并校验 token，返回 payload（过期/非法会抛异常）"""
    return _serializer.loads(token, max_age=config.TOKEN_MAX_AGE)


def token_required(f):
    """鉴权装饰器：要求请求头携带 Authorization: Bearer <token>"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header[7:] if auth_header.startswith('Bearer ') else None
        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401
        try:
            payload = decode_token(token)
            g.current_user = payload.get('username')
        except SignatureExpired:
            return jsonify({'error': '登录已过期，请重新登录'}), 401
        except BadSignature:
            return jsonify({'error': '无效的认证令牌'}), 401
        return f(*args, **kwargs)
    return decorated


# ═══ 注册 ═══
@bp.route('/api/register', methods=['POST'])
def register():
    """用户注册（密码 PBKDF2 哈希存储，注册即返回 token）"""
    try:
        data = request.json
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        if len(username) < 3:
            return jsonify({'error': '用户名至少3个字符'}), 400
        if len(password) < 6:
            return jsonify({'error': '密码至少6个字符'}), 400

        conn = db.get_db()
        c = conn.cursor()
        if c.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            conn.close()
            return jsonify({'error': '用户名已存在'}), 400

        pwd_hash = db.hash_password(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, pwd_hash))
        conn.commit()
        conn.close()

        db.log_activity(username, 'register', '新用户注册')
        token = generate_token(username)

        return jsonify({'success': True, 'message': '注册成功', 'token': token, 'username': username}), 200

    except Exception as e:
        print(f"注册错误：{e}")
        return jsonify({'error': str(e)}), 500


# ═══ 登录 ═══
@bp.route('/api/login', methods=['POST'])
def login():
    """用户登录 — 校验密码 + 旧格式惰性升级为 PBKDF2 + 返回 token"""
    try:
        data = request.json
        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400

        conn = db.get_db()
        c = conn.cursor()
        user = c.execute(
            'SELECT id, username, password, created_at FROM users WHERE username = ?', (username,)
        ).fetchone()

        if not user:
            conn.close()
            db.log_activity(username, 'login_failed', '用户不存在')
            return jsonify({'error': '用户名或密码错误'}), 401

        if not db.verify_password(password, user['password']):
            conn.close()
            db.log_activity(username, 'login_failed', '密码错误', request.remote_addr)
            return jsonify({'error': '用户名或密码错误'}), 401

        # 旧格式（SHA-256/明文）→ 惰性升级为 PBKDF2
        if db.needs_rehash(user['password']):
            c.execute('UPDATE users SET password = ? WHERE id = ?', (db.hash_password(password), user['id']))

        # 更新登录信息
        c.execute(
            'UPDATE users SET last_login = ?, login_count = login_count + 1 WHERE id = ?',
            (datetime.now().isoformat(), user['id'])
        )
        conn.commit()
        conn.close()

        db.log_activity(username, 'login', '登录成功', request.remote_addr)
        token = generate_token(username)

        return jsonify({
            'success': True,
            'username': username,
            'token': token,
            'created_at': user['created_at']
        }), 200

    except Exception as e:
        print(f"登录错误：{e}")
        return jsonify({'error': str(e)}), 500
