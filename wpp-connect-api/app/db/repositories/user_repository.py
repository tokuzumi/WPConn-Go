from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User
from typing import Optional
import uuid

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_users(self, limit: int = 50, offset: int = 0) -> list[User]:
        query = select(User).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_user(self, user_data: dict) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: str) -> bool:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
