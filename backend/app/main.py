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
import traceback
import threading
from urllib.parse import urlparse
from pydantic import HttpUrl, BaseModel
from scrapy.utils.reactor import install_reactor

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

@app.post("/scrape/", response_model=schemas.ScrapedData)
async def scrape_url(request: ScrapeRequest, db: Session = Depends(get_db)):
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

    db_item = models.ScrapedData(url=url_str, title=item["title"], content=item["content"])
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    return {"status": "ok"}