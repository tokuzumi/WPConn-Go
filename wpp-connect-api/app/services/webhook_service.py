import logging
import json
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant, Message
from app.services.meta_client import MetaClient

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

                        # Webhook Forwarding (Messages Only)
                        if tenant.webhook_url:
                            try:
                                import httpx
                                # Prepare payload for external webhook
                                # We send the internal Message object structure or a simplified version
                                forward_payload = {
                                    "id": str(new_message.id),
                                    "wamid": wamid,
                                    "phone": from_number,
                                    "direction": "inbound",
                                    "type": msg_type,
                                    "status": status,
                                    "content": content,
                                    "media_url": media_url,
                                    "media_type": media_type,
                                    "caption": caption,
                                    "created_at": new_message.created_at.isoformat() if new_message.created_at else datetime.utcnow().isoformat()
                                }
                                
                                # Fire and forget (or log error)
                                # We use a short timeout to not block the worker too long
                                async with httpx.AsyncClient() as client:
                                    await client.post(
                                        tenant.webhook_url, 
                                        json=forward_payload, 
                                        timeout=5.0
                                    )
                                logger.info(f"Forwarded message {wamid} to {tenant.webhook_url}")
                            except Exception as e:
                                logger.error(f"Failed to forward message {wamid} to {tenant.webhook_url}: {e}")
                                from app.services.log_service import AuditLogger
                                await AuditLogger.log(
                                    db,
                                    "webhook_delivery_failed",
                                    {
                                        "error": str(e),
                                        "payload": forward_payload,
                                        "url": tenant.webhook_url
                                    },
                                    tenant_id=tenant.id
                                )

                await db.commit()

        except Exception as e:
            logger.error(f"Error processing webhook payload: {e}")
            raise e

    async def process_media(self, message: Message, db: AsyncSession):
        """
        Process media for a message in 'media_pending' status.
        Fetches the download URL from Meta and saves it directly.
        Does NOT download the binary content to MinIO.
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
            
            # Fetch URL from Meta
            download_url = await meta_client.get_media_url(message.meta_media_id)
            
            if download_url:
                # Save Meta URL directly
                message.media_url = download_url
                message.status = "received"
                logger.info(f"Media URL fetched for message {message.id}: {download_url}")
            else:
                logger.error(f"Could not get download URL for media {message.meta_media_id}")
                message.status = "failed"

        except Exception as e:
            logger.error(f"Error processing media for message {message.id}: {e}")
            raise e
