import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()
# 挂载静态文件（自动处理 index.html）
app.mount("/", StaticFiles(directory="dist", html=True), name="static")


# 兜底路由处理前端 history 模式
@app.exception_handler(404)
async def custom_404_handler(request, exc: HTTPException):
    index_path = Path("dist") / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(index_path)


def run():
    uvicorn.run(
        "run_web:app",  # 使用字符串形式
        host="127.0.0.1",
        port=8688,
        access_log=False
    )


if __name__ == "__main__":
    run()
