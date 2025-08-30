BOT_NAME = "scraper_bot"

SPIDER_MODULES = ["scrapy_app.spiders"]
NEWSPIDER_MODULE = "scrapy_app.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 4
DOWNLOAD_TIMEOUT = 30
RETRY_ENABLED = True
RETRY_TIMES = 2

# pipelines can be enabled later
ITEM_PIPELINES = {
    # "scrapy_app.pipelines.ToJsonPipeline": 300,
}
