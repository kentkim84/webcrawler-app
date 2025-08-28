-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema
CREATE SCHEMA IF NOT EXISTS crawler;

-- =====================
-- Users
-- =====================
CREATE TABLE IF NOT EXISTS crawler.users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    role TEXT CHECK (role IN ('admin', 'analyst', 'viewer')) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- Crawl Jobs
-- =====================
CREATE TABLE IF NOT EXISTS crawler.crawls (
    crawl_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    start_time TIMESTAMP DEFAULT NOW(),
    end_time TIMESTAMP,
    status TEXT CHECK (status IN ('pending','running','completed','failed')) NOT NULL,
    target_url TEXT NOT NULL,
    depth INT DEFAULT 1,
    created_by UUID REFERENCES crawler.users(user_id) ON DELETE SET NULL
);

-- =====================
-- Raw Documents
-- =====================
CREATE TABLE IF NOT EXISTS crawler.documents_raw (
    doc_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    crawl_id UUID REFERENCES crawler.crawls(crawl_id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    html_content TEXT,
    headers JSONB,
    fetched_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- Cleaned Documents
-- =====================
CREATE TABLE IF NOT EXISTS crawler.documents_clean (
    clean_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID REFERENCES crawler.documents_raw(doc_id) ON DELETE CASCADE,
    title TEXT,
    body_text TEXT,
    language TEXT,
    word_count INT,
    processed_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- Enriched Documents (AI/NLP results)
-- =====================
CREATE TABLE IF NOT EXISTS crawler.documents_enriched (
    enrich_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clean_id UUID REFERENCES crawler.documents_clean(clean_id) ON DELETE CASCADE,
    embedding VECTOR(1536), -- dimension must match embedding model
    sentiment TEXT,
    topics TEXT[],
    summary TEXT,
    entities JSONB,
    enriched_at TIMESTAMP DEFAULT NOW()
);

-- Vector index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_documents_embedding
    ON crawler.documents_enriched
    USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);

-- =====================
-- Exports
-- =====================
CREATE TABLE IF NOT EXISTS crawler.exports (
    export_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES crawler.users(user_id) ON DELETE SET NULL,
    format TEXT CHECK (format IN ('csv','json','pdf')),
    filters JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    file_path TEXT
);