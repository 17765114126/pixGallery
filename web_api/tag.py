from fastapi import APIRouter
from db.Do import we_library

router = APIRouter()

base_url = "/tag"


# 列表查询
@router.post(f"{base_url}/list")
async def get_list():
    return {
        "code": 0,
        "model": we_library.fetch_all("SELECT * FROM tag order by sort ASC")
    }
