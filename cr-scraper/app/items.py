import scrapy

class DocumentItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    body_text = scrapy.Field()
    metadata = scrapy.Field()  # e.g., headers, publish date, author
    fetched_at = scrapy.Field()