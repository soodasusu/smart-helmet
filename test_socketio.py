#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Socket.IO 连接测试脚本
"""

import socketio
import time

# 服务器地址
SERVER_URL = 'http://localhost:8000'

# 创建 Socket.IO 客户端
sio = socketio.Client()


@sio.event
def connect():
    print("\n" + "="*60)
    print("✅ 连接成功！")
    print(f"服务器：{SERVER_URL}")
    print(f"时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    # 标识为测试客户端
    sio.emit('web_identify', {})


@sio.event
def disconnect():
    print("\n" + "="*60)
    print("❌ 已断开连接")
    print("="*60 + "\n")


@sio.event
def pi_status_update(data):
    print(f"📊 收到树莓派状态：{data}")


@sio.event
def web_response(data):
    print(f"📨 收到后端响应：{data}")


def main():
    print("=" * 60)
    print("🧪 Socket.IO 连接测试工具")
    print("=" * 60)
    print(f"📡 服务器地址：{SERVER_URL}")
    print("=" * 60)
    print("\n正在连接...")
    
    try:
        sio.connect(SERVER_URL)
        print("✅ Socket.IO 连接成功！")
        print("⏳ 保持连接 10 秒...")
        time.sleep(10)
        
        # 测试发送命令
        print("\n📤 测试发送命令...")
        sio.emit('web_command', {'command': 'test'})
        time.sleep(2)
        
        sio.disconnect()
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 连接失败：{e}")
        print("\n请确保服务器已启动：python server.py")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
