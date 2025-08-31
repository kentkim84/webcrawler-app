import scrapy

class ScraperItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()