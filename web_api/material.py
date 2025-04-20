from fastapi import APIRouter
from web_api.Do import BaseReq, we_library

router = APIRouter()

base_url = "/material"


# 列表查询
@router.post(f"{base_url}/list")
async def page(req: BaseReq):
    base_query = f"SELECT * FROM material"
    params = []

    # 添加筛选条件
    # where_clauses = []
    # for field, value in req.dict().items():
    #     if value is not None and field not in ['table_name', 'page', 'page_size']:
    #         where_clauses.append(f"{field} LIKE ?")
    #         params.append(f"%{value}%")
    #
    #     if where_clauses:
    #         base_query += " WHERE " + " AND ".join(where_clauses)

    # 获取总记录数
    count = we_library.fetch_count(base_query, tuple(params))

    # 添加分页
    if req.size != -1:
        base_query += " LIMIT ? OFFSET ?"
        params.extend([req.size, (req.current - 1) * req.size])

    return {
        "current": req.current,
        "size": req.size,
        "total": count,
        # "pages": count/req.size,
        "data": we_library.fetch_all(base_query, tuple(params))
    }


# 根据id查询
@router.get(f"{base_url}/info")
def get_info(id: int):
    return we_library.fetch_one(f"SELECT * FROM material WHERE id=?;", (id,))
