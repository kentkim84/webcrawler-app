from fastapi import APIRouter

router = APIRouter()

@router.get("/result/{job_id}")
def get_result(job_id: str):
    return {"job_id": job_id, "data": ["sample", "scraped", "data"]}