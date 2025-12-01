from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings

app = FastAPI(title="wpp-connect-api")

# Set all CORS enabled origins
# Configuração CORS Permissiva (Hardcoded para Produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.routers import tenants, messages, logs, users, dashboard, webhooks

app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messages"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["Logs"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])

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
