"""
Servidor da Giu — expõe o cérebro para as portas externas.

Rotas:
- GET  /                    → status
- POST /chat                → porta web/app ({"user_id", "message"})
- GET  /webhook/whatsapp    → verificação do webhook (Meta)
- POST /webhook/whatsapp    → mensagens recebidas do WhatsApp

Rodar: uvicorn server:app --host 0.0.0.0 --port 8000
"""

import asyncio
import hashlib
import hmac
import json
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel

from giu import brain, config, memory
from giu.channels import telegram, whatsapp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("giu")


async def reminder_loop():
    """Proatividade: a cada 60s, envia lembretes vencidos pelo canal de origem."""
    while True:
        try:
            for r in memory.due_reminders():
                text = f"✦ Lembrete: {r['text']}"
                if r["channel"] == "whatsapp" and whatsapp.is_configured():
                    await whatsapp.send_message(r["user_id"], text)
                    memory.mark_reminder_sent(r["id"])
                    log.info("Lembrete %s enviado via WhatsApp", r["id"])
                elif r["channel"] == "telegram" and telegram.is_configured():
                    await telegram.send_message(r["user_id"], text)
                    memory.mark_reminder_sent(r["id"])
                    log.info("Lembrete %s enviado via Telegram", r["id"])
                else:
                    # Canais sem push (web/cli): entregue na próxima conversa
                    memory.save_message(r["user_id"], "assistant", text, r["channel"])
                    memory.mark_reminder_sent(r["id"])
                    log.info("Lembrete %s registrado no histórico", r["id"])
        except Exception:
            log.exception("Erro no loop de lembretes")
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app):
    memory.init_db()
    task = asyncio.create_task(reminder_loop())
    yield
    task.cancel()


app = FastAPI(title="Giu — BazeX", version="0.1.0", lifespan=lifespan)


# ─── Autenticação ─────────────────────────────────────────────────────────────

def require_token(authorization: str = Header(default="")):
    """Protege endpoints com Bearer token. Sem GIU_API_TOKEN definido, libera (modo dev)."""
    if not config.GIU_API_TOKEN:
        log.warning("GIU_API_TOKEN não definido — endpoints abertos (use apenas em desenvolvimento)")
        return
    expected = f"Bearer {config.GIU_API_TOKEN}"
    if not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Token inválido ou ausente")


@app.get("/")
def status():
    from giu.integrations import google_calendar
    return {
        "giu": "online",
        "tagline": "Você não precisa segurar tudo sozinha. Eu estou aqui.",
        "canais": {
            "web": True,
            "whatsapp": whatsapp.is_configured(),
            "telegram": telegram.is_configured(),
        },
        "integracoes": {"google_calendar": google_calendar.is_configured()},
    }


# ─── Porta Web ────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.post("/chat", dependencies=[Depends(require_token)])
def chat(req: ChatRequest):
    reply = brain.think(req.user_id, req.message, channel="web")
    return {"reply": reply}


# ─── Governança da memória (os dados pertencem à pessoa) ─────────────────────

@app.get("/memories/{user_id}", dependencies=[Depends(require_token)])
def list_memories(user_id: str):
    return {"facts": memory.get_facts(user_id, limit=500)}


@app.delete("/memories/{user_id}/{fact_id}", dependencies=[Depends(require_token)])
def delete_memory(user_id: str, fact_id: int):
    if not memory.delete_fact(user_id, fact_id):
        raise HTTPException(status_code=404, detail="Fato não encontrado")
    return {"deleted": fact_id}


@app.get("/pending-actions/{user_id}", dependencies=[Depends(require_token)])
def pending_actions(user_id: str):
    return {"pending": memory.list_pending_actions(user_id)}


# ─── Porta WhatsApp ───────────────────────────────────────────────────────────

@app.get("/webhook/whatsapp")
def whatsapp_verify(request: Request):
    """Handshake de verificação exigido pela Meta ao cadastrar o webhook."""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == config.WHATSAPP_VERIFY_TOKEN
    ):
        return Response(content=params.get("hub.challenge", ""), media_type="text/plain")
    return Response(status_code=403)


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    body = await request.body()
    # Valida a assinatura da Meta — rejeita payloads forjados
    if config.META_APP_SECRET:
        signature = request.headers.get("X-Hub-Signature-256", "")
        expected = "sha256=" + hmac.new(
            config.META_APP_SECRET.encode(), body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            log.warning("Webhook WhatsApp com assinatura inválida — descartado")
            return Response(status_code=403)
    payload = json.loads(body)
    parsed = whatsapp.parse_incoming(payload)
    if parsed:
        number, text = parsed
        log.info("WhatsApp de %s: %s", number, text)
        # O número de telefone é a identidade da pessoa no cérebro
        reply = brain.think(number, text, channel="whatsapp")
        await whatsapp.send_message(number, reply)
    return {"status": "ok"}


# ─── Porta Telegram ───────────────────────────────────────────────────────────

@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    # Valida o secret token registrado no setWebhook — rejeita payloads forjados
    if config.TELEGRAM_SECRET_TOKEN:
        received = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(received, config.TELEGRAM_SECRET_TOKEN):
            log.warning("Webhook Telegram com secret inválido — descartado")
            return Response(status_code=403)
    payload = await request.json()
    parsed = telegram.parse_incoming(payload)
    if parsed:
        chat_id, text = parsed
        log.info("Telegram de %s: %s", chat_id, text)
        # O chat_id é a identidade da pessoa no cérebro
        reply = brain.think(chat_id, text, channel="telegram")
        await telegram.send_message(chat_id, reply)
    return {"status": "ok"}
