import scrapy

class NewsSpider(scrapy.Spider):
    name = "news"
    start_urls = ["https://example.com"]

    def parse(self, response):
        yield {
            "title": response.css("title::text").get(),
            "url": response.url,
        }