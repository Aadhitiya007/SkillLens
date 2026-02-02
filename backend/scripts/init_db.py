"""
Database initialization script.
Creates all tables and optionally seeds initial data.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import PostgreSQL
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize database with all tables."""
    try:
        logger.info("Connecting to PostgreSQL...")
        await PostgreSQL.connect()
        
        logger.info("Creating database tables...")
        await PostgreSQL.create_tables()
        
        logger.info("✅ Database initialized successfully!")
        logger.info(f"Database URL: {settings.database_url}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise
    finally:
        await PostgreSQL.disconnect()


async def seed_data():
    """Seed initial data (optional)."""
    from app.database import create_session, User, Skill
    from app.services.auth_service import get_password_hash
    
    try:
        logger.info("Seeding initial data...")
        
        async with await create_session() as session:
            # Create admin user
            admin = User(
                email="admin@skilllens.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role="admin",
                is_active=True
            )
            session.add(admin)
            
            # Add some common skills
            skills = [
                Skill(name="Python", category="Programming", difficulty_level="intermediate"),
                Skill(name="JavaScript", category="Programming", difficulty_level="intermediate"),
                Skill(name="React", category="Frontend", difficulty_level="intermediate"),
                Skill(name="Node.js", category="Backend", difficulty_level="intermediate"),
                Skill(name="SQL", category="Database", difficulty_level="beginner"),
                Skill(name="Docker", category="DevOps", difficulty_level="intermediate"),
                Skill(name="AWS", category="Cloud", difficulty_level="advanced"),
            ]
            session.add_all(skills)
            
            await session.commit()
            logger.info("✅ Initial data seeded successfully!")
            
    except Exception as e:
        logger.error(f"❌ Failed to seed data: {e}")
        raise


async def main():
    """Main initialization function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize SkillLens database")
    parser.add_argument("--seed", action="store_true", help="Seed initial data")
    parser.add_argument("--drop", action="store_true", help="Drop all tables first (DANGEROUS)")
    args = parser.parse_args()
    
    if args.drop:
        confirm = input("⚠️  This will DROP ALL TABLES. Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            await PostgreSQL.connect()
            await PostgreSQL.drop_tables()
            await PostgreSQL.disconnect()
            logger.info("✅ All tables dropped")
        else:
            logger.info("Aborted")
            return
    
    await init_database()
    
    if args.seed:
        await PostgreSQL.connect()
        await seed_data()
        await PostgreSQL.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
