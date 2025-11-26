import asyncio
import aiohttp
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1/tenants"

async def verify_tenant_flow():
    tenant_data = {
        "name": "Test Company",
        "waba_id": str(uuid.uuid4()),
        "phone_number_id": str(uuid.uuid4()),
        "token": "secret_token_123"
    }

    async with aiohttp.ClientSession() as session:
        # 1. Create Tenant
        print(f"Creating tenant with data: {tenant_data}")
        async with session.post(BASE_URL + "/", json=tenant_data) as response:
            if response.status == 201:
                data = await response.json()
                print(f"Tenant created successfully: {data}")
                assert data["name"] == tenant_data["name"]
                assert "id" in data
                assert "token" not in data  # Token should not be returned
            else:
                print(f"Failed to create tenant: {response.status} - {await response.text()}")
                sys.exit(1)

        # 2. Try to create duplicate Tenant
        print("Attempting to create duplicate tenant...")
        async with session.post(BASE_URL + "/", json=tenant_data) as response:
            if response.status == 409:
                print("Duplicate check passed (409 Conflict received).")
            else:
                print(f"Duplicate check failed: Expected 409, got {response.status}")
                sys.exit(1)

        # 3. List Tenants
        print("Listing tenants...")
        async with session.get(BASE_URL + "/") as response:
            if response.status == 200:
                data = await response.json()
                print(f"Tenants list: {len(data)} tenants found.")
                found = any(t["waba_id"] == tenant_data["waba_id"] for t in data)
                if found:
                    print("Created tenant found in list.")
                else:
                    print("Created tenant NOT found in list.")
                    sys.exit(1)
            else:
                print(f"Failed to list tenants: {response.status}")
                sys.exit(1)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_tenant_flow())
