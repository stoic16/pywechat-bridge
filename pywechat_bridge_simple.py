#!/usr/bin/env python3
"""
PyWeChat Bridge - 简化版本 (使用 Python 标准库)
连接 OpenClaw 和 PyWeChat，实现微信消息收发
支持微信 4.1+ 版本（使用 pyweixin 模块）

注意: 微信 4.1+ 需要手动克隆安装 pywechat，使用 pyweixin 模块
"""

import json
import logging
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# 添加手动安装的 pywechat 路径
MANUAL_INSTALL_PATH = os.path.expanduser("~/.local/share/pywechat/pywechat")
if os.path.exists(MANUAL_INSTALL_PATH) and MANUAL_INSTALL_PATH not in sys.path:
    sys.path.insert(0, MANUAL_INSTALL_PATH)
    print(f"[INFO] 已添加手动安装路径: {MANUAL_INSTALL_PATH}")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局状态
wechat_client = None
message_history = []
MAX_HISTORY = 1000
BRIDGE_PORT = 8765


def init_wechat():
    """初始化微信客户端 - 微信 4.1+ 使用 pyweixin"""
    global wechat_client

    # 首先尝试 pyweixin（微信 4.1+ 推荐）
    try:
        from pyweixin import Messages, Contacts
        logger.info("正在初始化 PyWeixin 客户端（微信 4.1+ 模式）...")
        wechat_client = PyWeixinClient()
        logger.info("✅ PyWeixin 客户端初始化成功（真实模式 - 微信 4.1+）")
        return True
    except ImportError as e:
        logger.debug(f"pyweixin 未找到: {e}")

    # 回退到 pywechat（旧版本）
    try:
        from pywechat import WeChat
        logger.info("正在初始化 PyWeChat 客户端（旧版本模式）...")
        wechat_client = WeChat()
        logger.info("✅ PyWeChat 客户端初始化成功（真实模式 - 旧版本）")
        return True
    except ImportError as e:
        logger.debug(f"pywechat 未找到: {e}")

    # 使用模拟模式
    logger.warning("未找到 pyweixin 或 pywechat，将使用模拟模式")
    logger.info("💡 提示: 如需真实微信功能，请在 Windows 侧运行 ./install_pywechat_manual.sh")
    wechat_client = MockWeChat()
    return True


class PyWeixinClient:
    """适配 pyweixin 的 API 包装器"""
    def __init__(self):
        # 延迟导入，确保只在初始化时检查
        from pyweixin import Messages, Contacts, Files, Monitor
        self.Messages = Messages
        self.Contacts = Contacts
        self.Files = Files
        self.Monitor = Monitor

    def send_text(self, to, message):
        """发送文本消息"""
        try:
            result = self.Messages.send_messages_to_friend(friend=to, messages=[message])
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return {"success": False, "error": str(e)}

    def send_image(self, to, file_path):
        """发送图片"""
        try:
            result = self.Files.send_images_to_friend(friend=to, images=[file_path])
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"发送图片失败: {e}")
            return {"success": False, "error": str(e)}

    def send_file(self, to, file_path):
        """发送文件"""
        try:
            result = self.Files.send_files_to_friend(friend=to, files=[file_path])
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"发送文件失败: {e}")
            return {"success": False, "error": str(e)}

    def get_contacts(self):
        """获取联系人列表"""
        try:
            # pyweixin 使用 get_friends_detail
            contacts = self.Contacts.get_friends_detail()
            # 转换为标准格式
            if isinstance(contacts, str):
                # 如果是 JSON 字符串，尝试解析
                import json
                contacts = json.loads(contacts)
            return contacts if contacts else []
        except Exception as e:
            logger.error(f"获取联系人失败: {e}")
            return []

    def get_group_chats(self):
        """获取群聊列表"""
        try:
            groups = self.Contacts.get_all_groups()
            return groups if groups else []
        except Exception as e:
            logger.error(f"获取群聊失败: {e}")
            return []

    def search_contact(self, keyword):
        """搜索联系人"""
        try:
            results = self.Contacts.search_contact(keyword)
            return results if results else []
        except Exception as e:
            logger.error(f"搜索联系人失败: {e}")
            return []


class MockWeChat:
    """模拟微信客户端（用于测试）"""
    def send_text(self, to, message):
        logger.info(f"[模拟] 发送消息给 {to}: {message}")
        return {"success": True, "type": "text", "to": to, "message": message}

    def send_image(self, to, file_path):
        logger.info(f"[模拟] 发送图片给 {to}: {file_path}")
        return {"success": True, "type": "image", "to": to, "file": file_path}

    def send_file(self, to, file_path):
        logger.info(f"[模拟] 发送文件给 {to}: {file_path}")
        return {"success": True, "type": "file", "to": to, "file": file_path}

    def get_contacts(self):
        return [
            {"name": "张三", "remark": "同事"},
            {"name": "李四", "remark": "朋友"},
            {"name": "王五", "remark": ""}
        ]

    def get_group_chats(self):
        return [
            {"name": "家庭群", "member_count": 5},
            {"name": "工作群", "member_count": 20}
        ]

    def search_contact(self, keyword):
        contacts = self.get_contacts()
        return [c for c in contacts if keyword.lower() in c["name"].lower()]

    def get_chat_history(self, chat_name, limit=50):
        return [
            {"from": chat_name, "content": "你好", "time": datetime.now().isoformat()}
        ]

    def send_group_at_msg(self, group_name, content, at_list=None):
        logger.info(f"[模拟] 发送群消息到 {group_name}: {content}, @: {at_list}")
        return {"success": True, "group": group_name, "message": content}


