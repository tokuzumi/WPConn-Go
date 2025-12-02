# Documentação de Integração - WPConn API

Esta documentação fornece as instruções necessárias para integrar sua aplicação com a API do WPConn para envio e recebimento de mensagens do WhatsApp.

## 🔐 Autenticação

Todas as requisições devem incluir o cabeçalho `x-api-key`.
Esta chave é única por conexão e pode ser encontrada no Dashboard > Telefones.

```http
x-api-key: SUA_API_KEY_AQUI
```

---

## 📤 Enviando Mensagens

### Endpoint
`POST https://webhook.talkingcar.com.br/api/v1/messages/send`

### 1. Enviar Texto Simples

**Payload:**
```json
{
  "to_number": "5511999999999",
  "content": "Olá! Esta é uma mensagem de teste."
}
```

### 2. Enviar Mídia (Imagem, Vídeo, Áudio, Documento)

A API suporta o envio de mídia através de **Links Públicos**. Você não precisa enviar o arquivo binário; apenas forneça a URL e a API instruirá o WhatsApp a baixá-lo.

**Tipos Suportados (`media_type`):**
*   `image` (JPEG, PNG)
*   `video` (MP4)
*   `audio` (MP3, OGG)
*   `document` (PDF)

**Payload:**
```json
{
  "to_number": "5511999999999",
  "media_type": "image",
  "media_url": "https://exemplo.com/minha-imagem.jpg",
  "caption": "Confira esta imagem! 📸"
}
```

> **Nota:** A URL deve ser pública e acessível diretamente pela internet.

---

## 📥 Recebendo Mensagens (Webhook)

Configure sua URL de Webhook no Dashboard > Telefones > Editar > Webhook URL.
Sempre que uma nova mensagem chegar, a API fará um `POST` para sua URL com o seguinte JSON:

**Payload do Webhook:**
```json
{
  "id": "uuid-da-mensagem-no-banco",
  "wamid": "wamid.HBgM...",
  "phone": "5511999999999",
  "direction": "inbound",
  "type": "text",
  "status": "received",
  "content": "Olá, gostaria de um orçamento.",
  "media_url": null,
  "media_type": null,
  "caption": null,
  "created_at": "2023-10-27T10:00:00.000000"
}
```

*   **`type`**: Pode ser `text`, `image`, `audio`, `video`, `document`, etc.
*   **`content`**: O texto da mensagem (ou null se for mídia).
*   **`media_url`**: Link para download da mídia (se houver).

---

## 🔎 Consultando Status da Mensagem

Para verificar se uma mensagem foi enviada, entregue ou lida, ou para recuperar seus detalhes.

### Endpoint
`GET https://webhook.talkingcar.com.br/api/v1/messages/{message_id}`

**Exemplo de Resposta:**
```json
{
  "id": "uuid-da-mensagem",
  "status": "sent",
  "wamid": "wamid.HBgM...",
  "phone": "5511999999999",
  "direction": "outbound",
  "type": "text",
  "content": "Olá!",
  "created_at": "2023-10-27T10:00:00"
}
```

---

## 🔄 Tratamento de Erros e Retentativas

Se o seu endpoint de Webhook estiver indisponível (retornar erro ou timeout), a API registrará a falha.
Você pode visualizar esses erros no **Dashboard > Logs > Logs de Erros** e utilizar o botão **"Reenviar"** para disparar o webhook novamente manualmente.
