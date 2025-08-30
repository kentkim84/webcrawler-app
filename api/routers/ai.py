from fastapi import APIRouter

router = APIRouter()

@router.post("/run")
def run_analysis(job_id: str):
    return {"job_id": job_id, "status": "analysis_started"}

@router.get("/status/{job_id}")
def analysis_status(job_id: str):
    return {"job_id": job_id, "status": "processing"}

@router.get("/result/{job_id}")
def analysis_result(job_id: str):
    return {"job_id": job_id, "summary": "Sample AI/NLP summary"}