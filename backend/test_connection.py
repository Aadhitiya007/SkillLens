import asyncio
import asyncpg
import os
import sys

# Database URL from .env
# DATABASE_URL=postgresql+asyncpg://skilllens:skilllens@localhost:5432/skilllens
DSN = "postgresql://skilllens:skilllens@localhost:5432/skilllens"

async def check_connection():
    try:
        print(f"Connecting to {DSN}...")
        conn = await asyncpg.connect(DSN)
        print("Successfully connected!")
        await conn.close()
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    success = asyncio.run(check_connection())
    sys.exit(0 if success else 1)
