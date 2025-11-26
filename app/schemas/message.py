from pydantic import BaseModel, UUID4
from typing import Optional

class MessageSendRequest(BaseModel):
    tenant_id: UUID4
    to_number: str
    content: str

class MessageResponse(BaseModel):
    id: UUID4
    status: str
    wamid: Optional[str] = None
    
    class Config:
        from_attributes = True
