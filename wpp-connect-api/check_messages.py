import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models import Message
from app.services.log_service import AuditLog
from sqlalchemy import select, desc

async def main():
    async with AsyncSessionLocal() as db:
        # Check Messages
        print("--- Messages ---")
        result = await db.execute(select(Message).order_by(desc(Message.created_at)).limit(5))
        messages = result.scalars().all()
        if not messages:
            print("No messages found.")
        for m in messages:
            print(f"Time: {m.created_at}, From: {m.phone}, Content: {m.content}, Status: {m.status}")

        # Check Audit Logs
        print("\n--- Audit Logs ---")
        result = await db.execute(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(5))
        logs = result.scalars().all()
        if not logs:
            print("No audit logs found.")
        for l in logs:
            print(f"Time: {l.created_at}, Event: {l.event}, Detail: {l.detail}")

if __name__ == "__main__":
    asyncio.run(main())
