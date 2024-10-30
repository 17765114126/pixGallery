from pydantic import BaseModel
from typing import Optional


class Content(BaseModel):
    table_name: str = "contents"
    id: Optional[int] = None
    title: Optional[str] = None
    thumb_img: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    type: Optional[int] = None
    status: Optional[int] = None
    tags_id: Optional[int] = None
    categorie_id: Optional[int] = None
    hits: Optional[int] = None
    sort: Optional[int] = None
    # create_time: Optional[int] = None
    # del_flag: Optional[int] = None
