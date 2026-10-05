import socketio

# 创建 Socket.IO 客户端
sio = socketio.Client()

@sio.event
def connect():
    print("成功连接到服务器")
    # 发送客户端标识
    sio.emit('web_identify', {'client_type': 'web'})

@sio.event
def disconnect():
    print("与服务器断开连接")

@sio.event
def pi_status_update(data):
    print(f"收到树莓派状态更新: {data}")

@sio.event
def web_response(data):
    print(f"收到服务器响应: {data}")

# 连接到服务器
try:
    sio.connect('http://localhost:8000')
    sio.wait()
except Exception as e:
    print(f"连接失败: {e}")
