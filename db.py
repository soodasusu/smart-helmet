# db.py - 数据库层：连接、初始化、密码哈希、日志记录、磁盘同步
import os
import json
import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime

import config

# ── PBKDF2 参数（Django 风格，标准库实现，零外部依赖） ──
PBKDF2_ITERATIONS = 260000
LEGACY_SALT = "ZhiJianYunWei_2024_SALT"  # 旧版 SHA-256 固定盐（仅用于兼容旧密码）


# ═══ 连接 ═══
def get_db():
    """获取数据库连接（每次返回新连接，线程安全）"""
    conn = sqlite3.connect(str(config.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ═══ 密码哈希（PBKDF2-HMAC-SHA256） ═══
def hash_password(password):
    """生成 PBKDF2 密码哈希，格式：pbkdf2_sha256$iterations$salt$hash"""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('ascii'), PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${dk.hex()}"


def verify_password(password, stored):
    """校验密码，兼容 PBKDF2（新）/ SHA-256（旧）/ 明文（历史遗留）三种格式"""
    if not stored:
        return False

    # 新：PBKDF2
    if stored.startswith('pbkdf2_sha256$'):
        try:
            _, iterations, salt, hash_hex = stored.split('$')
            dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('ascii'), int(iterations))
            return hmac.compare_digest(dk.hex(), hash_hex)
        except Exception:
            return False

    # 旧：SHA-256（固定盐），64 位 hex
    if len(stored) == 64 and all(c in '0123456789abcdef' for c in stored):
        legacy = hashlib.sha256((password + LEGACY_SALT).encode('utf-8')).hexdigest()
        return hmac.compare_digest(legacy, stored)

    # 历史遗留：明文
    return hmac.compare_digest(password, stored)


def needs_rehash(stored):
    """判断存储的密码是否为旧格式（需要升级为 PBKDF2）"""
    return not (stored and stored.startswith('pbkdf2_sha256$'))


# ═══ 初始化 ═══
def init_db():
    """初始化数据库 — 创建所有表"""
    conn = get_db()
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        login_count INTEGER DEFAULT 0
    )
    ''')

    # 兼容旧库：补齐 login_count / last_login 列
    try:
        c.execute('SELECT login_count FROM users LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0')
        c.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP')

    c.execute('''
    CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT,
        path TEXT,
        size INTEGER DEFAULT 0,
        username TEXT,
        upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        custom_name TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS command_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        command TEXT NOT NULL,
        params TEXT,
        status TEXT DEFAULT 'pending',
        response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    ''')

    # ── 设备表（头盔设备登记 + 在线状态） ──
    c.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT UNIQUE NOT NULL,
        name TEXT,
        username TEXT,
        status TEXT DEFAULT 'offline',
        last_heartbeat TIMESTAMP,
        version TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ── 预警事件表（核心：记录头盔检测到的周围危险目标） ──
    # 旧表 violations 字段设计已废弃（错误地按"违法执法"建模），清理之
    c.execute('DROP TABLE IF EXISTS violations')
    c.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        target_type TEXT,
        behavior TEXT,
        direction TEXT,
        threat_level TEXT,
        latitude REAL,
        longitude REAL,
        video_id INTEGER,
        description TEXT,
        source TEXT DEFAULT 'device',
        alerted INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ── 微信绑定表（接小程序用） ──
    c.execute('''
    CREATE TABLE IF NOT EXISTS wechat_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        openid TEXT UNIQUE NOT NULL,
        unionid TEXT,
        user_id INTEGER,
        nickname TEXT,
        avatar_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ── 设备状态历史表（在线/离线时间线） ──
    c.execute('''
    CREATE TABLE IF NOT EXISTS device_status_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")


# ═══ 日志 / 命令记录 ═══
def log_activity(username, action, details='', ip=''):
    """记录用户活动"""
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO activity_logs (username, action, details, ip_address) VALUES (?, ?, ?, ?)',
            (username, action, details, ip)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ 活动记录失败: {e}")


def log_command(username, command, params=''):
    """记录命令历史"""
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO command_history (username, command, params, status) VALUES (?, ?, ?, ?)',
            (username, command, json.dumps(params) if isinstance(params, dict) else params, 'sent')
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ 命令记录失败: {e}")


# ═══ 磁盘同步 ═══
def sync_videos_from_disk():
    """从磁盘同步视频文件到数据库（仅同步新增的）"""
    conn = get_db()
    existing = set(r['filename'] for r in conn.execute('SELECT filename FROM videos').fetchall())
    if os.path.exists(config.UPLOAD_FOLDER):
        for filename in os.listdir(config.UPLOAD_FOLDER):
            if filename.endswith(('.mp4', '.avi', '.mov', '.wmv')) and filename not in existing:
                filepath = os.path.join(config.UPLOAD_FOLDER, filename)
                try:
                    size = os.path.getsize(filepath)
                    parts = filename.split('_')
                    username = parts[0] if len(parts) >= 3 else 'unknown'
                    conn.execute(
                        'INSERT INTO videos (filename, original_filename, path, size, username, upload_time) VALUES (?, ?, ?, ?, ?, ?)',
                        (filename, filename, str(filepath), size, username, datetime.now().isoformat())
                    )
                except Exception as e:
                    print(f"同步视频失败: {filename}, {e}")
    conn.commit()
    conn.close()


def load_videos_from_db():
    """从数据库加载视频列表"""
    conn = get_db()
    rows = conn.execute('SELECT * FROM videos ORDER BY upload_time DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]
