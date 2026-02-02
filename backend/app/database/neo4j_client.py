"""
Neo4j database client and connection management.
Provides graph database operations for skill ontology.
"""

from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import Optional, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j connection manager."""
    
    driver: Optional[AsyncDriver] = None
    
    @classmethod
    async def connect(cls):
        """Establish connection to Neo4j."""
        try:
            cls.driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            
            # Test connection
            async with cls.driver.session() as session:
                result = await session.run("RETURN 1 AS test")
                await result.single()
            
            logger.info("Connected to Neo4j")
            
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """Close Neo4j connection."""
        if cls.driver:
            await cls.driver.close()
            logger.info("Disconnected from Neo4j")
    
    @classmethod
    def get_driver(cls) -> AsyncDriver:
        """Get driver instance."""
        if cls.driver is None:
            raise RuntimeError("Neo4j driver not initialized. Call connect() first.")
        return cls.driver
    
    @classmethod
    async def execute_query(cls, query: str, parameters: dict = None) -> list[dict]:
        """Execute a Cypher query and return results."""
        async with cls.driver.session() as session:
            result = await session.run(query, parameters or {})
            return [record.data() async for record in result]
    
    @classmethod
    async def execute_write(cls, query: str, parameters: dict = None) -> Any:
        """Execute a write transaction."""
        async with cls.driver.session() as session:
            result = await session.run(query, parameters or {})
            summary = await result.consume()
            return summary


# Dependency for FastAPI
async def get_neo4j() -> AsyncDriver:
    """FastAPI dependency to get Neo4j driver."""
    return Neo4jClient.get_driver()
