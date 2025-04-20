import multiprocessing
import run_api
import run_web

if __name__ == "__main__":
    # 创建两个进程
    api_process = multiprocessing.Process(target=run_api.run)
    web_process = multiprocessing.Process(target=run_web.run)

    # 启动进程
    api_process.start()
    web_process.start()

    # 保持主进程运行
    try:
        api_process.join()
        web_process.join()
    except KeyboardInterrupt:
        api_process.terminate()
        web_process.terminate()
