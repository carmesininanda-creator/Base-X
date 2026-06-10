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
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

from giu import brain, config, memory
from giu.channels import whatsapp

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


@app.get("/")
def status():
    return {
        "giu": "online",
        "tagline": "Você não precisa segurar tudo sozinha. Eu estou aqui.",
        "canais": {"web": True, "whatsapp": whatsapp.is_configured()},
    }


# ─── Porta Web ────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    reply = brain.think(req.user_id, req.message, channel="web")
    return {"reply": reply}


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
    payload = await request.json()
    parsed = whatsapp.parse_incoming(payload)
    if parsed:
        number, text = parsed
        log.info("WhatsApp de %s: %s", number, text)
        # O número de telefone é a identidade da pessoa no cérebro
        reply = brain.think(number, text, channel="whatsapp")
        await whatsapp.send_message(number, reply)
    return {"status": "ok"}
