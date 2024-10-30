from pydantic import BaseModel, Field


class BaseReq(BaseModel):
    table_name: str = "contents"
    page: int = Field(default=1, ge=1)  # 默认值为1，且必须大于等于1
    page_size: int = Field(default=10, ge=-1)  # 默认值为10，允许-1表示不分页

    class Config:
        extra = 'allow'  # 允许额外的字段
