# Resolução de Erro "Mixed Content" (Conteúdo Misto)

## O Problema
Ao implantar a aplicação em produção com HTTPS (via Traefik), o Dashboard (carregado via HTTPS) falhava ao se comunicar com a API, gerando erros de "Mixed Content".

### Sintomas
- O navegador bloqueava requisições para a API.
- O console exibia erros como: `Blocked loading mixed active content "http://webhook.talkingcar.com.br/api/v1/tenants/"`.
- Redirecionamentos automáticos do FastAPI (ex: adicionar `/` no final da URL) convertiam a requisição para `http://`, quebrando a segurança.

## Causa Raiz
O servidor **Uvicorn** (que roda a API FastAPI) estava atrás do proxy reverso **Traefik**. Por padrão, o Uvicorn não confia nos cabeçalhos `X-Forwarded-Proto` ou `X-Forwarded-For` enviados pelo proxy.

Consequentemente, o Uvicorn acreditava estar rodando em `http://`. Quando o FastAPI precisava fazer um redirecionamento (como uma correção de `trailing slash`), ele gerava uma URL de destino usando `http`, o que causava o bloqueio pelo navegador (que exige que uma página HTTPS só chame recursos HTTPS).

## A Solução
Configuramos o Uvicorn para confiar nos cabeçalhos do proxy.

### Alteração Realizada
No arquivo `wpp-connect-api/run.sh`, o comando de inicialização foi alterado para incluir as flags `--proxy-headers` e `--forwarded-allow-ips '*'`.

**Antes:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Depois:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --proxy-headers --forwarded-allow-ips '*'
```

### O que as flags fazem?
- `--proxy-headers`: Instrui o Uvicorn a ler os cabeçalhos `X-Forwarded-*` para determinar o esquema (http/https) e o IP real do cliente.
- `--forwarded-allow-ips '*'`: Define quais IPs de proxy são confiáveis. Como estamos em um ambiente Docker onde o IP do Traefik pode variar, usamos `*` para confiar em qualquer IP (seguro pois o container não é exposto diretamente à internet, apenas via Traefik).
