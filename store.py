# store.py - 共享运行时状态（内存列表 / 在线客户端集合）
import db

# 视频记录（内存缓存，与 DB 同步）
uploaded_videos = []

# 命令队列（HTTP 轮询兼容）
command_queue = []

# 在线客户端集合（Socket.IO）
pi_clients = set()    # 树莓派设备
web_clients = set()   # Web 管理端


def reload_videos():
    """从数据库重新加载视频列表到内存"""
    global uploaded_videos
    uploaded_videos = db.load_videos_from_db()
    print(f"📼 已加载 {len(uploaded_videos)} 个视频记录")
    return uploaded_videos
