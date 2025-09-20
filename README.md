# Webcrawler App

## Overview
The **Webcrawler App** is a full-stack application designed to crawl websites, extract data (e.g., titles and content), and provide a user-friendly interface for managing and viewing crawl results. The backend is powered by Python, utilizing **FastAPI** for the API and **Scrapy** for web crawling. The frontend is a **React**-based single-page application. The project is containerized with **Docker** and orchestrated using **Docker Compose** for seamless deployment and development.

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
- **Web Crawling**: Uses Scrapy to crawl websites and extract data such as page titles and paragraph content.
- **API**: FastAPI backend provides endpoints for user authentication, initiating crawls, and retrieving results.
- **Authentication**: Supports user registration and login with JWT-based authentication.
- **Database Integration**: Stores crawled data in a PostgreSQL database using SQLAlchemy, with Pydantic for input/output validation.
- **Frontend UI**: React-based interface for user authentication, submitting crawl requests, and viewing/searching results.
- **Containerization**: Fully containerized with Docker and orchestrated via Docker Compose.

## Prerequisites
- **Docker** and **Docker Compose** (for containerized setup)
- **Python 3.12+** (for local backend development)
- **Node.js 18+** (for local frontend development)

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
   - **Backend API**: Available at `http://localhost:8000`
   - **Frontend UI**: Available at `http://localhost:3000`
   - **Database**: PostgreSQL running on `localhost:5432`

3. **Local Development (Optional)**:
   - **Backend**:
     ```bash
     cd backend
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     export DATABASE_URL=postgresql://user:password@localhost:5432/scraper_db
     export SECRET_KEY=your-secret-key  # Replace with a secure key
     uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
     ```
   - **Frontend**:
     ```bash
     cd frontend
     npm install
     npm start
     ```

## Usage
1. **Register/Login**: Access the frontend at `http://localhost:3000` to register a new user or log in with existing credentials.
2. **Start a Crawl**: After logging in, enter a valid URL (e.g., `https://example.com`) in the frontend form or send a POST request to `/api/scrape/` with a JSON body containing the `url` field.
3. **View Results**: Crawled data (title, content, timestamp) is displayed in the frontend or accessible via the `/api/scrapes/` endpoint.
4. **Search Scrapes**: Use the search bar in the frontend to filter previous crawl results by URL, title, or content.

## API Endpoints
- **POST /register**: Register a new user (`{ "username": "string", "password": "string" }`).
- **POST /token**: Log in and receive a JWT token (`{ "username": "string", "password": "string" }`).
- **POST /scrape/**: Start a crawl for a given URL (`{ "url": "string" }`).
- **GET /scrapes/**: Retrieve all scraped data for the authenticated user, with optional `search` query parameter.
- **GET /users/**: List all users (admin-only).
- **GET /health**: Check API health status.

## Configuration
- **Backend**:
  - Modify `backend/scraper/scraper/settings.py` for Scrapy settings (e.g., `USER_AGENT`, `DOWNLOAD_TIMEOUT`).
  - Update `backend/app/database.py` or `docker-compose.yml` for database connection settings.
  - Set the `SECRET_KEY` environment variable for JWT authentication.
- **Docker**:
  - Adjust `docker-compose.yml` for custom ports, volumes, or environment variables.
  - Ensure the `DATABASE_URL` in `docker-compose.yml` matches your database configuration.
- **Frontend**:
  - Configure API base URL in `frontend/src/App.js` if the backend is hosted elsewhere.

## Security Notes
- Store sensitive configurations (e.g., `DATABASE_URL`, `SECRET_KEY`) in a `.env` file and load them using a library like `python-dotenv`.
- Ensure database credentials are secure in production environments.
- Use HTTPS for production deployments to secure API and frontend communication.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## Notes
- The `middlewares.py` and `pipelines.py` files in `backend/scraper/scraper/` are currently empty but can be extended for custom Scrapy middleware or item processing logic.
- The backend enforces a 30-second timeout for scraping operations to prevent long-running tasks.
- The frontend includes basic URL validation to ensure only valid HTTP/HTTPS URLs are submitted.
- CORS is configured to allow requests from `http://localhost:3000`. Update `backend/app/main.py` for different origins in production.

## License
This project is licensed under the MIT License.