from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def get_crawl_status():
    # Placeholder response
    return {"status": "no active crawls"}

@router.post("/start")
def start_crawl(target_url: str, depth: int = 1):
    return {"message": f"Crawl started for {target_url} with depth {depth}"}