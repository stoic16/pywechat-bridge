#!/usr/bin/env python3
"""
Windows 运行入口。
说明：该进程依赖 pyweixin/pywechat，必须在 Windows 环境运行。
"""

import argparse

from pywechat_bridge_simple import run_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyWeChat Bridge (Windows Runtime)")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8765, help="监听端口")
    parser.add_argument("--init", action="store_true", help="启动时初始化微信客户端")
    args = parser.parse_args()
    run_server(args.host, args.port, args.init)
