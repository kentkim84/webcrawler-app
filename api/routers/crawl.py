from fastapi import APIRouter
import uuid

router = APIRouter()

@router.post("/start")
def start_crawl(url: str):
    job_id = str(uuid.uuid4())
    # Normally enqueue job into Scheduler here
    return {"job_id": job_id, "url": url}

@router.get("/status/{job_id}")
def crawl_status(job_id: str):
    return {"job_id": job_id, "status": "running"}