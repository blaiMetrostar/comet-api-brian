from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.applicants.router import router as applicants_router
from app.cases.router import router as cases_router
from app.db import Base, engine
from app.health.router import router as health_router

# Create the app
app = FastAPI()
# Set up CORS middleware
# TODO: Restrict origins for production use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create database
Base.metadata.create_all(bind=engine)
# Add routes
app.include_router(cases_router)
app.include_router(applicants_router)
app.include_router(admin_router)
app.include_router(health_router)
