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
        self.logger.info(f"Initialized spider with start_url: {start_url}, allowed_domains: {self.allowed_domains}")

    def parse(self, response):
        self.logger.info(f"Parsing response from {response.url}, status: {response.status}, headers: {response.headers}")
        try:
            if response.status != 200:
                self.logger.error(f"Non-200 response for {response.url}: {response.status}")
                item = ScraperItem()
                item['title'] = "Error"
                item['content'] = f"Failed to fetch page: HTTP {response.status}"
                self.logger.info(f"Yielding error item: {dict(item)}")
                yield item
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.debug(f"Response body preview: {response.text[:500]}")  # Log first 500 chars
            
            # Extract title
            title = soup.title.string.strip() if soup.title else 'No Title'
            
            # Try multiple tags for content
            content_elements = (
                soup.find_all('p')[:5] + 
                soup.find_all('div', class_=['a-section', 'content'])[:5] + 
                soup.find_all('span', class_=['a-text'])[:5]
            )
            content = ' '.join([elem.text.strip() for elem in content_elements if elem.text.strip()]) or 'No content found'
            
            item = ScraperItem()
            item['title'] = title
            item['content'] = content
            self.logger.info(f"Yielding item: {dict(item)}")
            yield item
        except Exception as e:
            self.logger.error(f"Error parsing {response.url}: {str(e)}\n{traceback.format_exc()}")
            item = ScraperItem()
            item['title'] = "Error"
            item['content'] = f"Failed to parse: {str(e) or 'Unknown parsing error'}"
            self.logger.info(f"Yielding error item: {dict(item)}")
            yield item