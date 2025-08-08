from fastapi import APIRouter
from db.Do import we_library, WebsiteResource

router = APIRouter()

base_url = "/resource"


# 列表查询
@router.post(f"{base_url}/list")
async def get_list():
    title_list = we_library.fetch_all("SELECT * FROM website_title where del_flag = 0 order by sort asc;")
    for title in title_list:
        resource_list = we_library.fetch_all(
            f"SELECT * FROM website_resource where del_flag = 0 and website_title_id = {title.get('id')};")
        title['resources'] = resource_list
    return {
        "data": title_list
    }


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
