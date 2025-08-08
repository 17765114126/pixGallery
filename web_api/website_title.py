from fastapi import APIRouter
from db.Do import we_library, WebsiteTitle

router = APIRouter()

base_url = "/website_title"

# 列表查询
@router.post(f"{base_url}/list")
async def get_list():
    return {
        "code": 0,
        "model": we_library.fetch_all("SELECT * FROM website_title order by sort ASC")
    }


# 保存
@router.post(f"{base_url}/save")
async def save(do: WebsiteTitle):
    we_library.add_or_update(do, do.table_name)
    return True


# 根据id删除
@router.get(f"{base_url}/del")
def del_data(id: int):
    delete_data_query = f"DELETE FROM website_title WHERE id=?;"
    we_library.execute_query(delete_data_query, (id,))
    return True