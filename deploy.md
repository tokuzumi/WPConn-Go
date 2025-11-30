# Guia de Deploy em Produção (VPS) com Traefik Existente

Este guia descreve os passos para implantar o WPConn em um servidor VPS onde o **Traefik já está rodando** como Reverse Proxy.

## 1. Pré-requisitos
- Servidor VPS com Docker e Docker Compose.
- **Traefik já instalado e configurado** (com Entrypoints `web` e `websecure` e CertResolver `myresolver` ou similar).
- Uma rede Docker externa onde o Traefik está conectado (ex: `proxy`, `web`, `traefik-public`).

## 2. Estrutura de Arquivos
No servidor, clone o repositório:
```bash
git clone https://github.com/tokuzumi/WPConn.git
cd WPConn
```

## 3. Configuração de Variáveis de Ambiente
Crie um arquivo `.env` na raiz com as configurações abaixo.

```env
# Configuração de Domínios
DOMAIN_API=api.seudominio.com
DOMAIN_APP=app.seudominio.com

# Configuração do Traefik
# Nome da rede Docker onde o Traefik está rodando (ex: proxy, web, traefik_network)
TRAEFIK_NETWORK=proxy

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha_segura_db
POSTGRES_DB=wpp_connect
DATABASE_URL=postgresql+asyncpg://postgres:sua_senha_segura_db@db:5432/wpp_connect

# Backend API
APP_SECRET=sua_chave_secreta_gerada_com_openssl
WEBHOOK_VERIFY_TOKEN=seu_token_de_verificacao_meta
API_V1_STR=/api/v1
# CORS: Deve incluir o domínio do frontend
BACKEND_CORS_ORIGINS=["https://app.seudominio.com"]

# MinIO (Opcional)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=whatsapp-media
MINIO_USE_SSL=False

# Frontend Dashboard
NEXTAUTH_SECRET=sua_chave_secreta_nextauth
```

## 4. Ajustes no Docker Compose (Se necessário)
O arquivo `docker-compose.prod.yml` assume algumas configurações padrão do Traefik:
- **CertResolver**: `myresolver`. Se o seu Traefik usa outro nome (ex: `letsencrypt`), edite as labels no arquivo `docker-compose.prod.yml`.
- **Entrypoints**: `websecure`.

## 5. Deploy
Suba os serviços. Eles se conectarão automaticamente à rede do Traefik definida em `TRAEFIK_NETWORK`.

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 6. Verificação
- Verifique se os containers subiram e estão na rede correta.
- Acesse `https://app.seudominio.com`.
