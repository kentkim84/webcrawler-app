import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://crawler:secret@cr-db:5432/crawlerdb")
AI_API_URL = os.getenv("AI_API_URL", "http://cr-ai:8500")