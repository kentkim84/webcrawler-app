from fastapi import FastAPI
from . import nlp, embeddings

app = FastAPI(title="AI/NLP Service")

@app.post("/analyze")
def analyze_text(text: str):
    return {"summary": nlp.summarize(text), "sentiment": nlp.sentiment(text)}

@app.post("/embed")
def embed_text(text: str):
    return {"vector": embeddings.embed(text)}