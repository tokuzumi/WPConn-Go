import logging
import json
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant, Message
from app.services.storage_service import StorageService
from app.services.meta_client import MetaClient
from app.core.utils import AsyncIteratorToFileLike

logger = logging.getLogger(__name__)

class WebhookService:
    async def process_payload(self, payload: dict):
        try:
            # Basic validation of structure
            if not payload.get("entry"):
                return
            
            entry = payload["entry"][0]
            changes = entry.get("changes", [])
            
            if not changes:
                return

            value = changes[0].get("value", {})
            metadata = value.get("metadata", {})
            phone_number_id = metadata.get("phone_number_id")

            if not phone_number_id:
                logger.warning("Webhook payload missing phone_number_id")
                return

            async with AsyncSessionLocal() as db:
                # Find Tenant
                query = select(Tenant).where(Tenant.phone_number_id == phone_number_id)
                result = await db.execute(query)
                tenant = result.scalars().first()

                if not tenant:
                    logger.warning(f"Tenant not found for phone_number_id: {phone_number_id}")
                    return

                # Process Statuses
                if "statuses" in value:
                    for status_update in value["statuses"]:
                        wamid = status_update.get("id")
                        new_status = status_update.get("status")
                        
                        if wamid and new_status:
                            stmt = (
                                update(Message)
                                .where(Message.wamid == wamid)
                                .values(status=new_status)
                            )
                            await db.execute(stmt)
                            logger.info(f"Updated message {wamid} to status {new_status}")

                # Process Messages
                if "messages" in value:
                    
                    for msg in value["messages"]:
                        wamid = msg.get("id")
                        from_number = msg.get("from")
                        msg_type = msg.get("type")
                        
                        content = None
                        media_url = None
                        media_type = None
                        caption = None
                        meta_media_id = None
                        reply_to_wamid = None
                        status = "received"
                        
                        # Extract Context (Reply)
                        context = msg.get("context")
                        if context:
                            reply_to_wamid = context.get("id")

                        # Check if message already exists (idempotency)
                        exists_query = select(Message).where(Message.wamid == wamid)
                        exists_result = await db.execute(exists_query)
                        if exists_result.scalars().first():
                            continue

                        if msg_type == "text":
                            content = msg.get("text", {}).get("body")
                        elif msg_type in ["image", "video", "audio", "document", "sticker", "voice"]:
                            media_info = msg.get(msg_type, {})
                            meta_media_id = media_info.get("id")
                            mime_type = media_info.get("mime_type")
                            caption = media_info.get("caption")
                            media_type = mime_type
                            
                            # Media Offloading: Do NOT download here.
                            # Set status to media_pending
                            status = "media_pending"
                            
                        else:
                            # Store JSON for other types
                            content = json.dumps(msg)

                        new_message = Message(
                            tenant_id=tenant.id,
                            wamid=wamid,
                            phone=from_number,
                            direction="inbound",
                            type=msg_type,
                            status=status,
                            content=content,
                            media_url=media_url,
                            media_type=media_type,
                            caption=caption,
                            meta_media_id=meta_media_id,
                            reply_to_wamid=reply_to_wamid
                        )
                        db.add(new_message)
                        logger.info(f"Received new message {wamid} from {from_number} (Status: {status})")

                await db.commit()

        except Exception as e:
            logger.error(f"Error processing webhook payload: {e}")
            raise e

    async def process_media(self, message: Message, db: AsyncSession):
        """
        Process media for a message in 'media_pending' status.
        Downloads from Meta and uploads to MinIO.
        """
        try:
            if not message.meta_media_id:
                logger.warning(f"Message {message.id} has no meta_media_id")
                message.status = "failed"
                return
            
            # Eager load tenant or query it.
            if not message.tenant:
                 query = select(Tenant).where(Tenant.id == message.tenant_id)
                 result = await db.execute(query)
                 tenant = result.scalars().first()
                 if not tenant:
                     logger.error(f"Tenant not found for message {message.id}")
                     message.status = "failed"
                     return
            else:
                tenant = message.tenant

            meta_client = MetaClient(tenant.token, tenant.phone_number_id)
            storage_service = StorageService()
            
            download_url = await meta_client.get_media_url(message.meta_media_id)
            
            if download_url:
                async with meta_client.get_media_stream(download_url) as stream:
                    if stream:
                        # Determine extension
                        mime_type = message.media_type
                        ext = mime_type.split("/")[-1] if mime_type else "bin"
                        if ";" in ext: ext = ext.split(";")[0]
                        
                        # Create object name: {tenant_id}/{year}/{month}/{media_id}.{ext}
                        now = datetime.utcnow()
                        object_name = f"{tenant.id}/{now.year}/{now.month:02d}/{message.meta_media_id}.{ext}"
                        
                        wrapped_stream = AsyncIteratorToFileLike(stream)
                        media_url = await storage_service.upload_stream(
                            wrapped_stream, 
                            object_name, 
                            mime_type
                        )
                        
                        message.media_url = media_url
                        message.status = "received"
                        logger.info(f"Media processed for message {message.id}: {media_url}")
            else:
                logger.error(f"Could not get download URL for media {message.meta_media_id}")
                message.status = "failed"

        except Exception as e:
            logger.error(f"Error processing media for message {message.id}: {e}")
            raise e
