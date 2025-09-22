from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: str

    class Config:
        from_attributes = True

class ScrapedDataBase(BaseModel):
    url: str
    title: str
    content: str

class ScrapedData(ScrapedDataBase):
    id: int
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True

class Log(BaseModel):
    id: int
    level: str
    message: str
    timestamp: datetime
    user_id: Optional[int]

    class Config:
        from_attributes = True