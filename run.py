import multiprocessing
from multiprocessing import freeze_support  # 新增导入
import run_api
import run_web
import webbrowser
import socket
import time


def is_port_ready(port: int, timeout=30) -> bool:
    """检测端口是否就绪"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    return True
        except:
            pass
        time.sleep(0.2)
    return False


# pip install pyinstaller
# pyinstaller -F -i icon.ico run.py
# pyinstaller -F -i icon.ico --paths "D:\develop\project\reptile_project\excel_tool" run.py

if __name__ == "__main__":
    freeze_support()
    # 创建两个进程
    api_process = multiprocessing.Process(target=run_api.run)
    web_process = multiprocessing.Process(target=run_web.run)

    # 启动进程
    api_process.start()
    web_process.start()
    # 等待端口就绪
    if is_port_ready(8688):
        # 打开默认浏览器
        webbrowser.open("http://localhost:8688")
    else:
        print("⚠️ 服务启动失败，请手动访问 http://localhost:8688")
    # 保持主进程运行
    try:
        api_process.join()
        web_process.join()
    except KeyboardInterrupt:
        api_process.terminate()
        web_process.terminate()
