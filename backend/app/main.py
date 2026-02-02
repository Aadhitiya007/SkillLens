"""
SkillLens FastAPI Application
Main entry point for the backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting SkillLens backend...")
    
    # Connect to PostgreSQL database
    from app.database import PostgreSQL
    
    await PostgreSQL.connect()
    logger.info("Connected to PostgreSQL database")
    
    # Create tables if they don't exist (development only)
    if settings.environment == "development":
        await PostgreSQL.create_tables()
        logger.info("Database tables created/verified")
    
    # Validate API keys
    api_key_status = settings.validate_api_keys()
    logger.info(f"API Key Status: {api_key_status}")
    
    if not all(api_key_status.values()):
        logger.warning("Some API keys are missing. Check .env file.")
    
    logger.info("SkillLens backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SkillLens backend...")
    await PostgreSQL.disconnect()
    logger.info("Disconnected from PostgreSQL database")
    logger.info("SkillLens backend shut down successfully")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Career Intelligence & Workforce Readiness Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to SkillLens API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug
    }


# Import and include routers
from app.routers import analytics, auth, resume, scoring

# Working routers with PostgreSQL
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(scoring.router, prefix="/api/scoring", tags=["Scoring"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# TODO: Update remaining routers to use PostgreSQL:
# - predictions: Pydantic schema errors
# - verification: Needs PostgreSQL updates
# - jobs: Import hangs
# - agent: Pydantic/LangChain compatibility
# - skills: Needs PostgreSQL updates

# from app.routers import predictions, verification, jobs, skills
# app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
# app.include_router(verification.router, prefix="/api/verification", tags=["Verification"])
# app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
# app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
