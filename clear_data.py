import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def clear_data():
    async with AsyncSessionLocal() as db:
        # Disable foreign key checks temporarily or delete in order
        await db.execute(text("TRUNCATE TABLE audit_logs, messages, tenants RESTART IDENTITY CASCADE"))
        await db.commit()
        print("Data cleared.")

if __name__ == "__main__":
    asyncio.run(clear_data())
