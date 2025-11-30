import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.webhook_service import WebhookService
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant, Message
from sqlalchemy import select, delete

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_reply_flow():
    # 1. Setup Test Data
    phone_number_id = "123456123"
    wamid = "wamid.test.reply"
    reply_to_wamid = "wamid.original.message"
    
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {
                        "phone_number_id": phone_number_id
                    },
                    "messages": [{
                        "from": "5511999999999",
                        "id": wamid,
                        "type": "text",
                        "text": {
                            "body": "This is a reply"
                        },
                        "context": {
                            "id": reply_to_wamid
                        }
                    }]
                }
            }]
        }]
    }

    # 2. Run Service (No need to mock Meta/Storage for text messages)
    service = WebhookService()
    await service.process_payload(payload)

    # 3. Verify Database
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Message).where(Message.wamid == wamid))
        message = result.scalars().first()
        
        if message:
            print("SUCCESS: Reply message saved to DB")
            print(f"WAMID: {message.wamid}")
            print(f"Content: {message.content}")
            print(f"Reply To: {message.reply_to_wamid}")
            
            if message.reply_to_wamid == reply_to_wamid:
                print("VERIFICATION PASSED: Reply ID matches")
            else:
                print(f"VERIFICATION FAILED: Expected {reply_to_wamid}, got {message.reply_to_wamid}")

            # Cleanup
            await db.delete(message)
            await db.commit()
        else:
            print("FAILURE: Message not found in DB")

if __name__ == "__main__":
    asyncio.run(verify_reply_flow())
