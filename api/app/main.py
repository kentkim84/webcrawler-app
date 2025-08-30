from fastapi import FastAPI
from .routers import crawl, results, ai

app = FastAPI(title="Web Scraper API")

app.include_router(crawl.router, prefix="/crawl", tags=["Crawl"])
app.include_router(results.router, prefix="/crawl", tags=["Results"])
app.include_router(ai.router, prefix="/analysis", tags=["AI"])