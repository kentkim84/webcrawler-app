BOT_NAME = 'scraper'
SPIDER_MODULES = ['scraper.scraper.spiders']
NEWSPIDER_MODULE = 'scraper.scraper.spiders'
ROBOTSTXT_OBEY = True
LOG_LEVEL = 'INFO'
USER_AGENT = 'Mozilla/5.0 (compatible; ScraperBot/1.0)'
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
DOWNLOAD_TIMEOUT = 10