import asyncio
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer
from app.spiders.generic_spider import GenericSpider
from scrapy.utils.log import configure_logging

configure_logging()

def run_crawler(url: str):
    """
    Run Scrapy spider programmatically for the given URL.
    Returns crawled items as a list of dicts.
    """
    results = []

    runner = CrawlerRunner()

    @defer.inlineCallbacks
    def crawl():
        yield runner.crawl(GenericSpider, start_url=url)
        reactor.stop()

    def collect_item(item, response, spider):
        results.append(dict(item))

    for spider_cls in runner.spiders.values():
        spider_cls.signals.connect(collect_item, signal="item_scraped")

    crawl()
    reactor.run()  # blocks until crawling finishes
    return results


# Async wrapper (so cr-api can await it)
async def async_run_crawler(url: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_crawler, url)