FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Example: service with FastAPI exposing AI functions
EXPOSE 8500
CMD ["uvicorn", "ai_service:app", "--host", "0.0.0.0", "--port", "8500"]