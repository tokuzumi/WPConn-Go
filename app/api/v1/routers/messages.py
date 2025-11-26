from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.db.models import Tenant, Message
from app.schemas.message import MessageSendRequest, MessageResponse
from app.services.whatsapp_client import WhatsAppClient
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    request: MessageSendRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Fetch Tenant
    query = select(Tenant).where(Tenant.id == request.tenant_id)
    result = await db.execute(query)
    tenant = result.scalars().first()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )

    # 2. Save Message (Pending)
    db_message = Message(
        tenant_id=tenant.id,
        wamid="pending", # Placeholder until we get response
        phone=request.to_number,
        direction="outbound",
        type="text",
        status="pending",
        content=request.content
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)

    # 3. Send via WhatsAppClient
    client = WhatsAppClient()
    try:
        response = await client.send_text_message(
            token=tenant.token,
            phone_number_id=tenant.phone_number_id,
            to_number=request.to_number,
            message_body=request.content
        )
        
        # 4. Success: Update status and wamid
        # Meta response example: 
        # {'messaging_product': 'whatsapp', 'contacts': [{'input': '...', 'wa_id': '...'}], 
        #  'messages': [{'id': 'wamid.HBgM...'}]}
        if 'messages' in response and len(response['messages']) > 0:
            wamid = response['messages'][0]['id']
            db_message.wamid = wamid
            db_message.status = "sent"
        else:
            # Fallback if structure is unexpected but no exception raised
            db_message.status = "sent" 
            
    except Exception as e:
        # 5. Error: Update status to failed
        logger.error(f"Failed to send message: {e}")
        db_message.status = "failed"
        # We don't raise HTTPException here to return the message object with failed status
        # allowing the client to know it was attempted but failed.
    
    await db.commit()
    await db.refresh(db_message)
    
    return db_message
