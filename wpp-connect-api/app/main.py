from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.api.v1.routers import tenants, messages, webhooks

from app.core.config import settings

app = FastAPI(title="wpp-connect-api")

app.include_router(tenants.router, prefix=f"{settings.API_V1_STR}/tenants", tags=["tenants"])
app.include_router(messages.router, prefix=f"{settings.API_V1_STR}/messages", tags=["messages"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_STR}/webhooks", tags=["webhooks"])

from app.api.v1.routers import logs
app.include_router(logs.router, prefix=f"{settings.API_V1_STR}/logs", tags=["logs"])

from app.api.v1.routers import users
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

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
