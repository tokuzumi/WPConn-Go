import asyncio
import aiohttp
import sys
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import sessionmaker
from app.db.models import Tenant

# Configs
BASE_URL = "http://127.0.0.1:8000/api/v1"
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/wpp_connect"

async def verify_auth_flow():
    # Setup DB connection to fetch API Key
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with aiohttp.ClientSession() as session:
        # 1. Create Tenant
        print("1. Creating Tenant...")
        tenant_data = {
            "name": "Auth Test Company",
            "waba_id": str(uuid.uuid4()),
            "phone_number_id": str(uuid.uuid4()),
            "token": "auth_token"
        }
        
        tenant_id = None
        api_key = None
        
        async with session.post(f"{BASE_URL}/tenants/", json=tenant_data) as response:
            if response.status == 201:
                data = await response.json()
                tenant_id = data["id"]
                print(f"   Tenant created: {tenant_id}")
                
                # Fetch API Key from DB
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
                    tenant = result.scalars().first()
                    api_key = tenant.api_key
                    print(f"   API Key fetched from DB: {api_key}")
            else:
                print(f"   Failed to create tenant: {response.status}")
                sys.exit(1)

        # 2. Test Send Message WITHOUT Key
        print("\n2. Testing Send Message WITHOUT Key...")
        message_data = {
            "to_number": "5511999999999",
            "content": "Auth Test Message No Key"
        }
        async with session.post(f"{BASE_URL}/messages/send", json=message_data) as response:
            if response.status == 403 or response.status == 401: # FastAPI returns 403 for missing header usually, or 422 if required
                print(f"   Success: Request rejected as expected ({response.status})")
            else:
                print(f"   Fail: Unexpected status {response.status}")
                sys.exit(1)

        # 3. Test Send Message WITH INVALID Key
        print("\n3. Testing Send Message WITH INVALID Key...")
        headers = {"x-api-key": "invalid_key_123"}
        async with session.post(f"{BASE_URL}/messages/send", json=message_data, headers=headers) as response:
            if response.status == 401:
                print(f"   Success: Request rejected as expected (401)")
            else:
                print(f"   Fail: Unexpected status {response.status}")
                sys.exit(1)

        # 4. Test Send Message WITH VALID Key
        print("\n4. Testing Send Message WITH VALID Key...")
        headers = {"x-api-key": api_key}
        async with session.post(f"{BASE_URL}/messages/send", json=message_data, headers=headers) as response:
            if response.status == 201:
                print(f"   Success: Request accepted (201)")
                data = await response.json()
                print(f"   Message ID: {data['id']}")
            else:
                print(f"   Fail: Failed to send message {response.status} - {await response.text()}")
                sys.exit(1)

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_auth_flow())
