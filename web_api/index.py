from fastapi import APIRouter, status, HTTPException
from Do import BaseReq, we_library
from cachetools import TTLCache
import requests

router = APIRouter()


# 验证用户登录密码
def authenticate_user(mobile: str, password: str):
    # 这里应该有数据库查询逻辑
    return True  # 假设验证成功


# 创建一个最大大小为 100，超过 60 秒失效的缓存
cache = TTLCache(maxsize=100, ttl=60 * 60)


@router.post("/login")
async def login(req: BaseReq):
    if authenticate_user(req.mobile, req.password):
        # 生成token
        token = "generated_token_" + req.mobile
        # 将token存入缓存
        cache[token] = req.mobile
        return token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_bing_wallpaper():
    url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    try:
        response = requests.get(url)
        data = response.json()
        image_url = "https://www.bing.com" + data["images"][0]["url"]
        return image_url
    except Exception as e:
        print("Error:", e)
        return None


if __name__ == "__main__":
    wallpaper_url = get_bing_wallpaper()
    if wallpaper_url:
        print("今日必应壁纸:", wallpaper_url)
    else:
        print("获取失败！")


# 获取随机一张图片及素材
@router.post(f"/index/getRandomImg")
async def get_random_img():
    one_haven = get_bing_wallpaper()
    # one_haven = we_library.fetch_one(f"SELECT * FROM wall_haven where del_flag = 0 ORDER BY RANDOM() LIMIT 1;")
    one_material = we_library.fetch_one(f"SELECT * FROM material ORDER BY RANDOM() LIMIT 1;")
    # todo 判断是否收藏

    return {
        # "id": one_haven.get("id"),
        # "imgUrl": one_haven.get("img_url"),
        "imgUrl": one_haven,
        "contentId": one_material.get("id"),
        "content": one_material.get("content"),
        "source": one_material.get("source"),
        "author": one_material.get("author"),
        # "createTime": one_haven.get("create_time"),
        # "isEnshrine": one_material.get(""), # 是否收藏 0: 否 1：是
    }

# # 分页查询
# @app.post("/list")
# def page(req: BaseReq):
#     return we_library.page(req, req.table_name)
#
#
# # 根据id查询
# @app.get("/info")
# def get_info(table_name: str, id: int):
#     return we_library.fetch_one(f"SELECT * FROM {table_name} WHERE id=?;", (id,))
#
#
# # 根据id删除
# @app.get("/del")
# def del_data(table_name: str, id: int):
#     delete_data_query = f"DELETE FROM {table_name} WHERE id=?;"
#     we_library.execute_query(delete_data_query, (id,))
#     return True
