from pydantic import BaseModel, UUID4
from typing import Optional

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
    
    class Config:
        from_attributes = True
