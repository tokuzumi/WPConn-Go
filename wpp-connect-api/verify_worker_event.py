import asyncio
import logging
from sqlalchemy import select, text
from app.db.session import AsyncSessionLocal
from app.db.models import WebhookEvent, Message
from app.worker.main import process_events

# Configure logging to see worker output
logging.basicConfig(level=logging.INFO)

async def verify_worker():
    print("Verifying Worker Event Processing...")
    
    # Ensure there is a pending event (from previous test or create new one)
    async with AsyncSessionLocal() as db:
        query = select(WebhookEvent).where(WebhookEvent.status == 'pending').limit(1)
        result = await db.execute(query)
        event = result.scalars().first()
        
        if not event:
            print("No pending event found. Creating one...")
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
                                        "phone_number_id": "123456123" # Valid Tenant ID
                                    },
                                    "messages": [
                                        {
                                            "from": "5511999999999",
                                            "id": "wamid.HBgMTEST_WORKER_123",
                                            "timestamp": "1672531200",
                                            "text": {
                                                "body": "Test Worker Processing"
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
            event = WebhookEvent(payload=payload, status='pending')
            db.add(event)
            await db.commit()
            print(f"Created event {event.id}")
        else:
            print(f"Using existing pending event {event.id}")

    # Run worker for 5 seconds
    print("Running worker for 5 seconds...")
    try:
        await asyncio.wait_for(process_events(), timeout=5.0)
    except asyncio.TimeoutError:
        print("Worker stopped (timeout).")
    except Exception as e:
        print(f"Worker error: {e}")

    # Verify DB
    async with AsyncSessionLocal() as db:
        # Check event status
        # We need to find the event we used/created. 
        # If we created one, we have the ID. If we picked one, we have the ID.
        # But 'event' object from previous session is detached.
        # Let's query by ID if we had it, or just check if ANY event is processed.
        # Ideally we track the specific event.
        
        # Let's just query the latest event.
        query = select(WebhookEvent).order_by(WebhookEvent.updated_at.desc()).limit(1)
        result = await db.execute(query)
        latest_event = result.scalars().first()
        
        if latest_event:
            print(f"Latest Event ID={latest_event.id}, Status={latest_event.status}")
            if latest_event.status == 'processed':
                print("SUCCESS: Event processed.")
            else:
                print(f"FAILURE: Event status is {latest_event.status}.")
                if latest_event.error_log:
                    print(f"Error Log: {latest_event.error_log}")
        
        # Check Message
        # The wamid was "wamid.HBgMTEST_WORKER_123" or "wamid.HBgMTEST12345"
        # Let's check for both or just list recent messages.
        query = select(Message).order_by(Message.created_at.desc()).limit(1)
        result = await db.execute(query)
        message = result.scalars().first()
        
        if message:
            print(f"Latest Message WAMID={message.wamid}, Content={message.content}")
            if "Test" in str(message.content) or "Test" in str(message.wamid):
                 print("SUCCESS: Message created.")
        else:
            print("FAILURE: No message found.")

if __name__ == "__main__":
    asyncio.run(verify_worker())
