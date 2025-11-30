import asyncio
import aiohttp
import sys
import uuid
import hmac
import hashlib
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Configs
BASE_URL = "http://127.0.0.1:8000/api/v1"
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/wpp_connect"
APP_SECRET = "seu_app_secret_aqui"

async def verify_audit_logs():
    # Setup DB connection for verification
    engine = create_async_engine(DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with aiohttp.ClientSession() as session:
        # 1. Trigger 'tenant_created'
        print("1. Triggering 'tenant_created'...")
        tenant_data = {
            "name": "Audit Test Company",
            "waba_id": str(uuid.uuid4()),
            "phone_number_id": str(uuid.uuid4()),
            "token": "audit_token"
        }
        tenant_id = None
        async with session.post(f"{BASE_URL}/tenants/", json=tenant_data) as response:
            if response.status == 201:
                data = await response.json()
                tenant_id = data["id"]
                print("   Tenant created.")
            else:
                print(f"   Failed to create tenant: {response.status}")
                sys.exit(1)

        # 2. Trigger 'message_send_failed'
        print("2. Triggering 'message_send_failed'...")
        message_data = {
            "tenant_id": tenant_id,
            "to_number": "5511999999999",
            "content": "Audit Test Message"
        }
        # This should fail because token is invalid, triggering the log
        async with session.post(f"{BASE_URL}/messages/send", json=message_data) as response:
            print(f"   Message request status: {response.status}")

        # 3. Trigger 'webhook_received'
        print("3. Triggering 'webhook_received'...")
        payload = {"test": "audit_webhook", "random": str(uuid.uuid4())}
        body = json.dumps(payload).encode()
        signature = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
        headers = {"X-Hub-Signature-256": f"sha256={signature}"}
        
        async with session.post(f"{BASE_URL}/webhooks/", data=body, headers=headers) as response:
            if response.status == 200:
                print("   Webhook sent.")
            else:
                print(f"   Webhook failed: {response.status}")

    # 4. Verify Logs in DB
    print("\n4. Verifying logs in Database...")
    await asyncio.sleep(2) # Wait for async operations
    
    async with AsyncSessionLocal() as db:
        # Check tenant_created
        result = await db.execute(text("SELECT count(*) FROM audit_logs WHERE event = 'tenant_created'"))
        count = result.scalar()
        print(f"   'tenant_created' logs found: {count}")
        if count == 0:
            print("   FAIL: 'tenant_created' log not found.")
            sys.exit(1)

        # Check message_send_failed
        result = await db.execute(text("SELECT count(*) FROM audit_logs WHERE event = 'message_send_failed'"))
        count = result.scalar()
        print(f"   'message_send_failed' logs found: {count}")
        if count == 0:
            print("   FAIL: 'message_send_failed' log not found.")
            sys.exit(1)

        # Check webhook_received
        result = await db.execute(text("SELECT count(*) FROM audit_logs WHERE event = 'webhook_received'"))
        count = result.scalar()
        print(f"   'webhook_received' logs found: {count}")
        if count == 0:
            print("   FAIL: 'webhook_received' log not found.")
            sys.exit(1)
            
    print("\nSUCCESS: All audit logs verified.")
    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_audit_logs())
