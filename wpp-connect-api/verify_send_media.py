import asyncio
import logging
from unittest.mock import MagicMock, AsyncMock, patch
from app.api.v1.routers.messages import send_message
from app.schemas.message import MessageSendRequest
from app.db.session import AsyncSessionLocal
from app.db.models import Tenant, Message
from sqlalchemy import select, delete

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

async def verify_send_media():
    # 1. Setup Test Data
    tenant_id = None
    media_url = "bucket/test_image.jpg"
    meta_media_id = "media.123"
    
    # Mock Tenant
    mock_tenant = MagicMock(spec=Tenant)
    mock_tenant.id = "12345678-1234-5678-1234-567812345678"
    mock_tenant.token = "token"
    mock_tenant.phone_number_id = "123456123"

    # Mock Request
    request = MessageSendRequest(
        to_number="5511999999999",
        media_url=media_url,
        media_type="image",
        caption="Test Caption"
    )

    # 2. Mock Services
    with patch("app.api.v1.routers.messages.MetaClient") as MockMetaClient, \
         patch("app.api.v1.routers.messages.StorageService") as MockStorageService:
        
        # Mock MetaClient
        meta_instance = MockMetaClient.return_value
        meta_instance.upload_media = AsyncMock(return_value=meta_media_id)
        meta_instance.send_message = AsyncMock(return_value={"messages": [{"id": "wamid.sent"}]})

        # Mock StorageService
        storage_instance = MockStorageService.return_value
        storage_instance.get_stream = AsyncMock(return_value=AsyncMock()) # Mock stream

        # 3. Run Send Message (First Time - Upload)
        print("\n--- Test 1: First Send (Upload) ---")
        async with AsyncSessionLocal() as db:
            # Ensure clean state
            # We can't easily delete by media_url if tenant_id is mocked uuid, 
            # so let's just rely on mocks and db rollback or unique test data.
            # Ideally we should use a real tenant from DB or mock db session completely.
            # Let's use real DB session but mock tenant object.
            # Wait, we need a valid tenant_id for FK constraints if we insert into DB.
            # So we must fetch a real tenant.
            
            real_tenant = (await db.execute(select(Tenant))).scalars().first()
            if not real_tenant:
                print("FAILURE: No tenant found in DB")
                return

            # Update mock tenant ID to real one
            mock_tenant.id = real_tenant.id
            mock_tenant.token = real_tenant.token
            mock_tenant.phone_number_id = real_tenant.phone_number_id

            # Call endpoint function directly
            response = await send_message(request, db, mock_tenant)
            
            print(f"Status: {response.status}")
            print(f"Meta Media ID: {response.meta_media_id}")
            
            if response.meta_media_id == meta_media_id:
                print("SUCCESS: Media ID saved")
            else:
                print("FAILURE: Media ID mismatch")

            if meta_instance.upload_media.called:
                print("SUCCESS: upload_media called")
            else:
                print("FAILURE: upload_media NOT called")

        # 4. Run Send Message (Second Time - Cache)
        print("\n--- Test 2: Second Send (Cache) ---")
        async with AsyncSessionLocal() as db:
            # Reset mocks
            meta_instance.upload_media.reset_mock()
            
            # Call endpoint again
            response = await send_message(request, db, mock_tenant)
            
            print(f"Status: {response.status}")
            print(f"Meta Media ID: {response.meta_media_id}")
            
            if not meta_instance.upload_media.called:
                print("SUCCESS: upload_media NOT called (Cache Hit)")
            else:
                print("FAILURE: upload_media called (Cache Miss)")

            # Cleanup
            # Delete messages created
            stmt = delete(Message).where(Message.media_url == media_url)
            await db.execute(stmt)
            await db.commit()

if __name__ == "__main__":
    asyncio.run(verify_send_media())
