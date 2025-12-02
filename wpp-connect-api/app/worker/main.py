import asyncio
import os
import logging
import traceback
from datetime import datetime
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.db.models import WebhookEvent, Message
from app.services.webhook_service import WebhookService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_events():
    logger.info("Starting Event Processor Loop")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Fetch pending events with locking
                query = (
                    select(WebhookEvent)
                    .where(WebhookEvent.status == 'pending')
                    .order_by(WebhookEvent.created_at.asc())
                    .limit(int(os.getenv("WORKER_BATCH_SIZE", "50")))
                    .with_for_update(skip_locked=True)
                )
                
                result = await db.execute(query)
                events = result.scalars().all()
                
                if not events:
                    # print("No pending events found.")
                    await asyncio.sleep(1)
                    continue
                
                logger.info(f"Processing {len(events)} events")
                
                service = WebhookService()
                
                for event in events:
                    # print(f"Processing event {event.id}")
                    try:
                        await service.process_payload(event.payload)
                        
                        event.status = 'processed'
                        event.updated_at = datetime.utcnow()
                        
                    except Exception as e:
                        logger.error(f"Error processing event {event.id}: {e}")
                        traceback.print_exc()
                        
                        event.retry_count += 1
                        event.error_log = str(e)
                        event.updated_at = datetime.utcnow()
                        
                        if event.retry_count >= 3:
                            event.status = 'failed'
                        else:
                            event.status = 'pending' # Retry
                            
                await db.commit()
                
        except Exception as e:
            logger.error(f"Critical error in Event Loop: {e}")
            traceback.print_exc()
            await asyncio.sleep(5)

async def process_media():
    logger.info("Starting Media Processor Loop")
    while True:
        try:
            async with AsyncSessionLocal() as db:
                # Fetch messages with media_pending
                query = (
                    select(Message)
                    .options(selectinload(Message.tenant))
                    .where(Message.status == 'media_pending')
                    .limit(10)
                    .with_for_update(skip_locked=True)
                )
                
                result = await db.execute(query)
                messages = result.scalars().all()
                
                if not messages:
                    await asyncio.sleep(1)
                    continue
                
                logger.info(f"Processing {len(messages)} media messages")
                
                service = WebhookService()
                
                for message in messages:
                    try:
                        if hasattr(service, 'process_media'):
                            await service.process_media(message, db)
                        else:
                            logger.warning("process_media method not found in WebhookService yet.")
                            await asyncio.sleep(1) 
                            
                    except Exception as e:
                        logger.error(f"Error processing media for message {message.id}: {e}")
                        
                await db.commit()
                
        except Exception as e:
            logger.error(f"Critical error in Media Loop: {e}")
            await asyncio.sleep(5)

async def main():
    await asyncio.gather(
        process_events(),
        process_media()
    )

if __name__ == "__main__":
    asyncio.run(main())
