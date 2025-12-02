from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Tenant, Message
from app.schemas.message import MessageSendRequest, MessageResponse
from app.services.log_service import AuditLogger
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

from app.api.deps import get_current_tenant

from app.services.meta_client import MetaClient
from app.services.storage_service import StorageService
from app.core.utils import AsyncIteratorToFileLike

@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: MessageSendRequest,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    # 1. Prepare Message Data
    meta_media_id = None
    media_url = request.media_url
    media_type = request.media_type
    caption = request.caption
    content = request.content

    # 2. Handle Media Logic
    if media_url:
        # Check Cache (Reuse meta_media_id)
        # We look for ANY message that has the same media_url and a valid meta_media_id
        query = select(Message).where(
            Message.media_url == media_url,
            Message.meta_media_id.isnot(None)
        ).limit(1)
        result = await db.execute(query)
        cached_message = result.scalars().first()

        if cached_message:
            meta_media_id = cached_message.meta_media_id
            logger.info(f"Cache HIT for media {media_url}. Reusing ID: {meta_media_id}")
        else:
            logger.info(f"Cache MISS for media {media_url}. Uploading to Meta...")
            try:
                storage_service = StorageService()
                meta_client = MetaClient(tenant.token, tenant.phone_number_id)
                
                # Determine MIME type
                mime_type = "application/octet-stream"
                if media_type == "image": mime_type = "image/jpeg"
                elif media_type == "video": mime_type = "video/mp4"
                elif media_type == "audio": mime_type = "audio/mpeg"
                elif media_type == "document": mime_type = "application/pdf"

                # Check if URL is public (http/https) or internal (MinIO)
                if media_url.startswith("http"):
                    # Public URL: Download and stream to Meta
                    import httpx
                    async with httpx.AsyncClient() as client:
                        async with client.stream("GET", media_url) as response:
                            if response.status_code == 200:
                                # We need to pass the stream to upload_media
                                # Note: upload_media expects a file-like object or bytes.
                                # httpx stream yields bytes. We might need to read it all into memory 
                                # if upload_media doesn't support async generator.
                                # For simplicity and robust testing, let's read it.
                                # (Limit size in production, but fine for test)
                                file_content = await response.aread()
                                meta_media_id = await meta_client.upload_media(file_content, mime_type)
                            else:
                                raise HTTPException(status_code=400, detail=f"Failed to download media from URL: {response.status_code}")
                else:
                    # MinIO Path
                    stream = await storage_service.get_stream(media_url)
                    meta_media_id = await meta_client.upload_media(stream, mime_type)
                
                if not meta_media_id:
                    raise HTTPException(status_code=500, detail="Failed to upload media to Meta")
                    
            except Exception as e:
                logger.error(f"Error uploading media: {e}")
                raise HTTPException(status_code=500, detail=f"Media upload failed: {e}")

    # 3. Save Message (Pending)
    db_message = Message(
        tenant_id=tenant.id,
        wamid="pending",
        phone=request.to_number,
        direction="outbound",
        type=media_type if media_type else "text",
        status="pending",
        content=content,
        media_url=media_url,
        media_type=media_type,
        caption=caption,
        meta_media_id=meta_media_id
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)

    # 4. Send via MetaClient
    meta_client = MetaClient(tenant.token, tenant.phone_number_id)
    
    payload = {
        "messaging_product": "whatsapp",
        "to": request.to_number,
    }

    if media_type:
        payload["type"] = media_type
        payload[media_type] = {"id": meta_media_id}
        if caption:
            payload[media_type]["caption"] = caption
    else:
        payload["type"] = "text"
        payload["text"] = {"body": content}

    try:
        response = await meta_client.send_message(payload)
        
        if response and 'messages' in response and len(response['messages']) > 0:
            wamid = response['messages'][0]['id']
            db_message.wamid = wamid
            db_message.status = "sent"
        else:
            db_message.status = "failed" # Or sent if we trust 200 OK without body
            if response:
                 logger.error(f"Unexpected response from Meta: {response}")
            
            await AuditLogger.log(
                db, 
                "message_send_failed", 
                {"error": f"Meta Error: {response}", "message_id": str(db_message.id)},
                tenant_id=tenant.id
            )
            
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        db_message.status = "failed"
        await AuditLogger.log(
            db, 
            "message_send_failed", 
            {"error": str(e), "message_id": str(db_message.id)},
            tenant_id=tenant.id
        )
    
    await db.commit()
    await db.refresh(db_message)
    
    await db.refresh(db_message)
    
    return db_message

@router.get("/", response_model=list[MessageResponse])
async def get_messages(
    limit: int = 50,
    offset: int = 0,
    phone: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant)
):
    from app.db.repositories.message_repository import MessageRepository
    repo = MessageRepository(db)
    tenant_id = None if tenant.id == "admin" else str(tenant.id)
    return await repo.get_messages(tenant_id, limit, offset, phone, search)
