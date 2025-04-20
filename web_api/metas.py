from fastapi import APIRouter
from web_api.Do import BaseReq, we_library

router = APIRouter()

base_url = "/metas"


# 列表查询
@router.post(f"{base_url}/list")
async def get_list():
    return {
        "data": we_library.fetch_all("SELECT * FROM metas order by sort ASC")
    }
