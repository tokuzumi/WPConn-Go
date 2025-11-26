from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.api.v1.routers import tenants, messages, webhooks

app = FastAPI(title="wpp-connect-api")

app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

@app.get("/")
async def root():
    return {"message": "Welcome to wpp-connect-api"}
