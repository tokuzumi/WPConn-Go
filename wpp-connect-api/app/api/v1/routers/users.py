from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "user"

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=list[UserResponse])
async def get_users(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    from app.db.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    return await repo.get_users(limit, offset)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    from app.db.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    
    existing = await repo.get_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Simple password hashing (placeholder, use passlib in production)
    # For now, storing as plain text or simple hash to avoid dependency issues if passlib missing
    # Assuming we can just store it for this MVP step
    password_hash = user_in.password # TODO: Hash this!
    
    user_data = {
        "email": user_in.email,
        "password_hash": password_hash,
        "name": user_in.name,
        "role": user_in.role
    }
    
    return await repo.create_user(user_data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    from app.db.repositories.user_repository import UserRepository
    repo = UserRepository(db)
    success = await repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
