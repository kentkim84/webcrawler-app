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
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
import json
from urllib.parse import urlparse
from pydantic import HttpUrl, BaseModel
from scrapy.utils.reactor import install_reactor
from passlib.context import CryptContext
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
import os
import psutil
from fastapi_websocket_pubsub import PubSubEndpoint

# Configure logging
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s %(module)s %(lineno)s'
)
file_handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=5)
file_handler.setFormatter(formatter)

class PubSubHandler(logging.Handler):
    def __init__(self, endpoint):
        super().__init__()
        self.endpoint = endpoint
        self.setFormatter(formatter)

    def emit(self, record):
        try:
            log_json_str = self.format(record)
            log_dict = json.loads(log_json_str)
            self.endpoint.publish(["logs"], log_dict)
        except Exception:
            pass

class DBHandler(logging.Handler):
    def emit(self, record):
        try:
            db = database.SessionLocal()
            if isinstance(record.msg, dict):
                user_id = record.msg.get('user_id', None)
                message = record.msg.get('msg', json.dumps(record.msg))
            else:
                user_id = None
                message = record.msg
            log = models.Log(
                level=record.levelname,
                message=message,
                user_id=user_id
            )
            db.add(log)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()

# Initialize FastAPI app and WebSocket endpoint
app = FastAPI()
endpoint = PubSubEndpoint()
app.mount("/pubsub", endpoint)

crochet.setup()
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

# Setup logging
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(PubSubHandler(endpoint))
root_logger.addHandler(DBHandler())

logger = logging.getLogger(__name__)

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
    logger.info({"msg": f"Item scraped: {dict(item)}"})
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
            logger.error({"msg": "Invalid token: no username in payload"})
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError as e:
        logger.error({"msg": f"Token decode failed: {str(e)}"})
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        logger.error({"msg": f"User not found: {username}"})
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        logger.warning({"msg": f"Registration attempt with existing username: {user.username}"})
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info({"msg": f"User registered: {user.username}"})
    return new_user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.error({"msg": f"Login failed for username: {form_data.username}"})
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
    logger.info({"msg": f"User logged in: {form_data.username}"})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/scrape/", response_model=schemas.ScrapedData)
async def scrape_url(request: ScrapeRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    url_str = str(request.url)
    logger.info({"msg": f"Starting scrape for URL: {url_str}", "user_id": current_user.id})
    parsed_url = urlparse(url_str)
    if not parsed_url.scheme or not parsed_url.netloc:
        logger.error({"msg": f"Invalid URL format: {url_str}", "user_id": current_user.id})
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
        logger.error({"msg": "Scraping timed out after 30 seconds", "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="Scraping timed out after 30 seconds")
    except Exception as e:
        logger.error({"msg": f"Crawl failed: {str(e)}", "user_id": current_user.id})
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    if not global_results:
        logger.error({"msg": "No data scraped from the URL", "user_id": current_user.id})
        raise HTTPException(status_code=500, detail="No data scraped from the URL")

    item = global_results[0]
    if item.get('title') == "Error":
        logger.error({"msg": f"Scraping failed: {item['content']}", "user_id": current_user.id})
        raise HTTPException(status_code=500, detail=f"Scraping failed: {item['content']}")

    db_item = models.ScrapedData(url=url_str, title=item["title"], content=item["content"], user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info({"msg": f"Scraped data saved: {url_str}", "user_id": current_user.id})

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
    logger.info({"msg": f"Fetching scrapes for user: {current_user.id}", "user_id": current_user.id})
    return query.all()

@app.get("/users/", response_model=List[schemas.User])
def get_users(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        logger.warning({"msg": f"Unauthorized access to users endpoint by user: {current_user.id}", "user_id": current_user.id})
        raise HTTPException(status_code=403, detail="Not authorized")
    logger.info({"msg": "Fetching all users", "user_id": current_user.id})
    return db.query(models.User).all()

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        logger.info({"msg": f"Health check: CPU={cpu}%, Memory={mem}%"})
        return {"status": "ok", "cpu": cpu, "memory": mem}
    except Exception as e:
        logger.error({"msg": f"Health check failed: {str(e)}"})
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/logs/", response_model=List[schemas.Log])
def get_logs(skip: int = 0, limit: int = 100, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        logger.info({"msg": f"Admin fetching logs: skip={skip}, limit={limit}", "user_id": current_user.id})
        return db.query(models.Log).offset(skip).limit(limit).all()
    else:
        logger.info({"msg": f"User fetching logs: skip={skip}, limit={limit}", "user_id": current_user.id})
        return db.query(models.Log).filter(models.Log.user_id == current_user.id).offset(skip).limit(limit).all()