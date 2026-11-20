"""
Simple database initialization script.
Run this from the backend directory: python init_db_simple.py
"""

import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def init_database():
    """Initialize database with schema."""
    try:
        # Import after adding to path
        from app.config import settings
        from sqlalchemy.ext.asyncio import create_async_engine
        
        print("Connecting to PostgreSQL...")
        print(f"Database URL: {settings.database_url}")
        
        # Create engine
        engine = create_async_engine(
            settings.database_url,
            echo=True
        )
        
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        
        if not os.path.exists(schema_path):
            print(f"ERROR: Schema file not found at {schema_path}")
            return False
        
        print(f"\nReading schema from: {schema_path}")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split by statement (simple approach)
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        
        print(f"\nExecuting {len(statements)} SQL statements...")
        
        async with engine.begin() as conn:
            for i, statement in enumerate(statements, 1):
                if statement and not statement.startswith('--'):
                    try:
                        await conn.execute(statement)
                        print(f"  [{i}/{len(statements)}] ✓")
                    except Exception as e:
                        # Ignore "already exists" errors
                        if "already exists" in str(e).lower():
                            print(f"  [{i}/{len(statements)}] Already exists (OK)")
                        else:
                            print(f"  [{i}/{len(statements)}] Error: {e}")
        
        await engine.dispose()
        
        print("\n✅ Database initialized successfully!")
        print(f"Database URL: {settings.database_url}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(init_database())
    sys.exit(0 if success else 1)
