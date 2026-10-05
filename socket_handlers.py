# socket_handlers.py - Socket.IO 实时事件（树莓派/Web 客户端）
import json

from flask import request
from flask_socketio import emit

import db
import store


def register_socket_handlers(socketio):
    """在 server.py 中调用，注册所有 Socket.IO 事件"""

    @socketio.on('connect')
    def handle_connect(auth=None):
        print(f"Socket.IO 连接：{request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"Socket.IO 断开：{request.sid}")
        store.pi_clients.discard(request.sid)
        store.web_clients.discard(request.sid)
        if not store.pi_clients:
            emit('pi_status_update', {'online': False}, broadcast=True)

    @socketio.on('pi_identify')
    def handle_pi_identify(data):
        print(f"树莓派客户端连接：{request.sid}")
        store.pi_clients.add(request.sid)
        emit('pi_status_update', {'online': True, 'pi_count': len(store.pi_clients)}, broadcast=True)

    @socketio.on('web_identify')
    def handle_web_identify(data):
        print(f"Web 客户端连接：{request.sid}")
        store.web_clients.add(request.sid)
        emit('pi_status_update', {'online': len(store.pi_clients) > 0}, to=request.sid)

    @socketio.on('pi_status_update')
    def handle_pi_status(data):
        print(f"收到树莓派状态：{data}")
        store.pi_clients.add(request.sid)
        emit('pi_status_update', {
            'online': True,
            'pi_count': len(store.pi_clients),
            'status': data.get('status', 'online'),
            'recording': data.get('recording', False)
        }, broadcast=True)

    @socketio.on('web_command')
    def handle_web_command(data):
        command = data.get('command')
        params = data.get('params', {})
        username = data.get('username', 'web_user')

        db.log_command(username, command, json.dumps(params) if isinstance(params, dict) else str(params))

        print(f"📡 Web 命令: {command} (用户={username})")
        if store.pi_clients:
            for sid in store.pi_clients:
                emit('server_command', {'command': command, 'params': params}, to=sid)
        else:
            print("⚠️ 没有树莓派客户端在线")

    @socketio.on('pi_response')
    def handle_pi_response(data):
        print(f"收到树莓派响应：{data}")
        if store.web_clients:
            for sid in store.web_clients:
                emit('web_response', {
                    'status': 'success',
                    'message': data.get('status', 'ok'),
                    'data': data
                }, to=sid)
        else:
            print("没有 Web 客户端在线")
