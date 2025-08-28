from pydantic import BaseModel

class CrawlCreate(BaseModel):
    target_url: str
    depth: int = 1

class CrawlStatus(BaseModel):
    status: str