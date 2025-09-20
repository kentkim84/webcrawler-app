import scrapy
from scraper.scraper.items import ScraperItem
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

class BasicSpider(scrapy.Spider):
    name = 'basic'
    logger = logging.getLogger(__name__)

    def __init__(self, start_url='', *args, **kwargs):
        super(BasicSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        parsed_url = urlparse(start_url)
        self.allowed_domains = [parsed_url.netloc] if parsed_url.netloc else []

    def parse(self, response):
        if response.status != 200:
            item = ScraperItem()
            item['title'] = "Error"
            item['content'] = f"Failed to fetch page: HTTP {response.status}"
            yield item
            return

        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else 'No Title'
            content_elements = soup.find_all('p')
            content = ' '.join([elem.text.strip() for elem in content_elements if elem.text.strip()]) or 'No content found'
            
            item = ScraperItem()
            item['title'] = title
            item['content'] = content
            yield item
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {str(e)}")
            item = ScraperItem()
            item['title'] = "Error"
            item['content'] = f"Failed to parse: {str(e)}"
            yield item