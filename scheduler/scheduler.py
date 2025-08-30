from celery import Celery

app = Celery("tasks", broker="redis://redis:6379/0")

@app.task
def crawl_task(url: str):
    return f"Crawling {url}"

@app.task
def analyze_task(data: str):
    return f"Analyzing {data}"