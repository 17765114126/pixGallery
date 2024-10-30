from fastapi import FastAPI
import uvicorn
from db import SQLiteDB
import os
from Req import BaseReq
from Do import Content

app = FastAPI()

we_library = SQLiteDB.SQLiteDB(os.path.join('..', 'db', 'we_library.db'))


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


# content表添加或修改
@app.post("/content/add_or_update")
def add_or_update_content(do: Content):
    we_library.add_or_update(do, do.table_name)
    return True


# 启动命令（必须在主类目录下）：uvicorn library:app --reload
# 访问地址：http://127.0.0.1:7789
# 自动动生成交互式 API 文档，访问地址： http://127.0.0.1:7789/docs
if __name__ == '__main__':
    uvicorn.run(app='library:app', host="127.0.0.1", port=7789, reload=True)
