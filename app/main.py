import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.admin.router import router as admin_router
from app.applicants.router import router as applicants_router
from app.cases.router import router as cases_router
from app.config import settings
from app.db import Base, engine
from app.health.router import router as health_router
from app.utils import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Set root path if specified in settings
root_path = settings.ROOT_PATH if settings.ROOT_PATH else ""

# Create the app
app = FastAPI(root_path=root_path)
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

# Cache for landing page template
_landing_page_template: str = ""


@app.on_event("startup")
async def startup_event():
    """Validate application configuration and load required resources."""
    global _landing_page_template

    # Load landing page template - fail fast if not available
    html_path = Path(__file__).parent / "templates" / "index.html"
    try:
        _landing_page_template = html_path.read_text()
        logger.info("Landing page template loaded successfully from %s", html_path)
    except FileNotFoundError as exc:
        logger.critical("Landing page template not found at %s", html_path)
        raise RuntimeError(f"Required template file not found: {html_path}") from exc
    except Exception as e:
        logger.critical("Failed to load landing page template: %s", e)
        raise RuntimeError(f"Failed to load required template: {e}") from e


# Root endpoint with API documentation links
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    """Render an HTML page with links to API documentation."""
    return _landing_page_template


# Add routes
app.include_router(cases_router)
app.include_router(applicants_router)
app.include_router(admin_router)
app.include_router(health_router)
logger.info("API routes registered")
