from fastapi import APIRouter

router = APIRouter()

@router.get("/search")
def search_docs(query: str):
    return {"query": query, "results": []}