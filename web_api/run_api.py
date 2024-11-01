from fastapi import FastAPI
import uvicorn
from Do import BaseReq, we_library
from website_resource import router as resource_router

app = FastAPI()

app.include_router(resource_router)


# 分页查询
@app.post("/list")
def page(req: BaseReq):
    return we_library.page(req, req.table_name)


# 根据id查询
@app.get("/info")
def get_info(table_name: str, id: int):
    return we_library.fetch_one(f"SELECT * FROM {table_name} WHERE id=?;", (id,))


# 根据id删除
@app.get("/del")
def del_data(table_name: str, id: int):
    delete_data_query = f"DELETE FROM {table_name} WHERE id=?;"
    we_library.execute_query(delete_data_query, (id,))
    return True


# 使用 Python 3 提供静态文件服务命令（在dist根目录运行）: python -m http.server 8688

# 启动命令（必须在主类目录下）：uvicorn run_api:app --reload
# 访问地址：http://127.0.0.1:8686
# 自动动生成交互式 API 文档，访问地址： http://127.0.0.1:8686/docs
if __name__ == '__main__':
    uvicorn.run(app='run_api:app', host="127.0.0.1", port=8686, reload=True)
