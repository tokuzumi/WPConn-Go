# Guia de Integração WpConn

Este documento descreve o processo de integração com o **WpConn**, uma camada de middleware projetada para simplificar a comunicação com a WhatsApp Business Cloud API. O WpConn gerencia a complexidade de webooks, tokens e armazenamento de mensagens, oferecendo uma API unificada para sua aplicação.

## Visão Geral

O WpConn atua como um intermediário entre a Meta (WhatsApp) e sua aplicação (App/Dashboard).

- **Domínio da API:** `https://webhook.uaaldrive.com.br/api/v1`
- **Domínio do App:** `https://wpconn.uaaldrive.com.br`

### Fluxo de Mensagens

1.  **Recebimento (Entrada):**
    Quando um cliente envia uma mensagem para o número WhatsApp conectado, a Meta envia um Webhook para o WpConn. O WpConn processa, armazena a mensagem e resolve URLs de mídia automaticamente.
    *Atualmente, a entrega para a aplicação é feita via **Polling** (consulta periódica) ao endpoint de mensagens.*

2.  **Envio (Saída):**
    A aplicação envia uma requisição HTTP REST para o WpConn, que valida e encaminha a mensagem para a API da Meta.

---

## Passo-a-Passo para Integração

### 1. Autenticação
Todas as requisições para a API do WpConn devem incluir o cabeçalho `x-api-key`.
Esta chave é gerada ao criar um Tenant no Dashboard ou via API.

```http
x-api-key: sua-api-key-secreta
```

### 2. Consultar Mensagens (Recebimento)
Para receber mensagens dos seus clientes, sua aplicação deve consultar o endpoint de mensagens periodicamente.

**Endpoint:** `GET /messages`
**URL Completa:** `https://webhook.uaaldrive.com.br/api/v1/messages`

**Parâmetros Opcionais:**
- `limit`: Número de mensagens (padrão 50).
- `offset`: Paginação.
- `search`: Filtrar por conteúdo.

**Exemplo de Requisição (cURL):**
```bash
curl -X GET "https://webhook.uaaldrive.com.br/api/v1/messages?limit=10" \
     -H "x-api-key: sua-key"
```

### 3. Enviar Mensagens (Envio)
**Endpoint:** `POST /messages`
**URL Completa:** `https://webhook.uaaldrive.com.br/api/v1/messages`

**Payload Obrigatório:**
- `phone`: Número do destinatário (com DDI, ex: `5511999999999`).
- `type`: Tipo de mensagem (`text`, `image`, `video`, `document`, `audio`, `sticker`).
- `content`: Texto da mensagem (obrigatório para `text`, opcional como legenda para outros tipos).
- `media_url`: URL pública do arquivo (obrigatório para todos exceto `text`).

> [!IMPORTANT]
> **Mídia**: Para envio de imagens, vídeos e documentos, você deve fornecer uma URL pública (`media_url`). O WpConn repassa este link diretamente para a Meta. Certifique-se de que a URL seja acessível externamente.

**Exemplo de Requisição (cURL):**
```bash
curl -X POST "https://webhook.uaaldrive.com.br/api/v1/messages" \
     -H "x-api-key: sua-key" \
     -H "Content-Type: application/json" \
     -d '{
           "phone": "5511999998888",
           "type": "text",
           "content": "Olá! Seu pedido foi confirmado."
         }'
```

---

## Estrutura de Dados (Exemplos)

### Mensagem Recebida (WpConn -> Aplicação)
Este é o formato que você receberá ao consultar o endpoint `GET /messages`.

**Texto:**
```json
{
  "id": "uuid...",
  "type": "text",
  "direction": "inbound",
  "content": "Olá, tudo bem?",
  "media_url": "",
  "sender_phone": "5541988887777",
  "created_at": "..."
}
```

**Mídia (Áudio, Imagem, Vídeo):**
Para mensagens de mídia, o campo `media_url` conterá o link direto da Meta (já resolvido pelo WpConn). O `content` pode conter a legenda (se houver).

```json
{
  "id": "uuid...",
  "type": "audio",
  "direction": "inbound",
  "content": "", // Áudios geralmente não têm legenda
  "media_url": "https://lookaside.fbsbx.com/...", // URL temporária da Meta
  "sender_phone": "5541988887777",
  "created_at": "..."
}
```

### Mensagem a Enviar (Aplicação -> WpConn)
Este é o formato que sua aplicação deve construir para enviar uma mensagem.

**Texto Simples:**
```json
{
  "phone": "5511987654321",
  "type": "text",
  "content": "Olá, como podemos ajudar?"
}
```

**Imagem (com legenda):**
```json
{
  "phone": "5511987654321",
  "type": "image",
  "media_url": "https://sua-empresa.com/imagem.png",
  "content": "Segue o catálogo atualizado."
}
```

**Áudio (Link):**
```json
{
  "phone": "5511987654321",
  "type": "audio",
  "media_url": "https://sua-empresa.com/audio.mp3"
}
```

**Documento (PDF):**
```json
{
  "phone": "5511987654321",
  "type": "document",
  "media_url": "https://sua-empresa.com/contrato.pdf",
  "content": "Minuta do contrato"
}
```

---

## Status de Entrega
O WpConn gerencia os status de entrega (sent, delivered, read) internamente. Ao consultar o histórico (`GET /messages`), o campo `status` refletirá o estado mais recente processado pelo Webhook da Meta.
