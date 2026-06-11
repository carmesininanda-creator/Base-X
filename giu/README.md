# ✦ Giu — o cérebro da BazeX

> "Você não precisa segurar tudo sozinha. Eu estou aqui."

A Giu não é um app. Os dispositivos já existem — **a Giu é o cérebro** que
aparece neles. Este projeto é exatamente a arquitetura desenhada:

```text
              GIU
       (Cérebro Central)
        giu/brain.py
             │
 ┌───────────┼───────────┐
 │           │           │
WhatsApp    Web       Terminal      ← portas (giu/channels + server.py)
 │           │           │
 └───────────┼───────────┘
             │
      Memória da Vida               ← giu/memory.py (SQLite)
             │
 ┌──────┬────┴────┬──────┐
 │      │         │      │
Fatos Agenda  Lembretes Perfil      ← depois: Uber, iFood, Calendar, Banco
```

**Uma decisão importante já está tomada no código:** a Giu é a
**Companheira**, não a Secretária. Ela resolve tarefas, mas também lembra,
conversa, cuida e observa. O vínculo é o produto.

## O que já funciona (MVP 1)

| Parte | O que faz |
|-------|-----------|
| 🧠 Cérebro (`giu/brain.py`) | Loop de agente com ferramentas: pensa, age, responde |
| 💾 Memória (`giu/memory.py`) | Fatos permanentes, histórico, perfil, agenda, lembretes |
| 🛠 Ferramentas (`giu/tools.py`) | lembrar_fato, agendar, ver_agenda, criar_lembrete, buscar_memoria |
| 💬 Porta WhatsApp | Webhook oficial Meta Cloud API (recebe e responde) |
| ✈️ Porta Telegram | Webhook oficial Bot API (recebe e responde) |
| 🌐 Porta Web | `POST /chat` — qualquer app/site pode plugar |
| ⌨️ Porta Terminal | `python cli.py` para testar agora |
| 📅 Google Calendar | `agendar` cria eventos reais; `ver_agenda` mostra os próximos |
| ⏰ Proatividade | Scheduler envia lembretes na hora marcada, pelo canal de origem |

A memória é **uma só**: o que você conta no terminal, ela lembra no WhatsApp.

## Como rodar agora (5 minutos)

```bash
cd giu
pip install -r requirements.txt
cp .env.example .env        # edite e coloque sua OPENAI_API_KEY

# Conversar no terminal:
python cli.py

# Ou subir o servidor (web + WhatsApp):
uvicorn server:app --host 0.0.0.0 --port 8000
```

Teste a porta web:

```bash
curl -X POST localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id": "nanda_001", "message": "Giu, preciso marcar mamografia"}'
```

## Conectar o WhatsApp (porta oficial da Meta)

1. Crie um app em [developers.facebook.com](https://developers.facebook.com) → tipo **Business** → adicione o produto **WhatsApp**
2. Na aba *API Setup*, copie o **token temporário** e o **Phone number ID** para o `.env`
3. Suba o servidor num lugar com URL pública (Railway, como o basexcare-bot, funciona)
4. Em *Configuration → Webhook*, cadastre `https://SEU-DOMINIO/webhook/whatsapp` com o verify token `giu-bazex` e assine o campo `messages`
5. Mande um "oi" para o número de teste — a Giu responde 💛

## Conectar o Telegram

1. No Telegram, fale com o [@BotFather](https://t.me/BotFather) → `/newbot` (ou use um bot existente) e copie o token para `TELEGRAM_BOT_TOKEN` no `.env`
2. Com o servidor no ar, registre o webhook (uma vez):
   ```bash
   curl "https://api.telegram.org/bot<SEU_TOKEN>/setWebhook?url=https://SEU-DOMINIO/webhook/telegram"
   ```
3. Mande uma mensagem para o bot — a Giu responde, com a mesma memória dos outros canais

## Conectar o Google Calendar

1. Em [console.cloud.google.com](https://console.cloud.google.com): crie um projeto → ative a **Google Calendar API** → em *APIs & Services → Credentials*, crie um **OAuth client ID** (tipo *Web application*, com `https://developers.google.com/oauthplayground` como redirect URI autorizado)
2. No [OAuth Playground](https://developers.google.com/oauthplayground): clique na engrenagem → marque *Use your own OAuth credentials* e cole client ID/secret → no passo 1, autorize o escopo `https://www.googleapis.com/auth/calendar` → no passo 2, clique em *Exchange authorization code for tokens* e copie o **refresh token**
3. Preencha `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `GOOGLE_REFRESH_TOKEN` no `.env`
4. Pronto: "Giu, marca dentista sexta às 14h" cria o evento no seu calendário de verdade

## Roadmap (depois do MVP)

- **Alexa / Apple Watch** — são só novas portas; o cérebro não muda
- **Uber / iFood** — novas ferramentas em `giu/tools.py`
- **Memória vetorial** — busca semântica nos fatos quando passarem de centenas
- **Identidade unificada** — ligar o mesmo usuário entre canais (hoje cada canal tem sua identidade)

## Estrutura

```text
giu/
├── server.py            # FastAPI: portas web + WhatsApp + scheduler
├── cli.py               # porta terminal
├── giu/
│   ├── brain.py         # o cérebro (loop de agente)
│   ├── memory.py        # a Memória da Vida (SQLite)
│   ├── tools.py         # as mãos (ferramentas do agente)
│   ├── config.py        # variáveis de ambiente
│   ├── channels/
│   │   ├── whatsapp.py  # Meta WhatsApp Cloud API
│   │   └── telegram.py  # Telegram Bot API
│   └── integrations/
│       └── google_calendar.py  # agenda real (OAuth)
└── requirements.txt
```
