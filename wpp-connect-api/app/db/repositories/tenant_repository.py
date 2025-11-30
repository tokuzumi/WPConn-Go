from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Tenant
from app.schemas.tenant import TenantCreate
import secrets

class TenantRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tenant(self, tenant_in: TenantCreate) -> Tenant:
        api_key = secrets.token_urlsafe(32)
        db_tenant = Tenant(
            name=tenant_in.name,
            waba_id=tenant_in.waba_id,
            phone_number_id=tenant_in.phone_number_id,
            token=tenant_in.token,
            webhook_url=tenant_in.webhook_url,
            api_key=api_key
        )
        self.db.add(db_tenant)
        await self.db.commit()
        await self.db.refresh(db_tenant)
        return db_tenant

    async def get_by_phone_id(self, phone_number_id: str) -> Tenant | None:
        query = select(Tenant).where(Tenant.phone_number_id == phone_number_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_by_api_key(self, api_key: str) -> Tenant | None:
        query = select(Tenant).where(Tenant.api_key == api_key)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self) -> list[Tenant]:
        query = select(Tenant)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_tenant(self, tenant_id: str) -> bool:
        query = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.db.execute(query)
        tenant = result.scalars().first()
        if tenant:
            await self.db.delete(tenant)
            await self.db.commit()
            return True
        return False
