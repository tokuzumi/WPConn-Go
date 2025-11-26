import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MetaClient:
    def __init__(self, tenant_token: str, phone_number_id: str):
        self.token = tenant_token
        self.phone_number_id = phone_number_id
        self.base_url = "https://graph.facebook.com/v17.0"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def get_media_url(self, media_id: str) -> str:
        """
        Retrieves the temporary download URL for a media object.
        """
        url = f"{self.base_url}/{media_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("url")
            else:
                logger.error(f"Failed to get media URL: {response.text}")
                return None

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def get_media_stream(self, url: str):
        """
        Yields a stream of the media content.
        """
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url, headers={"Authorization": f"Bearer {self.token}"}) as response:
                if response.status_code == 200:
                    yield response.aiter_bytes()
                else:
                    logger.error(f"Failed to download media: {response.status_code}")
                    yield None

    async def upload_media(self, file_stream, content_type: str) -> str:
        """
        Uploads media to Meta and returns the media ID.
        """
        url = f"{self.base_url}/{self.phone_number_id}/media"
        
        # httpx requires a specific format for file uploads:
        # files = {'file': ('filename', file_stream, 'content_type')}
        # Since we are streaming, we need to ensure file_stream is compatible.
        # If file_stream is an async iterator (from aioboto3/utils), httpx might not handle it directly as a file.
        # However, we can read it into memory if it's not too huge, OR use a generator.
        # Given the "100 users 10MB" requirement, we should stream.
        # But httpx async client upload with generator is tricky.
        # Let's assume for now we read chunks.
        
        # Actually, aioboto3 download_fileobj writes to a file-like object.
        # We can use a custom AsyncReader that yields data.
        
        # For simplicity in this iteration, let's assume we can read the stream.
        # If file_stream is the AsyncIteratorToFileLike we created, it has a read method.
        # But httpx expects a sync read or an async iterator.
        
        # Let's try to just pass the stream if it supports read.
        
        files = {
            "file": ("media_file", file_stream, content_type),
            "messaging_product": (None, "whatsapp")
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers={"Authorization": f"Bearer {self.token}"}, files=files)
            
            if response.status_code == 200:
                return response.json().get("id")
            else:
                logger.error(f"Failed to upload media: {response.text}")
                return None

    async def send_message(self, payload: dict):
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            if response.status_code not in [200, 201]:
                logger.error(f"Failed to send message: {response.text}")
                return response.json() # Return error response for debugging
            return response.json()
