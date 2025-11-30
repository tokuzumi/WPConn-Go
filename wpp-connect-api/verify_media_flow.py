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

async def verify_media_flow():
    # 1. Setup Test Data
    phone_number_id = "123456123"
    wamid = "wamid.test.media"
    media_id = "media.123"
    
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
                        "type": "image",
                        "image": {
                            "mime_type": "image/jpeg",
                            "sha256": "hash",
                            "id": media_id,
                            "caption": "Test Image"
                        }
                    }]
                }
            }]
        }]
    }

    # 2. Mock Services
    with patch("app.services.webhook_service.MetaClient") as MockMetaClient, \
         patch("app.services.webhook_service.StorageService") as MockStorageService:
        
        # Mock MetaClient instance
        meta_instance = MockMetaClient.return_value
        meta_instance.get_media_url = AsyncMock(return_value="http://meta.com/media.jpg")
        
        from contextlib import asynccontextmanager

        # Mock get_media_stream context manager
        @asynccontextmanager
        async def mock_stream_cm(url):
            yield AsyncMock() # Yields a mock iterator
        meta_instance.get_media_stream = mock_stream_cm

        # Mock StorageService instance
        storage_instance = MockStorageService.return_value
        storage_instance.upload_stream = AsyncMock(return_value="bucket/media.jpg")

        # 3. Run Service
        service = WebhookService()
        await service.process_payload(payload)

        # 4. Verify Database
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Message).where(Message.wamid == wamid))
            message = result.scalars().first()
            
            if message:
                print("SUCCESS: Message saved to DB")
                print(f"Media URL: {message.media_url}")
                print(f"Media Type: {message.media_type}")
                print(f"Caption: {message.caption}")
                print(f"Meta Media ID: {message.meta_media_id}")
                
                # Cleanup
                await db.delete(message)
                await db.commit()
                
                # Verify Mocks
                print(f"Meta get_media_url called: {meta_instance.get_media_url.called}")
                # print(f"Meta get_media_stream called: {meta_instance.get_media_stream.called}") # Cannot check called on decorated func
                print(f"Storage upload_stream called: {storage_instance.upload_stream.called}")
                
            else:
                print("FAILURE: Message not found in DB")

if __name__ == "__main__":
    asyncio.run(verify_media_flow())
