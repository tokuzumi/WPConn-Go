import logging
import json
from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant, Message

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
                        if msg_type == "text":
                            content = msg.get("text", {}).get("body")
                        else:
                            # Store JSON for other types
                            content = json.dumps(msg)

                        # Check if message already exists (idempotency)
                        exists_query = select(Message).where(Message.wamid == wamid)
                        exists_result = await db.execute(exists_query)
                        if exists_result.scalars().first():
                            continue

                        new_message = Message(
                            tenant_id=tenant.id,
                            wamid=wamid,
                            phone=from_number,
                            direction="inbound",
                            type=msg_type,
                            status="received",
                            content=content
                        )
                        db.add(new_message)
                        logger.info(f"Received new message {wamid} from {from_number}")

                await db.commit()

        except Exception as e:
            logger.error(f"Error processing webhook payload: {e}")
