from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime

class ScrapedData(Base):
    __tablename__ = "scraped_data"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)