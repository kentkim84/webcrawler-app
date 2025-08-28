-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create app schema
CREATE SCHEMA IF NOT EXISTS crawler;

-- Example: a table to store documents and embeddings
CREATE TABLE IF NOT EXISTS crawler.documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    embedding VECTOR(1536), -- dimension should match your model (e.g., OpenAI ada-002)
    sentiment TEXT,
    topic TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast vector similarity search
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON crawler.documents
USING ivfflat (embedding vector_l2_ops)
WITH (lists = 100);