# 🎥 树莓派视频监控系统 - Vue3 版本

## ✅ 项目已完成

本项目已完全重构为现代化的 Vue3 单页应用，包含以下四个页面：

### 📄 页面结构

1. **登录页面** (`/login`)
   - 简约的登录界面
   - 用户名：`jhn` / 密码：`jhn911808`
   - 登录状态持久化

2. **功能选择页面** (`/home`)
   - 两个功能卡片入口
   - 树莓派控制
   - 违法地图
   - 退出登录按钮

3. **树莓派控制页面** (`/raspberry`)
   - 实时状态显示（运行中/已停止）
   - 启动/停止控制按钮
   - 连接到 Flask API `/command_raspberry`

4. **违法地图页面** (`/map`)
   - 高德地图集成（南京市栖霞区）
   - 三种标记类型：
     - 🔴 危险驾驶
     - 🟠 违法行为
     - 🟡 警告
   - 点击地图添加标记
   - 标记数据本地存储

## 🚀 快速启动

### 方法 1: 一键启动（最简单）⭐

双击运行：
- **生产模式**: `启动服务器.bat` - 自动构建并启动 Flask 服务器
- **开发模式**: `开发模式.bat` - Vite 开发服务器（支持热重载）

### 方法 2: VSCode 中运行

**生产模式**:
1. 打开 VSCode，打开项目文件夹 `D:\show`
2. 按 `F5` 或点击运行按钮
3. 选择 "Python: server.py"

**或使用终端**:
```bash
# 首次运行
npm install
npm run build

# 启动服务器
python server.py
```

**开发模式**（支持热重载）:
```bash
npm run dev
```

### 方法 3: 手动启动

```bash
# 安装依赖（首次运行）
npm install

# 生产模式
npm run build
python server.py

# 开发模式
npm run dev
```

## 📁 项目文件

```
d:\show/
├── src/
│   ├── views/
│   │   ├── Login.vue         # 登录页面
│   │   ├── Home.vue          # 功能选择页面
│   │   ├── Raspberry.vue     # 树莓派控制
│   │   └── Map.vue           # 高德地图
│   ├── router/
│   │   └── index.js          # 路由配置
│   ├── App.vue               # 根组件
│   └── main.js               # 入口文件
├── dist/                     # 构建输出（自动生成）
├── index.html                # HTML 模板
├── package.json              # 依赖配置
├── vite.config.js            # Vite 配置
├── server.py                 # Flask 服务器
├── 启动服务器.bat             # 生产启动脚本
├── 开发模式.bat               # 开发启动脚本
└── 使用说明.md                # 详细文档
```

## 🛠️ 技术栈

- **前端**: Vue 3 + Vue Router 4 + Axios
- **构建**: Vite 5
- **地图**: 高德地图 API v1.4.15
- **后端**: Flask
- **样式**: 原生 CSS + 渐变色设计

## 🌐 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/command_raspberry` | POST | 发送控制命令 |
| `/get_command` | GET | 获取命令 |
| `/upload_video` | POST | 上传视频 |
| `/get_videos` | GET | 获取视频列表 |
| `/play/<filename>` | GET | 播放视频 |
| `/download/<filename>` | GET | 下载视频 |

## 📝 访问地址

- **生产模式**: http://localhost:8000
- **开发模式**: http://localhost:3000

## 🎨 设计特点

- ✨ 现代化渐变背景
- 🎯 简约卡片式设计
- 📱 响应式布局
- 🔄 平滑动画过渡
- 🗺️ 交互式地图标记

## 🔧 配置

高德地图 API Key: `c0db1d466ad24bbe2dd28f829abb5a3f`
地图中心：南京市栖霞区 `[118.9569, 32.1297]`
服务器地址：`http://192.168.43.120:8000`

---

**🎉 项目已就绪，可以直接使用！**
