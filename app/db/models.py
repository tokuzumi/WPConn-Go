import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    waba_id = Column(String, unique=True, nullable=False)
    phone_number_id = Column(String, unique=True, nullable=False)
    token = Column(String, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    wamid = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=False)
    direction = Column(Enum('inbound', 'outbound', name='message_direction'), nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    
    # Media fields
    media_url = Column(String, index=True, nullable=True)
    media_type = Column(String, nullable=True)
    caption = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    meta_media_id = Column(String, index=True, nullable=True)
    
    # Context
    reply_to_wamid = Column(String, index=True, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="messages")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    event = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="audit_logs")
