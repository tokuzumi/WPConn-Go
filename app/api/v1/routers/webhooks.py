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

@router.post("/")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    # Signature verification dependency
    authorized: bool = Depends(verify_webhook_signature) 
):
    try:
        # We need to parse JSON here. 
        # Note: verify_webhook_signature already consumed the body stream, 
        # but FastAPI/Starlette caches it so await request.json() works.
        payload = await request.json()
        
        service = WebhookService()
        background_tasks.add_task(service.process_payload, payload)
        
        return Response(content="EVENT_RECEIVED", status_code=200)
    except Exception as e:
        logger.error(f"Error receiving webhook: {e}")
        # Always return 200 to Meta to avoid retries if it's an internal error we can't fix immediately
        return Response(content="EVENT_RECEIVED", status_code=200)
