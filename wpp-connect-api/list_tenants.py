import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant

async def list_tenants():
    async with AsyncSessionLocal() as db:
        query = select(Tenant)
        result = await db.execute(query)
        tenants = result.scalars().all()
        
        for t in tenants:
            print(f"Tenant: {t.name}, PhoneID: {t.phone_number_id}")

if __name__ == "__main__":
    asyncio.run(list_tenants())
