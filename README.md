# WPConn - WhatsApp Cloud API Gateway

WPConn is a high-performance, asynchronous FastAPI backend designed to govern communication with the WhatsApp Cloud API. It replaces third-party solutions like Evolution API, giving you full control over your WhatsApp integration.

## 🚀 Features

-   **Multi-Tenancy**: Support for multiple tenants (clients), each with their own WhatsApp credentials.
-   **Secure Authentication**: API Key-based authentication for all endpoints.
-   **Media Support**:
    -   **Receiving**: Automatically streams media (Images, Videos, Audio, Documents) from Meta to your own MinIO storage.
    -   **Sending**: Sends media directly from MinIO to WhatsApp, with intelligent caching to avoid redundant uploads.
-   **Message Context**: Tracks message replies (`reply_to_wamid`) to maintain conversation history.
-   **Webhook Gateway**: Robust webhook processing with idempotency and status tracking.
-   **Asynchronous Architecture**: Built with `asyncio`, `FastAPI`, and `SQLAlchemy` (Async) for high throughput.

## 🛠️ Tech Stack

-   **Language**: Python 3.10+
-   **Framework**: FastAPI
-   **Database**: PostgreSQL (Async via SQLAlchemy)
-   **Storage**: MinIO (S3 Compatible)
-   **HTTP Client**: `httpx` (Async)

## ⚙️ Setup

### 1. Prerequisites
-   Python 3.10+
-   PostgreSQL
-   MinIO Server

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/tokuzumi/WPConn.git
cd WPConn/wpp-connect-api

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate # Windows
# source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/wpconn_db

# Security
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Meta / WhatsApp
APP_SECRET=your_meta_app_secret
WEBHOOK_VERIFY_TOKEN=your_verify_token

# MinIO (Storage)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your_minio_access_key
MINIO_SECRET_KEY=your_minio_secret_key
MINIO_BUCKET_NAME=whatsapp-media
MINIO_USE_SSL=false
```

### 4. Database Migrations

```bash
alembic upgrade head
```

## 🏃‍♂️ Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## 📚 API Documentation

Interactive API documentation (Swagger UI) is automatically generated and available at:
-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Authentication
All endpoints (except Webhooks) require an `x-api-key` header.

#### Sending Messages

**Text Message:**
```json
POST /api/v1/messages/send
{
  "to_number": "5511999999999",
  "content": "Hello World!"
}
```

**Media Message:**
```json
POST /api/v1/messages/send
{
  "to_number": "5511999999999",
  "media_url": "bucket/path/to/image.jpg",
  "media_type": "image",
  "caption": "Check this out!"
}
```

## 🧪 Verification Scripts

The project includes several scripts to verify functionality:
-   `verify_media_flow.py`: Tests receiving media and saving to MinIO.
-   `verify_send_media.py`: Tests sending media from MinIO to WhatsApp.
-   `verify_reply_flow.py`: Tests message reply context.
