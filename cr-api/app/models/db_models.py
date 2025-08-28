from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
import datetime

Base = declarative_base()

class Crawl(Base):
    __tablename__ = "crawls"
    crawl_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_url = Column(Text, nullable=False)
    status = Column(String, default="pending")
    start_time = Column(DateTime, default=datetime.datetime.utcnow)