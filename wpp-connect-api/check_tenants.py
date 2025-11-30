import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Tenant))
        tenants = result.scalars().all()
        print(f"Found {len(tenants)} tenants.")
        for t in tenants:
            print(f"ID: {t.id}, Phone Number ID: {t.phone_number_id}, Name: {t.name}")

if __name__ == "__main__":
    asyncio.run(main())
