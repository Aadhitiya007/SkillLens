"""
Initialization script for SkillLens.
Sets up the skill knowledge graph in Neo4j.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Neo4jClient
from app.services.skill_graph import skill_graph_service
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Initialize the skill knowledge graph."""
    try:
        logger.info("Connecting to Neo4j...")
        await Neo4jClient.connect()
        
        logger.info("Initializing skill knowledge graph...")
        await skill_graph_service.initialize_skill_graph()
        
        logger.info("✓ Skill graph initialized successfully!")
        logger.info("You can view the graph at: http://localhost:7474")
        
    except Exception as e:
        logger.error(f"✗ Error initializing skill graph: {e}")
        raise
    
    finally:
        await Neo4jClient.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
