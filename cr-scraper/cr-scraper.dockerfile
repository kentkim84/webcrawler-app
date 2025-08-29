FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Scrapy + lxml
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# The scraper itself won't run standalone — cr-api will call it