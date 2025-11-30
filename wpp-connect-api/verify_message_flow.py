import asyncio
import aiohttp
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def verify_message_flow():
    # 1. Create a Tenant first
    tenant_data = {
        "name": "Message Test Company",
        "waba_id": str(uuid.uuid4()),
        "phone_number_id": str(uuid.uuid4()),
        "token": "invalid_token_for_test"
    }
    
    tenant_id = None

    async with aiohttp.ClientSession() as session:
        print(f"Creating tenant for message test...")
        async with session.post(f"{BASE_URL}/tenants/", json=tenant_data) as response:
            if response.status == 201:
                data = await response.json()
                tenant_id = data["id"]
                print(f"Tenant created: {tenant_id}")
            else:
                print(f"Failed to create tenant: {response.status}")
                sys.exit(1)

        # 2. Send Message
        message_data = {
            "tenant_id": tenant_id,
            "to_number": "5511999999999",
            "content": "Hello World from API"
        }
        
        print(f"Sending message...")
        async with session.post(f"{BASE_URL}/messages/send", json=message_data) as response:
            if response.status == 201:
                data = await response.json()
                print(f"Message response: {data}")
                
                # Expecting 'failed' status because credentials are invalid
                if data["status"] == "failed":
                    print("Test Passed: Message saved with status 'failed' as expected (invalid credentials).")
                elif data["status"] == "sent":
                     print("Unexpected: Message status is 'sent' (Mocking active?).")
                else:
                    print(f"Unexpected status: {data['status']}")
            else:
                print(f"Failed to send message: {response.status} - {await response.text()}")
                sys.exit(1)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_message_flow())
