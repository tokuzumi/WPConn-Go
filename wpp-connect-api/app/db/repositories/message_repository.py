from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_
from app.db.models import Message
from typing import Optional

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_messages(
        self, 
        tenant_id: Optional[str] = None, 
        limit: int = 50, 
        offset: int = 0,
        phone: Optional[str] = None,
        search: Optional[str] = None
    ) -> list[Message]:
        query = select(Message)
        
        if tenant_id:
            query = query.where(Message.tenant_id == tenant_id)
        
        if phone:
            query = query.where(Message.phone.ilike(f"%{phone}%"))
            
        if search:
            query = query.where(
                or_(
                    Message.content.ilike(f"%{search}%"),
                    Message.wamid.ilike(f"%{search}%"),
                    Message.caption.ilike(f"%{search}%")
                )
            )
            
        query = query.order_by(desc(Message.created_at)).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, message_id: str, tenant_id: Optional[str] = None) -> Optional[Message]:
        query = select(Message).where(Message.id == message_id)
        if tenant_id:
            query = query.where(Message.tenant_id == tenant_id)
        result = await self.db.execute(query)
        return result.scalars().first()
