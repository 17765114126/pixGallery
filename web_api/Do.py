from typing import Optional
from pydantic import BaseModel, Field
from db import SQLiteDB
import os

we_library = SQLiteDB.SQLiteDB(os.path.join('db', 'we_library.db'))


class BaseReq(BaseModel):
    table_name: str = "contents"
    current: int = Field(default=1, ge=1)  # 默认值为1，且必须大于等于1
    size: int = Field(default=10, ge=-1)  # 默认值为10，允许-1表示不分页

    class Config:
        extra = 'allow'  # 允许额外的字段


class User(BaseModel):
    table_name: str = "user"
    id: Optional[int] = None
    username: Optional[str] = ''
    password: Optional[str] = ''
    mobile: Optional[str] = ''
    realname: Optional[str] = ''
    mailbox: Optional[str] = ''
    head_img: Optional[str] = ''
    background: Optional[str] = ''
    signature: Optional[str] = ''
    status: Optional[bool] = 1
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class Comment(BaseModel):
    table_name: str = "comment"
    id: Optional[int] = None
    cid: Optional[int] = None
    author_id: Optional[int] = None
    ip: Optional[str] = None
    content: Optional[str] = None
    type: Optional[bool] = 0
    status: Optional[bool] = 0
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class Contents(BaseModel):
    table_name: str = "contents"
    id: Optional[int] = None
    title: Optional[str] = None
    thumb_img: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    type: Optional[bool] = 1
    status: Optional[bool] = 0
    tags_id: Optional[str] = ''
    categorie_id: Optional[int] = None
    hits: Optional[int] = 0
    sort: Optional[int] = 0
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class Material(BaseModel):
    table_name: str = "material"
    id: Optional[int] = None
    thumb_img: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None
    type: Optional[bool] = 1
    status: Optional[bool] = 0
    source: Optional[str] = ''
    author: Optional[str] = '佚名'
    original: Optional[bool] = 0
    metas_id: Optional[int] = None
    hits: Optional[int] = 0
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class Metas(BaseModel):
    table_name: str = "metas"
    id: Optional[int] = None
    name: Optional[str] = ''
    type: Optional[int] = 0
    sort: Optional[int] = 0
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class Tag(BaseModel):
    table_name: str = "tag"
    id: Optional[int] = None
    name: Optional[str] = ''
    sort: Optional[int] = 0
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class WallHaven(BaseModel):
    table_name: str = "wall_haven"
    id: Optional[int] = None
    img_url: Optional[str] = ''
    source: Optional[int] = 0
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class WebsiteResource(BaseModel):
    table_name: str = "website_resource"
    id: Optional[int] = None
    website_title_id: Optional[int] = None
    name: Optional[str] = ''
    website_url: Optional[str] = ''
    state: Optional[str] = ''
    icon: Optional[str] = ''
    sort: Optional[int] = 1
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0


class WebsiteTitle(BaseModel):
    table_name: str = "website_title"
    id: Optional[int] = None
    title: Optional[str] = ''
    sort: Optional[int] = 1
    # create_time: Optional[str] = CURRENT_TIMESTAMP
    # del_flag: Optional[bool] = 0
