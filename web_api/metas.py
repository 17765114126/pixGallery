from fastapi import APIRouter
from web_api.Do import BaseReq, we_library, Metas

router = APIRouter()

base_url = "/metas"


# 列表查询
@router.post(f"{base_url}/list")
async def get_list():
    return {
        "code": 0,
        "model": we_library.fetch_all("SELECT * FROM metas order by sort ASC")
    }


# 保存
@router.post(f"{base_url}/save")
async def save(do: Metas):
    we_library.add_or_update(do, do.table_name)
    return True
