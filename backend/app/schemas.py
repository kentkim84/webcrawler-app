from pydantic import BaseModel
from datetime import datetime

class ScrapedDataBase(BaseModel):
    url: str
    title: str
    content: str

class ScrapedDataCreate(ScrapedDataBase):
    pass

class ScrapedData(ScrapedDataBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True