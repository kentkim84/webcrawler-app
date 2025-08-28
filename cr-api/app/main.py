from fastapi import FastAPI
from app.routers import routes_crawls, routes_docs, routes_ai, routes_exports

app = FastAPI(title="Crawler API")

# Include routers
app.include_router(routes_crawls.router, prefix="/crawls", tags=["Crawls"])
app.include_router(routes_docs.router, prefix="/docs", tags=["Documents"])
app.include_router(routes_ai.router, prefix="/ai", tags=["AI"])
app.include_router(routes_exports.router, prefix="/exports", tags=["Exports"])

@app.get("/")
def root():
    return {"message": "Crawler API is running"}