# config.py - 全局配置（路径 / 密钥 / token 时效）
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

# 上传视频目录
UPLOAD_FOLDER = BASE_DIR / 'uploaded_videos'
# SQLite 数据库文件
DB_PATH = BASE_DIR / 'users.db'
# 前端构建产物目录（dist）
DIST_FOLDER = BASE_DIR / 'dist'

# token 签名密钥 —— 生产环境务必通过环境变量 APP_SECRET_KEY 覆盖
SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'zhi-jian-yun-wei-dev-secret-change-me')

# 登录 token 有效期（秒），默认 7 天
TOKEN_MAX_AGE = 60 * 60 * 24 * 7

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
