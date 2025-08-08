from fastapi import APIRouter
from db.Do import BaseReq, we_library, Material

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
        "code": 0,
        "current": req.current,
        "size": req.size,
        "total": count,
        # "pages": count/req.size,
        "model": we_library.fetch_all(base_query, tuple(params))
    }


# 保存
@router.post(f"{base_url}/save")
async def save(do: Material):
    one = we_library.fetch_one(f"SELECT * FROM material WHERE content = ?;", (do.content,))
    if one and one['content'] is not None:
        return {
            "code": 1,
            "msg": '句子已存在'
        }
    we_library.add_or_update(do, do.table_name)
    return {
        "code": 0,
        "msg": '发布成功'
    }


# 根据id查询
@router.get(f"{base_url}/info")
def get_info(id: int):
    return we_library.fetch_one(f"SELECT * FROM material WHERE id=?;", (id,))
