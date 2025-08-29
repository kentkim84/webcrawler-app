from bs4 import BeautifulSoup

def parse_html_content(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else ""
    body_text = ' '.join([p.get_text() for p in soup.find_all('p')])
    metadata = {
        "meta": {tag.get('name'): tag.get('content') for tag in soup.find_all('meta') if tag.get('name')}
    }
    return title, body_text, metadata