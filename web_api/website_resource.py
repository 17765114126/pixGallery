from fastapi import APIRouter
from Do import BaseReq, we_library, WebsiteResource

router = APIRouter()

base_url = "/resource"


# 分页查询
@router.post(f"{base_url}/list")
def page(req: BaseReq):
    base_query = f"SELECT * FROM website_resource"
    params = []

    # 添加筛选条件
    where_clauses = []
    for field, value in req.dict().items():
        if value is not None and field not in ['table_name', 'page', 'page_size']:
            where_clauses.append(f"{field} LIKE ?")
            params.append(f"%{value}%")

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

    # 获取总记录数
    count = we_library.fetch_count(base_query, tuple(params))

    # 添加分页
    if req.page_size != -1:
        base_query += " LIMIT ? OFFSET ?"
        params.extend([req.page_size, (req.page - 1) * req.page_size])

    return {
        "page": req.page,
        "page_size": req.page_size,
        "count": count,
        "data": we_library.fetch_all(base_query, tuple(params))
    }


# 根据id查询
@router.get(f"{base_url}/info")
def get_info(table_name: str, id: int):
    return we_library.fetch_one(f"SELECT * FROM {table_name} WHERE id=?;", (id,))


# 根据id删除
@router.get(f"{base_url}/del")
def del_data(table_name: str, id: int):
    delete_data_query = f"DELETE FROM {table_name} WHERE id=?;"
    we_library.execute_query(delete_data_query, (id,))
    return True


# content表添加或修改
@router.post(f"{base_url}/add")
def add_or_update_content(do: WebsiteResource):
    we_library.add_or_update(do, do.table_name)
    return True
