# ✅ Checklist de deploy piloto — Giu no Railway via Telegram

Marque cada item na ordem. Tempo estimado: 30 minutos.

## A. Antes do Railway

- [ ] Token do bot do Telegram em mãos (o NOVO, gerado após o `/revoke` no @BotFather)
- [ ] Chave da OpenAI em mãos
- [ ] Gerar dois tokens aleatórios (rode 2x):
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  Um será o `GIU_API_TOKEN`, o outro o `TELEGRAM_SECRET_TOKEN`.

## B. Criar o serviço

- [ ] [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → `Base-X`
- [ ] **Settings → Root Directory** = `giu` (o Dockerfile faz o resto)
- [ ] Start command: nenhum a configurar — o Dockerfile já define
      `uvicorn server:app --host 0.0.0.0 --port ${PORT}` e o Railway injeta a `PORT` sozinho

## C. Variáveis de ambiente (aba Variables)

- [ ] `OPENAI_API_KEY` = sua chave
- [ ] `GIU_DB_PATH` = `/data/giu_memory.db`
- [ ] `GIU_API_TOKEN` = primeiro token gerado
- [ ] `TELEGRAM_BOT_TOKEN` = token do @BotFather
- [ ] `TELEGRAM_SECRET_TOKEN` = segundo token gerado

## D. Volume persistente (a memória NÃO pode se perder)

- [ ] **Settings → Volumes → Add Volume** → Mount Path `/data`, 1 GB
- [ ] Conferir que `GIU_DB_PATH` aponta para dentro dele (`/data/giu_memory.db`)

## E. URL pública e webhook

- [ ] **Settings → Networking → Generate Domain** → anote `https://SEU-DOMINIO`
- [ ] Registrar o webhook (secret IGUAL ao da variável):
  ```bash
  curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://SEU-DOMINIO/webhook/telegram&secret_token=<TELEGRAM_SECRET_TOKEN>"
  ```
- [ ] Conferir: `curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"` → mostra a URL certa

## F. Testes de aceitação (na ordem)

**1. Saúde** — deve responder `"giu": "online"` com `"telegram": true`:
```bash
curl https://SEU-DOMINIO/
```

**2. Segurança** — sem token deve dar **401**:
```bash
curl -o /dev/null -w "%{http_code}\n" -X POST https://SEU-DOMINIO/chat \
  -H 'Content-Type: application/json' -d '{"user_id":"teste","message":"oi"}'
```

**3. /chat com token** — deve responder como a Giu:
```bash
curl -X POST https://SEU-DOMINIO/chat \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <GIU_API_TOKEN>' \
  -d '{"user_id":"teste","message":"oi"}'
```

**4. Onboarding (no Telegram)** — mande **"oi"** para o bot:
- [ ] Ela se apresenta com acolhimento e pergunta O QUE você vive esquecendo/adiando (UMA pergunta só)
- [ ] Responda; ela agradece e pergunta como prefere ser chamada
- [ ] Responda; ela usa seu nome e pede consentimento para guardar preferências
- [ ] Responda "sim"; ela agradece sem listar funcionalidades

**5. Ação pendente** — mande: *"marca dentista sexta às 14h"*
- [ ] Ela apresenta o resumo e PERGUNTA antes de criar (não executa direto)

**6. Confirmação** — responda *"pode sim"*
- [ ] Ela confirma que agendou; *"o que tenho essa semana?"* deve mostrar o compromisso

**7. Memória persistente** — em **Settings → Deployments → Redeploy**:
- [ ] Após o redeploy, pergunte *"como eu pedi pra você me chamar?"* — ela deve lembrar

**8. Resumo diário**:
```bash
curl https://SEU-DOMINIO/summary/<SEU_CHAT_ID> -H 'Authorization: Bearer <GIU_API_TOKEN>'
```
(seu chat_id aparece nos logs do Railway quando você manda mensagem)

**9. Check-in (opcional, no dia seguinte)** — às 08:00 ela manda o bom dia sozinha
(só depois do onboarding completo com consentimento "sim").

## Se algo falhar

| Sintoma | Causa provável |
|---------|----------------|
| Bot não responde | `getWebhookInfo` com URL errada, ou `TELEGRAM_SECRET_TOKEN` diferente entre Railway e setWebhook |
| Tudo 403 no webhook | secret do setWebhook ≠ variável `TELEGRAM_SECRET_TOKEN` |
| "Estou sem conexão com meu cérebro" | `OPENAI_API_KEY` ausente/errada |
| Esqueceu tudo após redeploy | volume não montado ou `GIU_DB_PATH` fora de `/data` |
| Erro de timezone nos logs | rode o deploy de novo — `tzdata` está no requirements |
