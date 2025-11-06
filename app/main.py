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

# Load and cache the landing page template at startup
_landing_page_template: str | None = None
try:
    html_path = Path(__file__).parent / "templates" / "index.html"
    _landing_page_template = html_path.read_text()
    logger.info("Landing page template loaded successfully")
except Exception as e:
    logger.error("Failed to load landing page template from %s: %s", html_path, e)


# Root endpoint with API documentation links
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    """Render an HTML page with links to API documentation."""
    if _landing_page_template is None:
        logger.error("Landing page template not available")
        return HTMLResponse(
            content=(
                "Error: Unable to load the homepage template. "
                "Please contact the administrator."
            ),
            status_code=500,
        )
    return _landing_page_template


# Add routes
app.include_router(cases_router)
app.include_router(applicants_router)
app.include_router(admin_router)
app.include_router(health_router)
logger.info("API routes registered")
