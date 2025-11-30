# WPConn API

High-performance, asynchronous REST API for WhatsApp Cloud API communication.

## Requirements
- Python 3.10+
- PostgreSQL
- Docker & Docker Compose

## Database Configuration
> [!IMPORTANT]
> **Database Connection**: Ensure your PostgreSQL database is running and accessible. The `DATABASE_URL` in `.env` must be correct.
> If running via Docker, ensure the `db` service is healthy before starting the API.
> If running locally, ensure you have created the database (e.g., `wpp_connect`) and that the user has permissions.

## Setup
1. Clone the repository
2. Copy `.env.example` to `.env`
3. Run `docker-compose up -d`

## Documentation
See `/docs` for more details.
