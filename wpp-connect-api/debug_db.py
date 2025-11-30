import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def test_connection():
    print(f"Testing connection to: {settings.DATABASE_URL.split('@')[-1]}") # Hide credentials
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())
