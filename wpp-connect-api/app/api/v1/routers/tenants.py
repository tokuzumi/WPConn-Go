from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.tenant import TenantCreate, TenantResponse
from app.db.repositories.tenant_repository import TenantRepository
from app.services.log_service import AuditLogger

router = APIRouter()

@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = TenantRepository(db)
    
    # Check if tenant already exists
    existing_tenant = await repo.get_by_phone_id(tenant.phone_number_id)
    if existing_tenant:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant with this phone_number_id already exists"
        )
    
    new_tenant = await repo.create_tenant(tenant)
    
    await AuditLogger.log(
        db, 
        "tenant_created", 
        {"name": new_tenant.name, "waba_id": new_tenant.waba_id},
        tenant_id=new_tenant.id
    )
    
    return new_tenant

@router.get("/", response_model=list[TenantResponse])
async def get_tenants(
    db: AsyncSession = Depends(get_db)
):
    repo = TenantRepository(db)
    return await repo.get_all()

@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: str,
    db: AsyncSession = Depends(get_db)
):
    repo = TenantRepository(db)
    success = await repo.delete_tenant(tenant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
