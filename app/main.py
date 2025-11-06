import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.admin.router import router as admin_router
from app.applicants.router import router as applicants_router
from app.cases.router import router as cases_router
from app.db import Base, engine
from app.health.router import router as health_router
from app.utils import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Create the app
app = FastAPI()
logger.info("FastAPI application initialized")

# Set up CORS middleware
# TODO: Restrict origins for production use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# Create database
Base.metadata.create_all(bind=engine)
logger.info("Database tables created")


# Root endpoint with API documentation links
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """Render an HTML page with links to API documentation."""
    html_path = Path(__file__).parent / "templates" / "index.html"
    return html_path.read_text()


# Add routes
app.include_router(cases_router)
app.include_router(applicants_router)
app.include_router(admin_router)
app.include_router(health_router)
logger.info("API routes registered")
