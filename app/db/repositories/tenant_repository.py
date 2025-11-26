from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Tenant
from app.schemas.tenant import TenantCreate

class TenantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tenant(self, tenant: TenantCreate) -> Tenant:
        db_tenant = Tenant(
            name=tenant.name,
            waba_id=tenant.waba_id,
            phone_number_id=tenant.phone_number_id,
            token=tenant.token
        )
        self.db.add(db_tenant)
        await self.db.commit()
        await self.db.refresh(db_tenant)
        return db_tenant

    async def get_by_phone_id(self, phone_number_id: str) -> Tenant | None:
        query = select(Tenant).where(Tenant.phone_number_id == phone_number_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> list[Tenant]:
        query = select(Tenant)
        result = await self.db.execute(query)
        return result.scalars().all()
