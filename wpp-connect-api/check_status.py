import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import WebhookEvent, Message

async def check_status():
    async with AsyncSessionLocal() as db:
        # Get latest event
        query = select(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(1)
        result = await db.execute(query)
        event = result.scalars().first()
        
        if event:
            print(f"Event ID: {event.id}")
            print(f"Status: {event.status}")
            print(f"Error Log: {event.error_log}")
            print(f"Retry Count: {event.retry_count}")
        else:
            print("No event found")

        # Get latest message
        query = select(Message).order_by(Message.created_at.desc()).limit(1)
        result = await db.execute(query)
        message = result.scalars().first()
        
        if message:
            print(f"Message WAMID: {message.wamid}")
            print(f"Message Status: {message.status}")
        else:
            print("No message found")

if __name__ == "__main__":
    asyncio.run(check_status())
