import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.db.models import WebhookEvent, Message
from app.worker.main import process_events, process_media

# Configure logging
logging.basicConfig(level=logging.INFO)

async def verify_media():
    print("Verifying Media Offloading...")
    
    # 1. Create Event with Media
    async with AsyncSessionLocal() as db:
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123456789",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "1234567890",
                                    "phone_number_id": "123456123"
                                },
                                "messages": [
                                    {
                                        "from": "5511999999999",
                                        "id": "wamid.MEDIA_TEST_123",
                                        "timestamp": "1672531200",
                                        "type": "image",
                                        "image": {
                                            "mime_type": "image/jpeg",
                                            "sha256": "...",
                                            "id": "MEDIA_ID_123",
                                            "caption": "Test Image"
                                        }
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        event = WebhookEvent(payload=payload, status='pending')
        db.add(event)
        await db.commit()
        print(f"Created media event {event.id}")

    # 2. Run Event Processor (should create message with media_pending)
    print("Running Event Processor...")
    try:
        await asyncio.wait_for(process_events(), timeout=5.0)
    except asyncio.TimeoutError:
        pass
    except Exception as e:
        print(f"Event Processor Error: {e}")

    # Verify Message Status
    async with AsyncSessionLocal() as db:
        query = select(Message).where(Message.wamid == "wamid.MEDIA_TEST_123")
        result = await db.execute(query)
        message = result.scalars().first()
        
        if message:
            print(f"Message Status after Event Processor: {message.status}")
            if message.status == 'media_pending':
                print("SUCCESS: Message is media_pending.")
            else:
                print(f"FAILURE: Message status is {message.status}.")
                return
        else:
            print("FAILURE: Message not created.")
            return

    # 3. Run Media Processor (should download/upload and update status)
    print("Running Media Processor with Mocks...")
    
    # Mock MetaClient and StorageService
    with patch("app.services.webhook_service.MetaClient") as MockMetaClient, \
         patch("app.services.webhook_service.StorageService") as MockStorageService:
        
        # Setup Mocks
        mock_meta = MockMetaClient.return_value
        mock_meta.get_media_url = AsyncMock(return_value="http://meta.com/media")
        
        # Mock stream context manager
        mock_stream = AsyncMock()
        mock_stream.__aenter__.return_value = AsyncMock() # The stream object
        mock_meta.get_media_stream.return_value = mock_stream
        
        mock_storage = MockStorageService.return_value
        mock_storage.upload_stream = AsyncMock(return_value="http://minio.com/media.jpg")
        
        try:
            await asyncio.wait_for(process_media(), timeout=10.0)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            print(f"Media Processor Error: {e}")

    # Verify Final Message Status
    async with AsyncSessionLocal() as db:
        query = select(Message).where(Message.wamid == "wamid.MEDIA_TEST_123")
        result = await db.execute(query)
        message = result.scalars().first()
        
        if message:
            print(f"Final Message Status: {message.status}")
            print(f"Media URL: {message.media_url}")
            
            if message.status == 'received' and message.media_url == "http://minio.com/media.jpg":
                print("SUCCESS: Media processed and URL updated.")
            else:
                print("FAILURE: Media processing failed.")

if __name__ == "__main__":
    asyncio.run(verify_media())
