# WPConn - WhatsApp Cloud API Gateway (Enterprise)

**WPConn** é um gateway de alta performance para a WhatsApp Cloud API, projetado para durabilidade e escala.

-   **Backend**: Go 1.24 (Fiber v3)
-   **Orquestração**: Temporal.io (Gerenciamento de Estado e Retries)
-   **Frontend**: Next.js 14 (Dashboard Administrativo)
-   **Banco de Dados**: PostgreSQL

---

## 🚀 Quick Start (Deploy)

### 1. Pré-requisitos
-   Docker & Docker Compose
-   Rede externa para o Traefik (padrão: `proxy`)
    ```bash
    docker network create proxy
    ```

### 2. Configuração (⚠️ Importante)

A configuração é **CENTRALIZADA**.

1.  Crie **APENAS UM** arquivo `.env` dentro da pasta `wpconn-go/`.
2.  **NÃO** crie arquivos `.env` em `dashboard/`. O sistema injeta as variáveis automaticamente.

**Copie o exemplo:**
```bash
cp wpconn-go/.env.example wpconn-go/.env
```

**Variáveis Obrigatórias (`wpconn-go/.env`):**
-   `TRAEFIK_NETWORK`: Nome da rede do Traefik (ex: `proxy`).
-   `APP_SECRET`: Chave mestra para JWT e validação de Webhooks.
-   `WEBHOOK_VERIFY_TOKEN`: Token global para o "aperto de mão" com a Meta (você define essa senha).
-   `POSTGRES_...`: Credenciais do banco.

### 3. Executando
Na raiz do projeto (ou dentro de `wpconn-go/`):

```bash
cd wpconn-go
docker-compose up -d --build
```

---

## 🔍 Monitoramento & Acesso

-   **Dashboard** (Admin e Cadastro): `https://app.talkingcar.com.br` (ou `http://localhost:3001`)
-   **API** (Webhook Incoming): `https://webhook.talkingcar.com.br`
-   **Health Check**: `https://webhook.talkingcar.com.br/health` (Retorna `{"status": "ok"}`)

---

## 📘 Guia: Conectar WhatsApp (Cadastro)

Este sistema é apenas o **Gateway**. Você deve ter criado o App e o System User no [Meta Developers](https://developers.facebook.com) previamente.

### 1. No Dashboard WPConn
Acesse o menu **Conexões** e clique em **Nova Conexão**. Preencha com os dados da Meta:

1.  **Nome**: Ex: "Suporte N1".
2.  **WABA ID**: ID da conta WhatsApp.
3.  **Phone Number ID**: ID do número.
4.  **Token**: Token Permanente do System User (permissão `whatsapp_business_messaging`).

### 2. Na Meta (Webhook Config)
No Developers Portal > WhatsApp > Configuration:

-   **Callback URL**: `https://webhook.talkingcar.com.br/api/v1/webhooks`
-   **Verify Token**: Deve ser idêntico ao valor de `WEBHOOK_VERIFY_TOKEN` configurado no seu `.env` raiz.

⚠️ **Atenção**: O `.env` valida o "aperto de mão". O Dashboard valida quem é o dono do número.

---

## 🛠️ Testes & Simulação (cURL)

### 1. Simular Recebimento (Inbound)
Para testar se o Gateway está aceitando mensagens sem precisar enviar um WhatsApp real.

**Texto Simples:**
```bash
curl -X POST "http://localhost:3090/api/v1/webhooks" \
     -H "Content-Type: application/json" \
     -d '{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "123456789",
          "phone_number_id": "SEU_PHONE_NUMBER_ID_AQUI"
        },
        "messages": [{
          "from": "5511999999999",
          "id": "wamid.HBgM...",
          "timestamp": "1702150000",
          "text": {
            "body": "Olá, teste de webhook!"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}'
```

**Imagem:**
```bash
curl -X POST "http://localhost:3090/api/v1/webhooks" \
     -H "Content-Type: application/json" \
     -d '{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": { "phone_number_id": "SEU_PHONE_NUMBER_ID_AQUI" },
        "messages": [{
          "from": "5511999999999",
          "id": "wamid.HBgM...",
          "timestamp": "1702150000",
          "type": "image",
          "image": {
            "caption": "Legenda da imagem",
            "mime_type": "image/jpeg",
            "sha": "hash...",
            "id": "MEDIA_ID_DA_META"
          }
        }]
      },
      "field": "messages"
    }]
  }]
}'
```

### 2. Testar Envio Real (Outbound)
Use este comando para testar se o seu **Token** e **Phone ID** estão funcionando diretamente com a Meta API.

```bash
curl -X POST "https://graph.facebook.com/v19.0/SEU_PHONE_ID_AQUI/messages" \
     -H "Authorization: Bearer SEU_TOKEN_PERMANENTE_AQUI" \
     -H "Content-Type: application/json" \
     -d '{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "text",
  "text": { "body": "Teste de envio via API Oficial" }
}'
```

## 🚀 Próximos Passos?
1.  Verifique a aba **Conexões** no Dashboard para ver o status.
2.  Confira a aba **Mensagens** para ver os logs de recebimento.
3.  Acompanhe o workflow no **Temporal UI** (`:8080`).
