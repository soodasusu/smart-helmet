# 项目改动清单（change log）

> 生成时间：2026-09-07
> 状态：**全部已完成并验证通过**
> 业务定位：头盔摄像头检测骑行两侧的危险车辆/行人，预警佩戴者避免碰撞

---

## 第一部分：UI 界面优化（浅色蓝白主题）

- 设计系统重写：`variables.css`（纯白背景 + 浅蓝 `#3b82f6` 主题令牌）、`global.css`
- 主题默认浅色、删除科幻背景、新增 SVG 图标组件 `AppIcon.vue`（30+ 图标）替换 emoji
- 浅色化 9 通用组件 + 2 布局组件 + 6 业务组件 + 5 页面

## 第二部分：后端重构（单文件 → 分层）

- `server.py` 780 行 → 8 个模块：`config / db / auth / store / routes(videos, stats, devices, alerts) / socket_handlers`
- 现有接口功能、URL、JSON 格式完全不变

## 第三部分：鉴权 + 数据库安全

- 密码 SHA-256 → PBKDF2-HMAC-SHA256（随机盐，零依赖），旧密码登录自动迁移
- 登录签发带过期 Token（7 天），敏感接口加鉴权装饰器

## 第四部分：数据库新增表（4 张）

| 表 | 作用 | 关键字段 |
|----|------|----------|
| `devices` | 头盔设备登记 + 在线状态 | device_id、name、status、last_heartbeat |
| `alerts` | **预警事件（核心）** | device_id、target_type、behavior、direction、threat_level、经纬度、video_id、alerted |
| `wechat_users` | 微信绑定 | openid、user_id |
| `device_status_log` | 设备状态历史 | device_id、status、created_at |

> `alerts` 表字段含义（按实际业务重新设计）：
> - `target_type` 检测到的目标种类（主要电动车，不限制类型）
> - `behavior` 危险行为（主要：逆行/横穿/违法变道）
> - `direction` 相对方向（左/右两侧）
> - `threat_level` 威胁等级（高/中/低）

## 第五部分：后端新增接口

| 接口 | 方法 | 作用 |
|------|------|------|
| `/api/devices/register` | POST | 设备注册 / 心跳 |
| `/api/devices` | GET | 设备列表（需登录） |
| `/api/alerts` | POST | 头盔上报预警事件 |
| `/api/alerts` | GET | 查询（支持 source/direction/threat_level/device_id 过滤） |
| `/api/alerts/<id>` | PATCH | 更新（标记已提醒等，需登录） |
| `/api/alerts` | DELETE | 删除（需登录） |

## 第六部分：前端配合

- 地图标记后端化：localStorage → `/api/alerts`，按威胁等级（高/中/低）着色
- 文案统一：违法地图 → 预警地图

## 执行结果（全部验证通过）

- ✅ 4 张表（alerts 已替代废弃的 violations 表）
- ✅ 接口端到端测试通过（上报/查询/方向过滤/威胁过滤/改状态/删除）
- ✅ 前端生产构建通过

## 未做（下一步）

- 微信小程序（含 `/api/wechat/login` 接口）
