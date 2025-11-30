import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant
from sqlalchemy import select, update

async def main():
    async with AsyncSessionLocal() as db:
        # Find the existing tenant (we know there is only one from previous checks)
        result = await db.execute(select(Tenant))
        tenant = result.scalars().first()
        
        if tenant:
            print(f"Updating Tenant {tenant.name}...")
            print(f"Old Phone Number ID: {tenant.phone_number_id}")
            
            stmt = (
                update(Tenant)
                .where(Tenant.id == tenant.id)
                .values(phone_number_id="123456123")
            )
            await db.execute(stmt)
            await db.commit()
            
            print(f"New Phone Number ID: 123456123")
        else:
            print("No tenant found to update.")

if __name__ == "__main__":
    asyncio.run(main())
