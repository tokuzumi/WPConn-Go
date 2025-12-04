# WPConn - WhatsApp Cloud API Gateway (Go + Temporal)

WPConn is a high-performance, durable backend designed to govern communication with the WhatsApp Cloud API. Rebuilt in **Go 1.24** and **Temporal**, it ensures ultra-low latency webhook handling and reliable background processing.

## 🚀 Features

-   **Go Core**: Built with Fiber v3 for extreme performance.
-   **Durable Execution**: Temporal workflows manage complex business logic and retries.
-   **Docker-First**: Optimized for containerized environments (Dev & Prod).
-   **Zero-Trust Media**: Passes media IDs to workflows without downloading content in the gateway.
-   **Hot-Reload**: Integrated `air` for seamless local development.

## 🛠️ Tech Stack

-   **Language**: Go 1.24
-   **Framework**: Fiber v3
-   **Orchestration**: Temporal.io
-   **Database**: PostgreSQL
-   **Dashboard**: Next.js (React)

## 🚀 Quick Start (Docker)

To run the full project (Dashboard + API + Temporal + Database):

### 1. Configuration
Copy the `.env` file into `wpconn-go/`:
```bash
cp .env.example wpconn-go/.env
# Edit wpconn-go/.env with your credentials
```

### 2. Start Services
```bash
cd wpconn-go
docker-compose up --build
```

### 3. Access
-   **Dashboard**: http://localhost:3001 (or https://app.talkingcar.com.br via Traefik)
-   **API**: http://localhost:3002/api/v1 (Internal) / https://webhook.talkingcar.com.br (Public)
-   **Temporal UI**: http://localhost:8080 (or https://temporal.talkingcar.com.br)

## 📂 Project Structure

-   `wpconn-go/`: Go Backend & Temporal Worker
-   `dashboard/`: Next.js Frontend
