"""
MongoDB Database Connection
Simple async MongoDB wrapper.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings


class MongoDB:
    """MongoDB connection manager."""
    
    client = None
    database = None
    
    @classmethod
    def connect(cls):
        """Connect to MongoDB."""
        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            cls.database = cls.client[settings.mongodb_db_name]
    
    @classmethod
    def get_database(cls):
        """Get database instance."""
        if cls.database is None:
            cls.connect()
        return cls.database
    
    @classmethod
    def close(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
