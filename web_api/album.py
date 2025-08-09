from fastapi import APIRouter, HTTPException, UploadFile, Form, File
from pydantic import BaseModel, Field
from typing import List, Optional
from db.Do import we_library, Album, BaseReq, AlbumFolders
import os
import config
import shutil

import datetime
from web_api import file_util

router = APIRouter()

base_url = "/album"


# 文件列表
@router.post(f"{base_url}/list")
async def get_files(req: BaseReq):
    # 执行查询
    is_lock_folders = we_library.fetch_all(f"SELECT id FROM album_folders WHERE is_lock = 0", tuple([]))
    # 提取ID列表
    # folder_ids = [str(item['id']) for item in is_lock_folders]
    folder_ids = [item['id'] for item in is_lock_folders]

    # 基础查询
    base_query = "SELECT * FROM album"
    conditions = []
    params = []

    # 文件夹筛选
    if req.folder_id != -1:
        conditions.append("folder_id = ?")
        params.append(req.folder_id)

    # 文件类型筛选
    if req.file_type:  # 假设前端传入file_type参数
        conditions.append("filetype = ?")
        params.append(req.file_type)

    # 文件名关键词筛选
    if req.filename_keyword:  # 假设前端传入filename_keyword参数
        conditions.append("filename LIKE ?")
        params.append(f'%{req.filename_keyword}%')


    if req.is_lock:
        placeholders = ",".join(["?"] * len(folder_ids))
        conditions.append(f"folder_id IN ({placeholders})")
        params.extend(folder_ids)

    # 构建WHERE子句
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    # 添加排序
    base_query += " ORDER BY create_time DESC"

    # 获取总记录数
    count = we_library.fetch_count(base_query, tuple(params))

    # 执行查询
    files = we_library.fetch_all(base_query, tuple(params))

    # 分组数据
    grouped_files = {}
    for file in files:
        # 获取文件路径
        folder_id = file.get("folder_id")
        folder = we_library.fetch_one(f"SELECT * FROM album_folders WHERE id = {folder_id}")
        file["filepath"] = os.path.join(config.source_img_dir, folder.get('folder_name'), file.get("filename"))

        # 按创建时间分组（使用日期部分）
        create_date = file["create_time"].split()[0]  # 假设create_time是"YYYY-MM-DD HH:MM:SS"格式
        if create_date not in grouped_files:
            grouped_files[create_date] = []
        grouped_files[create_date].append(file)

    return {
        "success": True,
        "current": req.current,
        "size": req.size,
        "total": count,
        "model": grouped_files  # 返回分组后的数据
    }


# 移动文件至指定相册
@router.get(f"{base_url}/update_album")
async def update_album(ids: str, folder_id: int):
    id_list = ids.split(",")
    for id in id_list:
        # 查询文件
        one = we_library.fetch_one(
            "SELECT * FROM album WHERE id = ?;",
            (id,)
        )
        old_folder_id = one.get("folder_id")
        old_folder = we_library.fetch_one(f"SELECT * FROM album_folders WHERE id = {old_folder_id}")
        old_file_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, old_folder["folder_name"],
                                     one["filename"])

        new_folder = we_library.fetch_one(f"SELECT * FROM album_folders WHERE id = {folder_id}")
        new_file_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, new_folder["folder_name"],
                                     one["filename"])
        # 将文件移动至新相册
        # 移动文件
        shutil.move(old_file_path, new_file_path)

        # 更新数据库记录
        do_album = Album(
            table_name="album",  # 直接初始化字段值
            id=id,
            folder_id=folder_id
        )
        we_library.add_or_update(do_album, do_album.table_name)
    return {"success": True, "message": f"操作成功"}


# 删除文件
@router.get(f"{base_url}/del_album")
async def del_album(ids: str):
    id_list = ids.split(",")
    for id in id_list:
        # 查询文件
        one = we_library.fetch_one(
            "SELECT * FROM album WHERE id = ?;",
            (id,)
        )
        folder_id = one.get("folder_id")
        folder_one = we_library.fetch_one(f"SELECT * FROM album_folders WHERE id = {folder_id}")
        try:
            # 删除物理文件
            file_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, folder_one["folder_name"],
                                     one["filename"])
            os.remove(file_path)
        except Exception as e:
            print("Error:", e)
        # 删除数据库记录
        we_library.execute_query("DELETE FROM album WHERE id=?;", (id,))
    return {"success": True, "message": f"删除成功"}


