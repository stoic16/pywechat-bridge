# PyWeChat Bridge for OpenClaw

将 PyWeChat/PyWeixin（支持微信 4.1+）集成到 OpenClaw，实现微信消息收发功能。

## 重要说明

### ⚠️ 微信 4.1+ 必须使用 pyweixin

微信 4.1+ 版本需要使用 `pyweixin` 模块：

```python
# 微信 4.1+ 推荐
from pyweixin import WeChat

# 旧版本兼容
from pywechat import WeChat
```

### ⚠️ Windows 环境要求

**pywechat/pyweixin 必须在 Windows 上运行**，因为需要：
- Windows API (pywin32)
- 控制微信窗口 (Win32 GUI)

## 架构

```
┌──────────────────┐         ┌─────────────┐
│  Windows (Host)  │  WinAPI │   微信 4.1+  │
│                  │◄────────│             │
│ PyWeChat Bridge  │         │   客户端    │
│ (pyweixin)       │         │             │
└──────────────────┘         └─────────────┘
```

## 快速开始

1. **克隆本项目**：
   ```powershell
   cd C:\Users\你的用户名\Documents
   git clone <本项目仓库>
   cd pywechat-bridge
   ```

2. **安装依赖**（管理员 PowerShell）：
   ```powershell
   .\install.ps1
   ```

3. **启动 Bridge**：
   ```powershell
   .\start.bat
   # 或 .\start.bat start
   ```

4. **测试服务**：
   ```powershell
   .\test.ps1
   ```

5. **停止服务**：
   ```powershell
   .\start.bat stop
   ```

## 文件说明

| 文件 | 用途 |
|------|------|
| `pywechat_bridge_simple.py` | Bridge 服务（纯 Python，无需 fastapi） |
| `requirements.txt` | Python 依赖 |
| `install.ps1` | Windows 安装脚本 |
| `start.bat` | Windows 启动/停止/重启服务 |
| `test.ps1` | Windows 测试脚本 |
| `README.md` | 项目文档 |

## API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务状态 |
| `/send` | POST | 发送私聊消息 |
| `/send_group` | POST | 发送群消息 |
| `/contacts` | GET | 获取联系人列表 |
| `/groups` | GET | 获取群聊列表 |
| `/search` | POST | 搜索联系人 |
| `/messages/{name}` | GET | 获取聊天记录 |
| `/init` | POST | 初始化微信客户端 |

## 测试

```powershell
# 测试服务
curl http://localhost:8765/

# 测试发送
curl -X POST http://localhost:8765/send -H "Content-Type: application/json" -d '{"to": "张三", "message": "晚上好"}'

# 获取联系人
curl http://localhost:8765/contacts
```

## 故障排除

### ModuleNotFoundError: No module named 'pyweixin'

```bash
# 检查 pyweixin
python -c "from pyweixin import WeChat; print('OK')"

# 如果不存在，使用 pywechat
python -c "from pywechat import WeChat; print('OK')"
```

我们的代码会自动回退。

### Connection refused

1. 检查 Windows 防火墙
2. 确保 Bridge 在运行：`curl http://localhost:8765/`

### 微信 4.1+ 无法发送

1. 确认使用 `from pyweixin import WeChat`
2. 微信窗口必须打开且未最小化
3. 微信版本 >= 4.1

## 版本说明

### 微信 4.1+ 的变化

微信 4.1+ 更新了许多内部 API，旧版 pywechat 可能无法工作。pywechat 项目提供了 `pyweixin` 模块作为兼容层。

**导入优先级**（我们的代码自动处理）：
1. `from pyweixin import WeChat`（微信 4.1+）
2. `from pywechat import WeChat`（旧版本）
3. `MockWeChat`（模拟模式）

## 相关项目

- [PyWeChat](https://github.com/Hello-Mr-Crab/pywechat) - 微信自动化库
- [OpenClaw](https://openclaw.ai) - AI 代理平台

## License

MIT
