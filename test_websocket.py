#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket 测试脚本
用于测试树莓派客户端连接
"""

import socketio
import time
from datetime import datetime

# 服务器地址
SERVER_URL = 'http://localhost:8000'

# 创建 Socket.IO 客户端
sio = socketio.Client()


@sio.event
def connect():
    print(f"\n{'='*60}")
    print(f"✅ 连接成功！")
    print(f"服务器：{SERVER_URL}")
    print(f"时间：{datetime.now()}")
    print(f"{'='*60}\n")


@sio.event
def disconnect():
    print(f"\n{'='*60}")
    print(f"❌ 已断开连接")
    print(f"{'='*60}\n")


@sio.event
def server_command(data):
    print(f"📨 收到服务器命令：{data}")
    # 模拟回复
    sio.emit('pi_response', {
        'status': 'executed',
        'command': data.get('command'),
        'timestamp': datetime.now().isoformat()
    })


@sio.event
def server_message(data):
    print(f"💬 收到服务器消息：{data}")


def test_http_api():
    """测试 HTTP API"""
    import requests
    
    print("\n📋 开始测试 HTTP API...")
    print("-" * 60)
    
    # 测试 1: 获取树莓派状态
    print("\n1️⃣ 测试 GET /api/pi_status")
    try:
        response = requests.get(f'{SERVER_URL}/api/pi_status')
        print(f"   状态码：{response.status_code}")
        print(f"   响应：{response.json()}")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
    
    # 测试 2: 发送命令
    print("\n2️⃣ 测试 POST /api/send_command")
    try:
        response = requests.post(
            f'{SERVER_URL}/api/send_command',
            json={'command': 'test_command'},
            headers={'Content-Type': 'application/json'}
        )
        print(f"   状态码：{response.status_code}")
        print(f"   响应：{response.json()}")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
    
    print("\n" + "-" * 60)
    print("✅ HTTP API 测试完成\n")


def main():
    print("=" * 60)
    print("🧪 WebSocket 测试工具")
    print("=" * 60)
    print(f"📡 服务器地址：{SERVER_URL}")
    print("=" * 60)
    
    # 先测试 HTTP API
    test_http_api()
    
    # 测试 WebSocket 连接
    print("🔌 正在连接 WebSocket...")
    try:
        sio.connect(SERVER_URL)
        print("✅ WebSocket 连接成功！")
        print("⏳ 保持连接 10 秒...")
        time.sleep(10)
        sio.disconnect()
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        print("⏳ 5 秒后重试...")
        time.sleep(5)
        main()


if __name__ == '__main__':
    main()
