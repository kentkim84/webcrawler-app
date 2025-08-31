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

try:
    crochet.setup()
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
except Exception as e:
    logger.error(f"Failed to initialize crochet: {str(e)}\n{traceback.format_exc()}")
    raise

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    models.Base.metadata.create_all(bind=database.engine)
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}\n{traceback.format_exc()}")
    raise

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
    logger.info(f"Signal handler received item: {dict(item)}, appending to global_results ID: {id(global_results)}")
    global_results.append(dict(item))
    logger.info(f"After append, global_results: {global_results}")
    logger.info(f"Signal handler thread ID: {threading.get_ident()}")

@app.post("/scrape/", response_model=schemas.ScrapedData)
async def scrape_url(request: ScrapeRequest, db: Session = Depends(get_db)):
    url_str = str(request.url)
    logger.info(f"Starting scrape for URL: {url_str}")
    try:
        # Validate URL
        parsed_url = urlparse(url_str)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.error(f"Invalid URL format: {url_str}")
            raise HTTPException(status_code=400, detail="Invalid URL format")

        # Clear global_results before each crawl
        global_results.clear()
        logger.info(f"Cleared global_results, ID: {id(global_results)}")
        
        # Set up Scrapy crawler
        settings = get_project_settings()
        settings.set('REQUEST_FINGERPRINTER_IMPLEMENTATION', '2.7')
        settings.set('USER_AGENT', 'Mozilla/5.0 (compatible; ScraperBot/1.0)')
        settings.set('DOWNLOAD_TIMEOUT', 10)

        runner = CrawlerRunner(settings)
        crawler = runner.create_crawler(BasicSpider)  # No start_url here
        crawler.signals.connect(handle_item_scraped, signal=item_scraped)
        logger.info(f"Starting Scrapy crawler for {url_str}, global_results ID: {id(global_results)}")
        try:
            deferred = runner.crawl(crawler, start_url=url_str)  # Pass start_url to crawl
            wait_for_crawl = crochet.run_in_reactor(lambda: deferred)
            wait_for_crawl().wait(timeout=30)
            logger.info(f"Crawl completed for {url_str}, global_results: {global_results}")
            logger.info(f"Main thread ID: {threading.get_ident()}")
        except crochet.TimeoutError as e:
            logger.error(f"Crawl timed out for {url_str}: {str(e)}")
            raise HTTPException(status_code=500, detail="Scraping failed: Crawl timed out after 30 seconds")
        except Exception as e:
            logger.error(f"Crawl failed for {url_str}: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Scraping failed: Crawler error: {str(e) or 'Unknown crawler error'}")

        if not global_results:
            logger.error(f"No items scraped for {url_str}. global_results: {global_results}")
            raise HTTPException(status_code=500, detail="Scraping failed: No data scraped from the URL. Check logs for details.")

        item = global_results[0]
        logger.info(f"Scraped item: {item}")
        if item.get('title') == "Error":
            logger.error(f"Spider returned error item: {item['content']}")
            raise HTTPException(status_code=500, detail=f"Scraping failed: {item['content']}")

        db_item = models.ScrapedData(url=url_str, title=item["title"], content=item["content"])
        db.add(db_item)
        try:
            db.commit()
            db.refresh(db_item)
            logger.info(f"Data saved to database for {url_str}")
        except Exception as db_e:
            logger.error(f"Database error for {url_str}: {str(db_e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Scraping failed: Database error: {str(db_e)}")

        return db_item

    except Exception as e:
        logger.error(f"Error scraping {url_str}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e) or 'Check server logs for details'}")

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        models.Base.metadata.create_all(bind=database.engine)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Health check failed")