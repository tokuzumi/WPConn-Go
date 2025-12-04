# Guia de Deploy (Go + Temporal)

Este guia descreve como implantar o novo stack WPConn (Go) em um ambiente com Traefik.

## 1. Estrutura
O projeto agora reside principalmente em `wpconn-go/`.

## 2. Configuração
Certifique-se de que o arquivo `.env` em `wpconn-go/` esteja configurado corretamente com:
-   `TRAEFIK_NETWORK`: Nome da rede externa do Traefik.
-   `APP_SECRET`: Chave para assinatura de JWT e validação de Webhook.
-   `WEBHOOK_VERIFY_TOKEN`: Token de verificação da Meta.

## 3. Deploy
No servidor:

```bash
cd WPConn/wpconn-go
docker-compose up -d --build
```

## 4. Verificação
-   **Webhook**: `https://webhook.talkingcar.com.br/api/v1/webhooks` (GET para verificar token).
-   **Dashboard**: `https://app.talkingcar.com.br`.
