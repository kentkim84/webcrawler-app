import scrapy
from scrapy_app.items import ScrapedItem
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class NewsSpider(scrapy.Spider):
    name = "news"

    # url is expected as -a url=...
    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not url:
            raise ValueError("start url required via -a url=")
        self.start_urls = [url]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("title")
        article = soup.find("article") or soup.find("div", {"class": "article"}) or soup

        text = []
        for p in article.find_all("p"):
            text.append(p.get_text(strip=True))

        item = ScrapedItem()
        item["url"] = response.url
        item["title"] = title_tag.get_text(strip=True) if title_tag else ""
        item["text"] = "\n\n".join(text).strip()
        item["meta"] = {m.get("name") or m.get("property"): m.get("content") for m in soup.find_all("meta") if (m.get("name") or m.get("property"))}
        yield item

        # follow some internal links (very shallow)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#"):
                continue
            absolute = urljoin(response.url, href)
            if self.allowed_domain_check(absolute):
                yield scrapy.Request(absolute, callback=self.parse)

    def allowed_domain_check(self, url):
        # basic: keep same domain for this simple demo
        from urllib.parse import urlparse
        s = urlparse(self.start_urls[0]).netloc
        t = urlparse(url).netloc
        return s == t
