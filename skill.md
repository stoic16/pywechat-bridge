# PyWeChat Bridge Skill

## 用途
将 OpenClaw 的调用映射到 Windows 侧运行的 PyWeChat Bridge HTTP 服务。

## 运行边界
- 本 Skill 默认安装在 Linux/WSL。
- 本 Skill 不负责启动微信运行时，不执行任何 `git`/`pip` 部署动作。
- `pywechat/pyweixin` 与 `main.py` 必须在 Windows 运行。

## 环境变量
- `WECHAT_BRIDGE_URL`：桥接服务地址，默认 `http://localhost:8765`

## 最小 API 映射
1. `health_check` -> `GET /`
2. `send_text` -> `POST /send`
3. `list_contacts` -> `GET /contacts`
4. `list_groups` -> `GET /groups`

## 请求/响应约定
- `send_text` 请求体:
```json
{"to": "张三", "message": "你好", "message_type": "text"}
```
- 若桥接不可达，返回错误：`Bridge unavailable, please start Windows runtime`

## 前置条件
1. Windows 已完成手动部署（虚拟环境、依赖、pywechat 安装）。
2. Windows 已启动 `start.bat`，`http://127.0.0.1:8765/` 可访问。
