import logging
import json
from typing import Union, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AuditLog
from uuid import UUID

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    async def log(
        db: AsyncSession, 
        event: str, 
        detail: Union[Dict, str], 
        tenant_id: UUID = None
    ):
        try:
            # Ensure detail is a string
            if isinstance(detail, dict):
                detail_str = json.dumps(detail, default=str)
            else:
                detail_str = str(detail)

            audit_entry = AuditLog(
                tenant_id=tenant_id,
                event=event,
                detail=detail_str
            )
            db.add(audit_entry)
            # We don't commit here to allow the caller to manage the transaction 
            # or we can commit if we want it to be independent. 
            # Given the requirement "silently handle exceptions", 
            # it might be safer to commit immediately to ensure log is saved 
            # even if main transaction fails, OR use a separate session.
            # However, usually audit logs are part of the transaction or fire-and-forget.
            # Let's assume we want to persist it immediately for visibility.
            # But since we are receiving 'db' session from dependency injection which might be used by others,
            # committing here might commit other changes prematurely.
            # BUT, the prompt says "logs no banco", and usually we want them even if operation fails?
            # Actually, for "message_send_failed", the operation failed, so we are likely in an exception handler.
            # For "webhook_received", we are at the start.
            # Let's try to commit. If it fails, we catch it.
            await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            # Do not raise exception
