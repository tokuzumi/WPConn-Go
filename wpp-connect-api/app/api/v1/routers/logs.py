from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_tenant
from app.db.models import Tenant, AuditLog
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter()

class LogResponse(BaseModel):
    id: int
    tenant_id: Optional[str] = None # UUID but converted to str
    event: str
    detail: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=list[LogResponse])
async def get_logs(
    limit: int = 50,
    offset: int = 0,
    event: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    from app.db.repositories.log_repository import LogRepository
    repo = LogRepository(db)
    # If tenant is admin, maybe show all? But for now, let's show only tenant's logs
    # Or if the user wants "Logs (General/Error/Per Number)", maybe they want to see everything.
    # Assuming the dashboard user is an Admin managing connections.
    # If the API key belongs to a specific tenant, they should only see their logs.
    # But the dashboard seems to be a "Super Admin" dashboard managing multiple numbers.
    # The current auth is basic.
    # Let's allow filtering by tenant_id if provided, otherwise show all if admin?
    # For now, let's just return logs for the authenticated tenant OR all if we assume admin key.
    # Since we are using "admin-key" in the frontend, let's assume we want to see ALL logs if possible.
    # But `get_current_tenant` resolves a tenant.
    # If we want to see all logs, we might need a different auth mechanism or a "superuser" flag.
    # For this MVP, let's just return logs for the current tenant.
    # Wait, "Per Number" implies we can see logs for different numbers.
    # If I am logged in as "Admin" (which is just a dashboard user), I want to see logs for all tenants.
    # But the API requires `x-api-key`.
    # If I use one tenant's key, I only see that tenant.
    # I might need to relax auth for this endpoint or use a master key.
    # Let's assume for now we return logs for the current tenant.
    # To support "Per Number", we might need to pass `tenant_id` filter.
    # But `get_current_tenant` restricts us.
    # Let's just implement it for the current tenant for now, or maybe the dashboard iterates over tenants?
    # No, "Logs" page usually shows system logs.
    # Let's pass `tenant_id` as None to `get_logs` to fetch all if we want (but repo filters if provided).
    # But `get_current_tenant` enforces a tenant.
    # I'll stick to current tenant for now to be safe, or maybe the dashboard uses a special key.
    
    return await repo.get_logs(limit, offset, tenant_id=str(tenant.id), event=event)
