from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.repositories.tenant_repository import TenantRepository
from app.db.models import Tenant

api_key_header = APIKeyHeader(name="x-api-key", auto_error=True)

from app.core.config import settings

async def get_current_tenant(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> Tenant:
    # Master Key Check (Admin Mode)
    import logging
    logger = logging.getLogger(__name__)
    # logger.info(f"Auth Check: Received Key={api_key[:5]}... Expected Secret={settings.APP_SECRET[:5]}...")
    
    if api_key == settings.APP_SECRET:
        return Tenant(id="admin", name="Admin", is_active=True)

    repo = TenantRepository(db)
    tenant = await repo.get_by_api_key(api_key)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant is inactive"
        )
        
    return tenant
