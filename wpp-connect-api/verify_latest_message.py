import asyncio
import logging
from app.db.session import AsyncSessionLocal
from app.db.models import Message
from sqlalchemy import select, desc

# Disable sqlalchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Message).order_by(desc(Message.created_at)).limit(1))
        message = result.scalars().first()
        
        if message:
            print(f"SUCCESS_MESSAGE_FOUND")
            print(f"ID: {message.id}")
            print(f"From: {message.phone}")
            print(f"Content: {message.content}")
            print(f"Status: {message.status}")
            print(f"WAMID: {message.wamid}")
        else:
            print("NO_MESSAGES_FOUND")

if __name__ == "__main__":
    asyncio.run(main())
