from scrapy import Spider, Request
from bs4 import BeautifulSoup
from ..pipelines import clean_and_normalize


class SimpleSpider(Spider):
    name = 'simple'


    def __init__(self, start_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]


    def parse(self, response):
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')


        # title
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''


        # extract visible text (naive)
        for script in soup(['script', 'style']):
            script.decompose()
        text = ' '.join(part.strip() for part in soup.stripped_strings)


        # cleaning and normalization
        normalized = clean_and_normalize(title, text)


        yield {
            'url': response.url,
            'title': title,
            'text_snippet': text[:2000],
            'normalized': normalized,
        }