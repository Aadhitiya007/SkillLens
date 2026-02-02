"""
PostgreSQL database connection and session management.
Provides async SQLAlchemy engine and session factory.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from typing import AsyncGenerator
import logging

from app.config import settings
from app.database.models import Base

logger = logging.getLogger(__name__)


class PostgreSQL:
    """PostgreSQL connection manager."""
    
    engine = None
    async_session_factory = None
    
    @classmethod
    async def connect(cls):
        """Initialize database engine and session factory."""
        try:
            # Create async engine
            cls.engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                poolclass=NullPool if settings.environment == "test" else None,
                pool_pre_ping=True,  # Verify connections before using
                pool_size=5,
                max_overflow=10,
            )
            
            # Create session factory
            cls.async_session_factory = async_sessionmaker(
                cls.engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
            
            # Test connection
            async with cls.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            logger.info("Connected to PostgreSQL database")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Close database connections."""
        if cls.engine:
            await cls.engine.dispose()
            logger.info("Disconnected from PostgreSQL")
    
    @classmethod
    async def create_tables(cls):
        """Create all tables (for development/testing)."""
        if not cls.engine:
            raise RuntimeError("Database not initialized. Call connect() first.")
        
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Created all database tables")
    
    @classmethod
    async def drop_tables(cls):
        """Drop all tables (for testing)."""
        if not cls.engine:
            raise RuntimeError("Database not initialized. Call connect() first.")
        
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("Dropped all database tables")
    
    @classmethod
    def get_session_factory(cls) -> async_sessionmaker:
        """Get session factory."""
        if cls.async_session_factory is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.async_session_factory


# FastAPI dependency for database sessions
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session.
    
    Usage:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            users = result.scalars().all()
            return users
    """
    session_factory = PostgreSQL.get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Convenience function for manual session creation
async def create_session() -> AsyncSession:
    """Create a new database session manually."""
    session_factory = PostgreSQL.get_session_factory()
    return session_factory()
