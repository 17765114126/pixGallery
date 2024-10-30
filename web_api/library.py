from fastapi import FastAPI, HTTPException
import uvicorn
from db import SQLiteDB
import os
from Req import ContentReq
from Do import Content

app = FastAPI()
db_path = os.path.join('..', 'db', 'we_library.db')
we_library = SQLiteDB.SQLiteDB(db_path)


# 分页查询content表
@app.post("/content/list")
def page_content(req: ContentReq):
    return we_library.page(req, req.table_name)


# 根据id查询content表
@app.get("/content/info_")
def get_info_content(id: int):
    return we_library.fetch_one("SELECT * FROM contents WHERE id=?;", (id,))


# content表添加或修改
@app.post("/content/add_or_update")
def add_or_update_content(do: Content):
    we_library.add_or_update(do, do.table_name)
    return True


# id删除数据
@app.get("/content/del")
def del_content(id: int):
    delete_data_query = "DELETE FROM contents WHERE id=?;"
    we_library.execute_query(delete_data_query, (id,))
    return True


# 启动命令（必须在主类目录下）：uvicorn library:app --reload
# 访问地址：http://127.0.0.1:7789
# 自动动生成交互式 API 文档，访问地址： http://127.0.0.1:7789/docs
if __name__ == '__main__':
    uvicorn.run(app='library:app', host="127.0.0.1", port=7789, reload=True)
