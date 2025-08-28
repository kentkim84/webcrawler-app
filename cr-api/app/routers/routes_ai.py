from fastapi import APIRouter

router = APIRouter()

@router.get("/embedding")
def get_embedding(text: str):
    return {"text": text, "embedding": [0.0]*1536}