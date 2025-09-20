from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database
import crochet
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.signals import item_scraped
from scraper.scraper.spiders.basic_spider import BasicSpider
import logging
import threading
from urllib.parse import urlparse
from pydantic import HttpUrl, BaseModel
from scrapy.utils.reactor import install_reactor
from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

crochet.setup()
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ScrapeRequest(BaseModel):
    url: HttpUrl

# Shared list for collecting items
global_results = []

def handle_item_scraped(item, response, spider):
    logger.info(f"Item scraped: {dict(item)}")
    global_results.append(dict(item))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/scrape/", response_model=schemas.ScrapedData)
async def scrape_url(request: ScrapeRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    url_str = str(request.url)
    logger.info(f"Starting scrape for URL: {url_str}")
    parsed_url = urlparse(url_str)
    if not parsed_url.scheme or not parsed_url.netloc:
        raise HTTPException(status_code=400, detail="Invalid URL format")

    global_results.clear()
    
    settings = get_project_settings()
    settings.set('REQUEST_FINGERPRINTER_IMPLEMENTATION', '2.7')
    settings.set('USER_AGENT', 'Mozilla/5.0 (compatible; ScraperBot/1.0)')
    settings.set('DOWNLOAD_TIMEOUT', 10)

    runner = CrawlerRunner(settings)
    crawler = runner.create_crawler(BasicSpider)
    crawler.signals.connect(handle_item_scraped, signal=item_scraped)
    
    try:
        deferred = runner.crawl(crawler, start_url=url_str)
        wait_for_crawl = crochet.run_in_reactor(lambda: deferred)
        wait_for_crawl().wait(timeout=30)
    except crochet.TimeoutError:
        raise HTTPException(status_code=500, detail="Scraping timed out after 30 seconds")
    except Exception as e:
        logger.error(f"Crawl failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    if not global_results:
        raise HTTPException(status_code=500, detail="No data scraped from the URL")

    item = global_results[0]
    if item.get('title') == "Error":
        raise HTTPException(status_code=500, detail=f"Scraping failed: {item['content']}")

    db_item = models.ScrapedData(url=url_str, title=item["title"], content=item["content"], user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@app.get("/scrapes/", response_model=List[schemas.ScrapedData])
def get_scrapes(search: str = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.ScrapedData).filter(models.ScrapedData.user_id == current_user.id)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (models.ScrapedData.title.ilike(search_term)) |
            (models.ScrapedData.content.ilike(search_term)) |
            (models.ScrapedData.url.ilike(search_term))
        )
    return query.all()

@app.get("/users/", response_model=List[schemas.User])
def get_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(models.User).all()

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    return {"status": "ok"}