import scrapy
from app.items import DocumentItem
from app.utils.html_parser import parse_html_content

class GenericSpider(scrapy.Spider):
    name = "generic_spider"

    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []

    def parse(self, response):
        item = DocumentItem()
        item["url"] = response.url
        item["title"], item["body_text"], item["metadata"] = parse_html_content(response.text)
        item["fetched_at"] = response.headers.get("Date")
        yield item