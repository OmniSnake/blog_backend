import asyncio
import os
import sys
from asyncpg import connect, exceptions


async def check_db_connection():
    max_retries = 30
    retry_delay = 2

    db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:password@db:5432/blog_db')

    for i in range(max_retries):
        try:
            conn = await connect(db_url)
            await conn.close()
            print("✅ Database is ready!")
            return True
        except exceptions.ConnectionDoesNotExistError:
            print(f"❌ Database connection failed. Retry {i + 1}/{max_retries}...")
            await asyncio.sleep(retry_delay)
        except Exception as e:
            print(f"❌ Unexpected error: {e}. Retry {i + 1}/{max_retries}...")
            await asyncio.sleep(retry_delay)

    print("❌ Could not connect to database after all retries")
    return False


if __name__ == "__main__":
    success = asyncio.run(check_db_connection())
    sys.exit(0 if success else 1)