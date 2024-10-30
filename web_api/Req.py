from pydantic import BaseModel
from typing import Optional


class ContentReq(BaseModel):
    table_name: str = "contents"
    page: int = 1
    page_size: int = 10
    title: Optional[str] = None
