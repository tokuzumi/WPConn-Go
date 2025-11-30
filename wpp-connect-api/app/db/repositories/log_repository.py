from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import AuditLog
from typing import Optional

class LogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_logs(
        self, 
        limit: int = 50, 
        offset: int = 0,
        tenant_id: Optional[str] = None,
        event: Optional[str] = None
    ) -> list[AuditLog]:
        query = select(AuditLog)
        
        if tenant_id:
            query = query.where(AuditLog.tenant_id == tenant_id)
            
        if event:
            query = query.where(AuditLog.event.ilike(f"%{event}%"))
            
        query = query.order_by(desc(AuditLog.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
