"""
MongoDB database client and connection management.
Provides async MongoDB operations using Motor.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls):
        """Establish connection to MongoDB."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            cls.db = cls.client[settings.mongodb_db_name]
            
            # Test connection
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.mongodb_db_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.db
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection."""
        return cls.get_database()[collection_name]


# Collection names
class Collections:
    """MongoDB collection names."""
    USERS = "users"
    RESUMES = "resumes"
    READINESS_SCORES = "readiness_scores"
    LEARNING_PLANS = "learning_plans"
    LEARNING_PROGRESS = "learning_progress"
    ASSESSMENTS = "assessments"
    JOB_LISTINGS = "job_listings"
    ANALYTICS = "analytics"


# Dependency for FastAPI
async def get_db() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database instance."""
    return MongoDB.get_database()
