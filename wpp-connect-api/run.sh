#!/bin/bash

# Executa as migrações do banco de dados
echo "Running database migrations..."
alembic upgrade head

# Inicia a aplicação
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'