# 查询相册列表
@router.get(f"{base_url}/folders")
async def get_folders(id: int, is_lock: int):
    if id == -1:
        # 如果传-1则查询全部
        folder_list = we_library.fetch_all(f"SELECT * FROM album_folders WHERE is_lock = {is_lock}")
        for folder in folder_list:
            folder_id = folder.get("id")
            album_count = we_library.fetch_all(f"SELECT count(*) FROM album where folder_id = {folder_id}")
            folder["file_count"] = album_count[0].get("count(*)")
        return folder_list
    else:
        one = we_library.fetch_one(f"SELECT * FROM album_folders WHERE id = {id}")
        return one


# 新增相册
@router.get(f"{base_url}/add_album_folders")
async def add_album_folders(album_name: str, ):
    # 创建目标文件夹
    target_folder = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, album_name)
    os.makedirs(target_folder, exist_ok=True)

    one = we_library.fetch_one(f"SELECT * FROM album_folders WHERE folder_name = ?;", (album_name,))
    if one is None:
        # 添加文件夹记录
        # 创建 AlbumFolders 实例
        do_folders = AlbumFolders(
            table_name="album_folders",  # 直接初始化字段值
            folder_name=album_name
        )
        we_library.add_or_update(do_folders, do_folders.table_name)
    return True


# 修改相册名称
@router.post(f"{base_url}/update_album_folder")
async def update_album_folder(req: BaseReq):
    # 查询相册
    one = we_library.fetch_one(
        "SELECT * FROM album_folders WHERE id = ?;",
        (req.id,)
    )
    # 重命名物理文件夹
    old_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, one["folder_name"])
    new_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, req.new_name)
    os.rename(old_path, new_path)

    # 更新数据库记录
    do_folders = AlbumFolders(
        table_name="album_folders",  # 直接初始化字段值
        id=req.id,
        folder_name=req.new_name
    )
    we_library.add_or_update(do_folders, do_folders.table_name)
    return {"status": "success", "message": f"修改成功"}


# 锁定相册
@router.get(f"{base_url}/lock_album")
async def lock_album(id: int):
    do_folders = AlbumFolders(
        table_name="album_folders",  # 直接初始化字段值
        id=id,
        is_lock=1
    )
    we_library.add_or_update(do_folders, do_folders.table_name)
    return True


# 解锁相册
@router.get(f"{base_url}/unlock_album")
async def lock_album(id: int):
    do_folders = AlbumFolders(
        table_name="album_folders",  # 直接初始化字段值
        id=id,
        is_lock=0
    )
    we_library.add_or_update(do_folders, do_folders.table_name)
    return True


# 设置锁定密码
@router.get(f"{base_url}/set_lock_password")
async def set_lock_password(password: str):
    file_util.update_value("lock_password", password)
    return True


# 删除相册
@router.get(f"{base_url}/del_album_folder")
async def delete_album_folder(id: int):
    # 查询相册
    one = we_library.fetch_one(
        "SELECT * FROM album_folders WHERE id = ?;",
        (id,)
    )
    # 删除物理文件夹
    folder_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, one["folder_name"])
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # 递归删除整个文件夹
    # 删除文件记录
    we_library.execute_query("DELETE FROM album WHERE folder_id=?;", (id,))
    # 删除相册记录
    we_library.execute_query("DELETE FROM album_folders WHERE id=?;", (id,))
    return {"status": "success", "message": f"已删除"}


# 判断是否未设置密码
@router.get(f"{base_url}/is_lock_password")
async def is_lock_password():
    if file_util.load_config().get("lock_password") is None:
        return True
    return False


# 设置锁定密码
@router.get(f"{base_url}/set_lock_password")
async def set_lock_password(password: str):
    file_util.update_value("lock_password", password)
    return True


# 重置锁定密码
@router.get(f"{base_url}/reset_lock_password")
async def reset_lock_password(old_password: str, new_password: str):
    if file_util.load_config().get("lock_password") != old_password:
        return False
    file_util.update_value("lock_password", new_password)
    return True


# 访问相册
@router.get(f"{base_url}/unlock")
async def unlock(password: str):
    if file_util.load_config().get("lock_password") == password:
        return True
    return False


