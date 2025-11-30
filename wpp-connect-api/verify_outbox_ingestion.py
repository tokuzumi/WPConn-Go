import asyncio
import json
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import verify_webhook_signature
from app.db.session import AsyncSessionLocal
from app.db.models import WebhookEvent
from sqlalchemy import select, text

# Override dependency to bypass signature verification
app.dependency_overrides[verify_webhook_signature] = lambda: True

async def verify_ingestion():
    print("Verifying Outbox Ingestion (Async)...")
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
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
                                    "phone_number_id": "103782649406562"
                                },
                                "messages": [
                                    {
                                        "from": "5511999999999",
                                        "id": "wamid.HBgMTEST12345",
                                        "timestamp": "1672531200",
                                        "text": {
                                            "body": "Test Outbox Ingestion"
                                        },
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }

        response = await client.post("/api/v1/webhooks/", json=payload)
        
        if response.status_code == 200:
            print("Response: 200 OK")
        else:
            print(f"Response: {response.status_code} - {response.text}")
            return

    # Verify DB
    async with AsyncSessionLocal() as db:
        query = select(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(1)
        result = await db.execute(query)
        event = result.scalars().first()
        
        if event:
            print(f"Event found: ID={event.id}, Status={event.status}")
            if event.status == 'pending':
                print("SUCCESS: Event persisted with status 'pending'.")
            else:
                print(f"FAILURE: Event status is {event.status}, expected 'pending'.")
        else:
            print("FAILURE: No event found in DB.")

if __name__ == "__main__":
    asyncio.run(verify_ingestion())
