# server.py - 入口：组装 Flask 应用、注册蓝图与 Socket.IO、启动服务
import sys

# 修复 Windows 控制台 GBK 编码导致的 emoji 打印报错
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO

import config
import db
import store
from auth import bp as auth_bp
from routes.videos import bp as videos_bp
from routes.stats import bp as stats_bp
from routes.devices import bp as devices_bp
from routes.alerts import bp as alerts_bp
from socket_handlers import register_socket_handlers

# ═══ 应用与 Socket.IO ═══
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', manage_session=False)

# ═══ 注册蓝图 ═══
app.register_blueprint(auth_bp)
app.register_blueprint(videos_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(devices_bp)
app.register_blueprint(alerts_bp)

# ═══ 注册 Socket.IO 事件 ═══
register_socket_handlers(socketio)

# ═══ 初始化（数据库 / 磁盘同步 / 视频缓存） ═══
db.init_db()
db.sync_videos_from_disk()
store.reload_videos()


# ═══ 静态文件服务 ═══
@app.route('/')
def index():
    """主页 - 返回 Vue 应用"""
    return send_from_directory(config.DIST_FOLDER, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """服务静态文件；未命中时回退到 index.html，交给前端 Vue Router 处理"""
    filepath = config.DIST_FOLDER / filename
    if filepath.is_file():
        return send_from_directory(config.DIST_FOLDER, filename)
    # SPA 前端路由（/login /dashboard /map /videos 等）→ 返回 index.html
    return send_from_directory(config.DIST_FOLDER, 'index.html')


if __name__ == "__main__":
    print("=" * 60)
    print("树莓派视频服务器 (Vue3 + Socket.IO + Token 鉴权)")
    print("=" * 60)
    print(f"视频保存路径：{config.UPLOAD_FOLDER}")
    print(f"Web 界面：http://localhost:8000")
    print(f"上传接口：http://你的 IP:8000/upload_video")
    print(f"Socket.IO: ws://你的 IP:8000/socket.io/")
    print("=" * 60)

    socketio.run(app, host='0.0.0.0', port=8000, debug=False, allow_unsafe_werkzeug=True)
