from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class MessageSendRequest(BaseModel):
    to_number: str
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    caption: Optional[str] = None

class MessageResponse(BaseModel):
    id: UUID4
    status: str
    wamid: Optional[str] = None
    phone: str
    direction: str
    type: str
    content: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    caption: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
