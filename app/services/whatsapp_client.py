import httpx
from typing import Any, Dict

class WhatsAppClient:
    BASE_URL = "https://graph.facebook.com/v17.0"

    async def send_text_message(
        self, 
        token: str, 
        phone_number_id: str, 
        to_number: str, 
        message_body: str
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": message_body}
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
