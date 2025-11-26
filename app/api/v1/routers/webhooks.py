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

@router.post("/")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    authorized: bool = Depends(verify_webhook_signature),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = await request.json()
        
        # Log raw payload
        await AuditLogger.log(db, "webhook_received", payload)
        
        service = WebhookService()
        background_tasks.add_task(service.process_payload, payload)
        
        return Response(content="EVENT_RECEIVED", status_code=200)
    except Exception as e:
        logger.error(f"Error receiving webhook: {e}")
        # Log error if possible, though db might be closed or issue might be related to db
        # We can try logging the error too
        try:
             await AuditLogger.log(db, "webhook_error", str(e))
        except:
             pass
        return Response(content="EVENT_RECEIVED", status_code=200)
