from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_tenant
from app.db.models import Tenant, AuditLog
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from uuid import UUID

router = APIRouter()

class LogResponse(BaseModel):
    id: int
    tenant_id: Optional[UUID] = None
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
    
    tenant_id = None if tenant.id == "admin" else str(tenant.id)
    try:
        return await repo.get_logs(limit, offset, tenant_id=tenant_id, event=event)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

@router.post("/{log_id}/retry")
async def retry_webhook(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    # 1. Fetch Log
    from sqlalchemy import select
    query = select(AuditLog).where(AuditLog.id == log_id)
    if tenant.id != "admin":
        query = query.where(AuditLog.tenant_id == tenant.id)
    
    result = await db.execute(query)
    log_entry = result.scalars().first()
    
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log not found")
        
    # 2. Validate Event Type
    if log_entry.event != "webhook_delivery_failed":
        raise HTTPException(status_code=400, detail="Only failed webhook logs can be retried")
        
    # 3. Parse Detail
    import json
    try:
        detail_data = json.loads(log_entry.detail)
    except:
        raise HTTPException(status_code=500, detail="Failed to parse log details")
        
    payload = detail_data.get("payload")
    url = detail_data.get("url")
    
    if not payload or not url:
        raise HTTPException(status_code=400, detail="Log details missing payload or url")
        
    # 4. Resend
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            
            # 5. Log Result
            if response.status_code in [200, 201, 202, 204]:
                # Success! We can maybe update the old log or create a new "success" log.
                # Let's create a new log to show it worked.
                from app.services.log_service import AuditLogger
                await AuditLogger.log(
                    db,
                    "webhook_delivery_retry_success",
                    {"original_log_id": log_id, "status_code": response.status_code},
                    tenant_id=log_entry.tenant_id
                )
                return {"status": "success", "detail": "Webhook resent successfully"}
            else:
                raise Exception(f"Received status code {response.status_code}")
                
    except Exception as e:
         # Log the retry failure too
        from app.services.log_service import AuditLogger
        await AuditLogger.log(
            db,
            "webhook_delivery_retry_failed",
            {"original_log_id": log_id, "error": str(e)},
            tenant_id=log_entry.tenant_id
        )
        raise HTTPException(status_code=502, detail=f"Retry failed: {str(e)}")
