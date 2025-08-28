from fastapi import APIRouter

router = APIRouter()

@router.post("/generate")
def generate_export(format: str = "csv"):
    return {"message": f"Export generated in {format} format"}