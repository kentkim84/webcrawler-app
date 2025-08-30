from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from scrapy import signals
from scrapy.signalmanager import dispatcher
import json
from scraper_pkg.spiders.simple_spider import SimpleSpider


app = FastAPI()


class ScrapeRequest(BaseModel):
    url: HttpUrl


@app.post('/scrape')
def scrape(req: ScrapeRequest):
    """Run a short scrapy crawl in-process and return the first result synchronously.
    Note: in-production you should run spiders as tasks (Celery, background workers) instead.
    """
    url = req.url
    results = []


    # Ensure previous signal handlers are cleared
    dispatcher.disconnect_all()


    def handle_item(item, response, spider):
        results.append(item)


    # attach signal
    dispatcher.connect(lambda item, response, spider: handle_item(item, response, spider), signals.item_passed)


    runner = CrawlerRunner(get_project_settings())


    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(SimpleSpider, start_url=url)
        reactor.stop()


    try:
        crawl()
        reactor.run() # will block until crawling finishes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    if not results:
        raise HTTPException(status_code=404, detail='No items extracted')


    # return the first item (already cleaned/normalized in pipelines)
    return results[0]