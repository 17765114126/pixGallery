from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import config,log_config
from db import init_database

from web_api.website_resource import router as resource_router
from web_api.index import router as index_router, cache
from web_api.material import router as material_router
from web_api.metas import router as metas_router
from web_api.tag import router as tag_router
from web_api.website_title import router as website_title_router
from web_api.album import router as album_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(resource_router)
app.include_router(index_router)
app.include_router(material_router)
app.include_router(metas_router)
app.include_router(tag_router)
app.include_router(album_router)
app.include_router(website_title_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

# 白名单列表
WHITELIST = ["/login"]


# # 拦截所有接口判断用户是否登录
# @app.middleware("http")
# async def add_process(request: Request, call_next):
#     # 处理预检请求
#     if request.method == "OPTIONS":
#         response = Response(status_code=200)
#         response.headers["Access-Control-Allow-Origin"] = "*"
#         response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#         response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
#         return response
#     # 检查请求路径是否在白名单中
#     if request.url.path in WHITELIST:
#         return await call_next(request)
#
#     token = request.headers.get("Authorization")
#     if token:
#         # 从缓存中获取数据
#         mobile = cache.get(token)
#         if mobile:
#             return await call_next(request)
#     raise HTTPException(status_code=401, detail="Invalid token")


# 使用 Python 3 提供静态文件服务命令（在dist根目录运行）: python -m http.server 8688

# 启动命令（必须在主类目录下）：uvicorn run_api:app --reload
# 访问地址：http://127.0.0.1:8686
# 自动动生成交互式 API 文档，访问地址： http://127.0.0.1:8686/docs

def run():
    # 开启日志配置
    log_config.log_run()
    logging.info('------主程序开始运行-------')
    init_database.init_database()
    uvicorn.run(app='run_api:app',
                host="127.0.0.1",
                port=config.api_host,
                reload=True,
                log_config=None)


if __name__ == '__main__':
    run()
