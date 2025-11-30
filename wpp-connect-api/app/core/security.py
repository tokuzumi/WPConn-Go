import hmac
import hashlib
from fastapi import Request, HTTPException, status
from app.core.config import settings

async def verify_webhook_signature(request: Request):
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing X-Hub-Signature-256 header"
        )
    
    # Extract hash from "sha256=<hash>"
    parts = signature.split("=")
    if len(parts) != 2 or parts[0] != "sha256":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature format"
        )
    
    expected_hash = parts[1]
    
    # Get raw body
    body = await request.body()
    
    # Calculate HMAC
    calculated_hmac = hmac.new(
        key=settings.APP_SECRET.encode(),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_hash, calculated_hmac):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature"
        )
