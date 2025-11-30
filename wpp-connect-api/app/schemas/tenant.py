from pydantic import BaseModel, UUID4
from datetime import datetime

class TenantCreate(BaseModel):
    name: str
    waba_id: str
    phone_number_id: str
    token: str
    webhook_url: str | None = None

class TenantResponse(BaseModel):
    id: UUID4
    name: str
    waba_id: str
    phone_number_id: str
    webhook_url: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