# 上传文件
@router.post(f"{base_url}/upload_file")
async def upload_file(file_stream: UploadFile = File(...),
                      folder_id: int = Form(...),
                      folder_name: str = Form(...),
                      file_name: str = Form(...)):
    # 查询相册是否存在
    if folder_id == -1:
        folder_one = we_library.fetch_one(
            "SELECT * FROM album_folders WHERE folder_name = ?;",
            (folder_name,))
        if folder_one is None:
            access_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, folder_name, file_name)
            os.makedirs(access_path, exist_ok=True)
            do_album_folders = AlbumFolders(
                table_name="album_folders",
                folder_name=folder_name
            )
            folder_id = we_library.add_or_update(do_album_folders, do_album_folders.table_name)
        if folder_one is not None:
            folder_id = folder_one["id"]

    else:
        folder_one = we_library.fetch_one(
            "SELECT * FROM album_folders WHERE id = ?;",
            (folder_id,)
        )
        folder_name = folder_one["folder_name"]
    access_path = os.path.join(config.ROOT_DIR_WIN, config.source_img_dir, folder_name, file_name)
    access_path = os.path.normpath(access_path)  # 修复斜杠问题
    # 分块写入文件（适合大文件）
    with open(access_path, "wb") as buffer:
        while content := await file_stream.read(1024 * 1024):  # 每次读取1MB
            buffer.write(content)
    # 支持的媒体文件扩展名
    media_extensions = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
        'audio': ['.mp3', '.wav', '.ogg', '.flac']
    }
    if not os.path.isfile(access_path):
        return False
        # 检查文件类型
    _, ext = os.path.splitext(file_name.lower())
    filetype = None
    for type_name, exts in media_extensions.items():
        if ext in exts:
            filetype = type_name
            break
    if not filetype:
        return False
    # 初始化GPS变量
    longitude, latitude = None, None
    # 仅当图片文件时尝试提取GPS
    if filetype == 'image':
        longitude, latitude = file_util.get_lat_lon(access_path)
    # 获取文件信息
    file_stat = os.stat(access_path)
    file_create_time = datetime.datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
    # 插入数据库记录
    do_files = Album(
        table_name="album",  # 直接初始化字段值
        folder_id=folder_id,
        filename=file_name,
        filepath=str(access_path),
        filesize=file_stat.st_size,
        filetype=filetype,
        longitude=longitude,
        latitude=latitude,
        file_create_time=file_create_time,
    )
    we_library.add_or_update(do_files, do_files.table_name)
    return {
        "success": True,
    }


# Pydantic模型
class MapLocation(BaseModel):
    longitude: float
    latitude: float
    count: int


# 获取地图标记数据
@router.get(f"{base_url}/map/locations", response_model=List[MapLocation])
def get_map_locations():
    try:
        # 构建查询SQL
        query = """
                SELECT ROUND(longitude, 4) AS longitude, \
                       ROUND(latitude, 4)  AS latitude, \
                       COUNT(id) AS count
                FROM album
                WHERE
                    del_flag = 0
                  AND longitude IS NOT NULL
                  AND latitude IS NOT NULL
                GROUP BY ROUND(longitude, 4), ROUND(latitude, 4) \
                """

        # 执行查询
        results = we_library.fetch_all(query)
        city_name = "杭州"
        # 转换结果格式
        locations = []
        for row in results:
            locations.append({
                "longitude": row["longitude"],
                "latitude": row["latitude"],
                "count": row["count"],
                "city": city_name  # 添加城市名字段
            })

        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 获取特定位置的图片
@router.get(f"{base_url}/map/location/photos")
def get_location_photos(longitude: float, latitude: float):
    try:
        # 构建查询SQL
        query = """
                SELECT *
                FROM album
                WHERE del_flag = 0
                  AND ROUND(longitude, 4) = ROUND(?, 4)
                  AND ROUND(latitude, 4) = ROUND(?, 4) \
                """

        # 执行查询
        params = [longitude, latitude]
        photos = we_library.fetch_all(query, params)

        # 转换日期格式为ISO格式
        for photo in photos:
            if "create_time" in photo and photo["create_time"]:
                photo["create_time"] = datetime.datetime.strptime(photo["create_time"], "%Y-%m-%d %H:%M:%S").isoformat()
            if "file_create_time" in photo and photo["file_create_time"]:
                photo["file_create_time"] = datetime.datetime.strptime(photo["file_create_time"],
                                                                       "%Y-%m-%d %H:%M:%S").isoformat()
        for file in photos:
            folder_id = file.get("folder_id")
            folder = we_library.fetch_one(f"SELECT * FROM album_folders WHERE id = {folder_id}")
            file["filepath"] = os.path.join(config.source_img_dir, folder.get('folder_name'), file.get("filename"))
        return photos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
