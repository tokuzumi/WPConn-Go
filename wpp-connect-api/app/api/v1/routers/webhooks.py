from fastapi import APIRouter, Request, Response, BackgroundTasks, Depends, HTTPException, status
from app.core.config import settings
from app.core.security import verify_webhook_signature
from app.services.webhook_service import WebhookService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def verify_webhook(
    request: Request
):
    # Query params are accessed via request.query_params
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
            logger.info("Webhook verified successfully")
            return Response(content=challenge, media_type="text/plain")
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Verification failed"
            )
    
    # If params are missing, just return 200 or 400? Meta expects 200 for health check sometimes, 
    # but strictly for verification it sends params.
    return Response(content="Webhook Endpoint", media_type="text/plain")

from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.log_service import AuditLogger

from app.db.models import WebhookEvent

@router.post("/")
async def receive_webhook(
    request: Request,
    authorized: bool = Depends(verify_webhook_signature),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = await request.json()
        
        # Log raw payload (AuditLogger might be redundant but keeping for consistency if needed, 
        # but WebhookEvent is the main storage now. Let's keep it for now or remove if double storage is bad. 
        # The user said "O endpoint deve APENAS inserir o payload cru...". 
        # I will keep AuditLogger as it logs to a different table for audit purposes, but maybe it's better to remove to be strictly "APENAS".
        # Let's remove AuditLogger call here to be fast and atomic on WebhookEvent.)
        
        # Create WebhookEvent
        event = WebhookEvent(payload=payload, status='pending')
        db.add(event)
        await db.commit()
        
        return Response(content="EVENT_RECEIVED", status_code=200)
    except Exception as e:
        logger.error(f"Error receiving webhook: {e}")
        # If DB fails, we return 500 or 200? Meta retries on 500.
        # If we can't save to DB, we should probably return 500 so Meta retries later.
        # But the original code returned 200 even on error.
        # I will return 500 to signal failure to Meta if we can't persist.
        return Response(content="ERROR_SAVING_EVENT", status_code=500)
