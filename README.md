# Webcrawler App

## Overview
The **Webcrawler App** is a full-stack application designed to crawl websites, extract data, and provide a user interface for managing and viewing crawl results. The backend is built with Python using FastAPI for the API and Scrapy for web crawling, while the frontend is a React-based single-page application. The project is containerized using Docker and orchestrated with Docker Compose for easy deployment.

## Project Structure
```
webcrawler-app/
├── backend/                    # Backend services (FastAPI + Scrapy)
│   ├── Dockerfile             # Docker build instructions for backend
│   ├── app/                   # FastAPI application
│   │   ├── database.py        # Database connection and session management
│   │   ├── main.py            # FastAPI app entry point with API routes
│   │   ├── models.py          # SQLAlchemy database models
│   │   └── schemas.py         # Pydantic models for API validation
│   ├── requirements.txt       # Python dependencies
│   └── scraper/               # Scrapy web crawler
│       ├── scrapy.cfg         # Scrapy configuration
│       └── scraper/
│           ├── items.py       # Scrapy item definitions
│           ├── middlewares.py # Custom Scrapy middlewares (currently empty)
│           ├── pipelines.py   # Item processing and storage logic
│           ├── settings.py    # Scrapy settings
│           └── spiders/
│               └── basic_spider.py # Core crawling logic
├── docker-compose.yml         # Docker Compose configuration
└── frontend/                  # React frontend
    ├── Dockerfile             # Docker build instructions for frontend
    ├── package.json           # Node.js dependencies and scripts
    ├── public/
    │   └── index.html         # HTML entry point
    └── src/
        ├── App.js             # Main React component
        └── index.js           # React app entry point
```

## Features
- **Web Crawling**: Uses Scrapy to recursively crawl websites and extract data (e.g., URLs, titles, content).
- **API**: FastAPI backend provides endpoints to start crawls, retrieve results, and manage tasks.
- **Database Integration**: Stores crawled data using SQLAlchemy, with Pydantic for validation.
- **Frontend UI**: React-based interface for submitting crawl requests and viewing results.
- **Containerization**: Dockerized backend and frontend services, orchestrated with Docker Compose.

## Prerequisites
- Docker and Docker Compose
- Python 3.8+ (for local backend development)
- Node.js 16+ (for local frontend development)

## Setup and Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/kentkim84/webcrawler-app.git
   cd webcrawler-app
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```
   - Backend API: `http://localhost:8000`
   - Frontend UI: `http://localhost:3000`

3. **Local Development (Optional)**:
   - **Backend**:
     ```bash
     cd backend
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     ```
   - **Frontend**:
     ```bash
     cd frontend
     npm install
     npm start
     ```

## Usage
- **Start a Crawl**: Use the frontend UI or send a POST request to the API (e.g., `/api/crawl`) with a target URL.
- **View Results**: Access crawled data via the frontend or API endpoints (e.g., `/api/results`).
- **Database**: Crawled data is stored in a database (configured in `docker-compose.yml`, e.g., PostgreSQL).

## Configuration
- **Backend**:
  - Edit `backend/scraper/scraper/settings.py` for Scrapy settings (e.g., concurrency, user-agent).
  - Configure database in `backend/app/database.py` (e.g., connection string).
- **Docker**:
  - Update `docker-compose.yml` for ports, volumes, or database settings.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## Notes
- The `middlewares.py` file is currently empty and can be extended for custom Scrapy middleware (e.g., proxies, retries).
- Ensure database credentials are secure in production.
- Add environment variables for sensitive configurations (e.g., `.env` file).

## License
This project is licensed under the MIT License.