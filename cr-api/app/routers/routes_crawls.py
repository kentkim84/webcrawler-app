from fastapi import APIRouter
from cr_scraper.crawler_runner import async_run_crawler

router = APIRouter()

@router.get("/status")
def get_crawl_status():
    # Placeholder response
    return {"status": "no active crawls"}

@router.post("/start")
def start_crawl(target_url: str, depth: int = 1):
    return {"message": f"Crawl started for {target_url} with depth {depth}"}

@router.get("/crawl")
async def crawl_url(url: str = Query(..., description="Target URL to crawl")):
    results = await async_run_crawler(url)
    return {"count": len(results), "data": results}