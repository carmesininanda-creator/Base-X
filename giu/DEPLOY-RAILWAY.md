# Deploy da Giu no Railway

Coloca o cérebro da Giu no ar com URL pública — pré-requisito para WhatsApp e Telegram funcionarem.

## Passo 1 — Criar o serviço

1. Acesse [railway.app](https://railway.app) e faça login com GitHub.
2. **New Project** → **Deploy from GitHub repo** → selecione **Base-X**.
3. Em **Settings → Root Directory**, defina: `giu`
   (o Railway vai detectar o `Dockerfile` automaticamente).

## Passo 2 — Variáveis de ambiente

Na aba **Variables**, adicione:

| Variável | Obrigatória? | Valor |
|----------|--------------|-------|
| `OPENAI_API_KEY` | ✅ Sim | sua chave da OpenAI |
| `GIU_DB_PATH` | ✅ Sim | `/data/giu_memory.db` (ver Passo 3) |
| `GIU_API_TOKEN` | ✅ Sim em produção | string aleatória longa — protege `/chat` e `/memories` |
| `TELEGRAM_BOT_TOKEN` | opcional | token do @BotFather |
| `TELEGRAM_SECRET_TOKEN` | recomendado | string aleatória — valida que o webhook veio do Telegram |
| `WHATSAPP_TOKEN` | opcional | token da Meta Cloud API |
| `WHATSAPP_PHONE_ID` | opcional | phone ID da Meta |
| `META_APP_SECRET` | recomendado | App Secret da Meta — valida a assinatura dos webhooks |
| `GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN` | opcional | ver README |

Para gerar tokens aleatórios: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## Passo 3 — Volume persistente (a memória NÃO pode se perder)

A memória da Giu é o produto. Sem volume, ela esquece tudo a cada deploy.

1. **Settings → Volumes → Add Volume**
2. Mount Path: `/data` — Size: 1 GB
3. Confirme que `GIU_DB_PATH=/data/giu_memory.db` está nas variáveis.

## Passo 4 — Gerar a URL pública

**Settings → Networking → Generate Domain** → você ganha algo como
`giu-production.up.railway.app`.

Teste: abra `https://SEU-DOMINIO/` — deve responder:

```json
{"giu": "online", "tagline": "Você não precisa segurar tudo sozinha. Eu estou aqui.", ...}
```

## Passo 5 — Registrar os webhooks

**Telegram** (uma vez — o `secret_token` DEVE ser o mesmo valor de `TELEGRAM_SECRET_TOKEN`):
```bash
curl "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://SEU-DOMINIO/webhook/telegram&secret_token=<SEU_TELEGRAM_SECRET_TOKEN>"
```
Confirme com: `curl "https://api.telegram.org/bot<SEU_TOKEN>/getWebhookInfo"` — deve mostrar a URL e `"pending_update_count": 0`.

**WhatsApp**: no painel da Meta (Configuration → Webhook), cadastre
`https://SEU-DOMINIO/webhook/whatsapp` com verify token `giu-bazex` e assine o campo `messages`.

## Pronto

Mande uma mensagem para o bot — a Giu responde, lembra, e os lembretes
proativos chegam sozinhos na hora marcada. ✦