class APIHandler(BaseHTTPRequestHandler):
    """HTTP API 处理器"""

    def log_message(self, format, *args):
        logger.info(format % args)

    def _send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _read_json(self):
        """读取 JSON 请求体"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode('utf-8')
            return json.loads(body)
        return {}

    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        # 根路径 - 服务状态
        if path == '/':
            mode = "mock"
            if wechat_client and not isinstance(wechat_client, MockWeChat):
                mode = "real"
            self._send_json({
                "status": "running",
                "service": "PyWeChat Bridge",
                "wechat_connected": wechat_client is not None,
                "mode": mode,
                "timestamp": datetime.now().isoformat(),
                "note": "运行 ./install_pywechat_manual.sh 启用真实微信功能"
            })
            return

        # 获取联系人
        if path == '/contacts':
            try:
                contacts = wechat_client.get_contacts() if wechat_client else []
                self._send_json({
                    "success": True,
                    "message": "获取联系人成功",
                    "data": {"contacts": contacts}
                })
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 500)
            return

        # 获取群聊
        if path == '/groups':
            try:
                groups = wechat_client.get_group_chats() if wechat_client else []
                self._send_json({
                    "success": True,
                    "message": "获取群聊成功",
                    "data": {"groups": groups}
                })
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 500)
            return

        # 获取聊天记录
        if path.startswith('/messages/'):
            chat_name = path.split('/')[2]
            limit = int(query.get('limit', [50])[0])
            try:
                messages = wechat_client.get_chat_history(chat_name, limit) if wechat_client else []
                self._send_json({
                    "success": True,
                    "message": "获取聊天记录成功",
                    "data": {"messages": messages}
                })
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 500)
            return

        # 获取历史
        if path == '/history':
            limit = int(query.get('limit', [100])[0])
            self._send_json({
                "success": True,
                "message": "获取历史成功",
                "data": {"history": message_history[-limit:]}
            })
            return

        self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        """处理 POST 请求"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        try:
            data = self._read_json()
        except json.JSONDecodeError:
            self._send_json({"success": False, "message": "Invalid JSON"}, 400)
            return

        # 发送消息
        if path == '/send':
            try:
                to = data.get('to')
                message = data.get('message')
                msg_type = data.get('message_type', 'text')
                file_path = data.get('file_path')

                if not to or not message:
                    self._send_json({"success": False, "message": "Missing 'to' or 'message'"}, 400)
                    return

                if msg_type == 'text':
                    result = wechat_client.send_text(to, message) if wechat_client else {}
                elif msg_type == 'image':
                    result = wechat_client.send_image(to, file_path) if wechat_client else {}
                elif msg_type == 'file':
                    result = wechat_client.send_file(to, file_path) if wechat_client else {}
                else:
                    self._send_json({"success": False, "message": f"Unsupported type: {msg_type}"}, 400)
                    return

                # 记录历史
                message_history.append({
                    "direction": "out",
                    "to": to,
                    "content": message,
                    "type": msg_type,
                    "timestamp": datetime.now().isoformat()
                })

                self._send_json({
                    "success": True,
                    "message": "消息发送成功",
                    "data": {"result": result}
                })
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 500)
            return

        # 发送群消息
        if path == '/send_group':
            try:
                group_name = data.get('group_name')
                message = data.get('message')
                at_list = data.get('at_list')

                if not group_name or not message:
                    self._send_json({"success": False, "message": "Missing 'group_name' or 'message'"}, 400)
                    return

                if at_list:
                    result = wechat_client.send_group_at_msg(group_name, message, at_list) if wechat_client else {}
                else:
                    result = wechat_client.send_text(group_name, message) if wechat_client else {}

                self._send_json({
                    "success": True,
                    "message": "群消息发送成功",
                    "data": {"result": result}
                })
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 500)
            return

        # 搜索联系人
        if path == '/search':
            try:
                keyword = data.get('keyword')
                if not keyword:
                    self._send_json({"success": False, "message": "Missing 'keyword'"}, 400)
                    return

                results = wechat_client.search_contact(keyword) if wechat_client else []
                self._send_json({
                    "success": True,
                    "message": "搜索完成",
                    "data": {"results": results}
                })
            except Exception as e:
                self._send_json({"success": False, "message": str(e)}, 500)
            return

        # 初始化
        if path == '/init':
            if init_wechat():
                self._send_json({
                    "success": True,
                    "message": "微信客户端初始化成功"
                })
            else:
                self._send_json({"success": False, "message": "初始化失败"}, 503)
            return

        # 接收 webhook
        if path == '/receive':
            message_history.append({
                "direction": "in",
                "data": data,
                "timestamp": datetime.now().isoformat()
            })
            logger.info(f"收到消息: {data}")
            self._send_json({"status": "received"})
            return

        self._send_json({"error": "Not found"}, 404)


def run_server(host='127.0.0.1', port=8765, init=False):
    """运行 HTTP 服务器"""
    global BRIDGE_PORT
    BRIDGE_PORT = port

    if init:
        init_wechat()

    server = HTTPServer((host, port), APIHandler)
    logger.info(f"PyWeChat Bridge 服务启动: http://{host}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("服务停止")
        server.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PyWeChat Bridge")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8765, help="监听端口")
    parser.add_argument("--init", action="store_true", help="启动时初始化微信客户端")

    args = parser.parse_args()

    run_server(args.host, args.port, args.init)
