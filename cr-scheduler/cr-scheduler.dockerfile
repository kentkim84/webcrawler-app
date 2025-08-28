FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Start Celery worker (adjust module name if needed)
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]