# routes/videos.py - 视频：上传 / 列表 / 播放 / 下载 / 重命名 / 删除
import os
from datetime import datetime

from flask import Blueprint, request, jsonify, send_from_directory

import config
import db
import store
from auth import token_required

bp = Blueprint('videos', __name__)


@bp.route('/upload_video', methods=['POST'])
def upload_video():
    """接收树莓派上传的视频（支持用户名）——设备链路，无需 token"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file'}), 400

        video = request.files['video']
        if video.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        username = request.form.get('username', request.args.get('username', 'unknown'))

        original_name = video.filename
        name, ext = os.path.splitext(original_name)

        if '_' in name:
            parts = name.split('_')
            if len(parts) > 1 and parts[0] not in ['video', 'recording', 'pi']:
                name = '_'.join(parts[1:])

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_filename = f"{username}_{name}_{timestamp}{ext}"
        filepath = os.path.join(config.UPLOAD_FOLDER, new_filename)

        if os.path.exists(filepath):
            unique_id = datetime.now().strftime('%H%M%S%f')
            new_filename = f"{username}_{name}_{unique_id}{ext}"
            filepath = os.path.join(config.UPLOAD_FOLDER, new_filename)

        video.save(filepath)

        video_info = {
            'filename': new_filename,
            'original_filename': original_name,
            'path': str(filepath),
            'size': os.path.getsize(filepath),
            'upload_time': datetime.now().isoformat(),
            'username': username,
            'custom_name': new_filename
        }
        store.uploaded_videos.insert(0, video_info)

        conn = db.get_db()
        conn.execute(
            'INSERT INTO videos (filename, original_filename, path, size, username, upload_time) VALUES (?, ?, ?, ?, ?, ?)',
            (new_filename, original_name, str(filepath), video_info['size'], username, video_info['upload_time'])
        )
        conn.commit()
        conn.close()

        db.log_activity(username, 'video_upload', f'上传视频: {new_filename} ({video_info["size"] / (1024 * 1024):.1f} MB)')

        # 只保留最近 100 个视频文件
        if len(store.uploaded_videos) > 100:
            old_video = store.uploaded_videos.pop()
            conn = db.get_db()
            conn.execute('DELETE FROM videos WHERE filename = ?', (old_video['filename'],))
            conn.commit()
            conn.close()
            try:
                os.remove(old_video['path'])
            except Exception:
                pass

        print(f"📹 视频已上传: {new_filename} (用户={username})")
        return jsonify({'success': True, 'filename': new_filename, 'username': username})

    except Exception as e:
        print(f"上传错误：{e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/get_videos')
def get_videos():
    """获取已上传的视频列表"""
    return jsonify({'videos': store.uploaded_videos})


@bp.route('/play/<filename>')
def play_video(filename):
    """播放视频"""
    try:
        return send_from_directory(config.UPLOAD_FOLDER, filename, mimetype='video/mp4')
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@bp.route('/download/<filename>')
def download_video(filename):
    """下载视频"""
    try:
        return send_from_directory(config.UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@bp.route('/rename_video', methods=['POST'])
@token_required
def rename_video():
    """重命名视频（需登录）"""
    try:
        data = request.json
        old_filename = data.get('old_filename')
        new_filename = data.get('new_filename')
        username = data.get('username', 'unknown')

        if not old_filename or not new_filename:
            return jsonify({'error': 'Missing filename'}), 400

        old_path = os.path.join(config.UPLOAD_FOLDER, old_filename)
        if not os.path.exists(old_path):
            return jsonify({'error': 'File not found'}), 404

        if not new_filename.endswith('.mp4'):
            _, ext = os.path.splitext(new_filename)
            if not ext:
                new_filename = f"{new_filename}.mp4"

        new_path = os.path.join(config.UPLOAD_FOLDER, new_filename)
        if os.path.exists(new_path):
            name, ext = os.path.splitext(new_filename)
            timestamp = datetime.now().strftime('%H%M%S')
            new_filename = f"{name}_{timestamp}{ext}"
            new_path = os.path.join(config.UPLOAD_FOLDER, new_filename)

        os.rename(old_path, new_path)

        for video in store.uploaded_videos:
            if video['filename'] == old_filename:
                video['filename'] = new_filename
                video['path'] = str(new_path)
                video['custom_name'] = new_filename
                video['renamed_by'] = username
                video['rename_time'] = datetime.now().isoformat()
                break

        print(f"✏️ 视频重命名：{old_filename} -> {new_filename}")
        return jsonify({'success': True, 'old_filename': old_filename, 'new_filename': new_filename})

    except Exception as e:
        print(f"❌ 重命名错误：{e}")
        return jsonify({'error': str(e)}), 500


@bp.route('/api/delete_video', methods=['POST'])
@token_required
def delete_video():
    """删除视频文件（需登录）"""
    try:
        data = request.json
        filename = data.get('filename')
        username = data.get('username', 'unknown')

        if not filename:
            return jsonify({'error': 'Missing filename'}), 400

        file_path = os.path.join(config.UPLOAD_FOLDER, filename)

        store.uploaded_videos = [v for v in store.uploaded_videos if v['filename'] != filename]

        conn = db.get_db()
        conn.execute('DELETE FROM videos WHERE filename = ?', (filename,))
        conn.commit()
        conn.close()

        if os.path.exists(file_path):
            os.remove(file_path)

        db.log_activity(username, 'video_delete', f'删除视频: {filename}')
        print(f"🗑️ 已删除视频：{filename}")
        return jsonify({'success': True, 'filename': filename})

    except Exception as e:
        print(f"❌ 删除错误：{e}")
        return jsonify({'error': str(e)}), 500
