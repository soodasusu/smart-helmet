import requests
import json

# 测试登录端点
print("测试登录端点...")
try:
    response = requests.post('http://localhost:8000/api/login', json={'username': 'test', 'password': 'test'})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    print(f"响应头: {dict(response.headers)}")
except Exception as e:
    print(f"错误: {e}")

print("\n测试注册端点...")
try:
    response = requests.post('http://localhost:8000/api/register', json={'username': 'testuser', 'password': 'testpass'})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text}")
    print(f"响应头: {dict(response.headers)}")
except Exception as e:
    print(f"错误: {e}")

print("\n测试GET请求...")
try:
    response = requests.get('http://localhost:8000/')
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
except Exception as e:
    print(f"错误: {e}")
