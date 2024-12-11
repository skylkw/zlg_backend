import random
import socket
import threading

import webview
from main import app
import uvicorn


def get_unused_port():
    """获取未被使用的端口"""
    while True:
        port = random.randint(1024, 65535)  # 端口范围一般为1024-65535
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("localhost", port))
            sock.close()
            return port
        except OSError:
            pass


port = get_unused_port()

# 启动FastAPI服务
t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": port})
t.daemon = True
t.start()

# 在PyWebview应用程序中加载FastAPI应用程序的URL
webview.create_window(
    "株齿电机控制上位机",
    f"http://localhost:{port}",
    width=1024,  # 初始窗口宽度（像素）
    height=768,  # 初始窗口高度（像素）
    resizable=True,  # 是否允许调整窗口大小
    fullscreen=False,  # 是否全屏显示
    min_size=(800, 600),  # 最小窗口大小
)
webview.start()
