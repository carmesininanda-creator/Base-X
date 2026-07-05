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

from datetime import datetime
from zoneinfo import ZoneInfo

from giu import brain, config, memory, routines
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


async def _send_push(user_id, channel, text):
    if channel == "whatsapp" and whatsapp.is_configured():
        await whatsapp.send_message(user_id, text)
    elif channel == "telegram" and telegram.is_configured():
        await telegram.send_message(user_id, text)
    else:
        return False
    memory.save_message(user_id, "assistant", text, channel)
    return True


async def checkin_loop():
    """Check-in diário: a Giu aparece de manhã e à noite, sem ser chamada."""
    while True:
        try:
            now = datetime.now(ZoneInfo(config.TIMEZONE))
            hhmm, today = now.strftime("%H:%M"), now.date().isoformat()
            period = "manha" if hhmm == config.MORNING_CHECKIN else (
                "noite" if hhmm == config.NIGHT_CHECKIN else None)
            if period:
                for user_id, channel in memory.push_users():
                    profile = memory.get_profile(user_id)
                    data = profile["data"]
                    # Só após onboarding completo, com check-in não desativado, 1x por dia
                    if not data.get("onboarding", {}).get("consentimento"):
                        continue
                    if data.get("checkin") is False or data.get(f"checkin_{period}") == today:
                        continue
                    text = (routines.morning_message(user_id) if period == "manha"
                            else routines.night_message(user_id))
                    if await _send_push(user_id, channel, text):
                        memory.set_profile(user_id, **{f"checkin_{period}": today})
                        log.info("Check-in %s enviado para %s via %s", period, user_id, channel)
        except Exception:
            log.exception("Erro no loop de check-in")
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app):
    memory.init_db()
    tasks = [asyncio.create_task(reminder_loop()), asyncio.create_task(checkin_loop())]
    yield
    for t in tasks:
        t.cancel()


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


def require_self(user_id: str, authorization: str = Header(default="")):
    """Acesso à memória: em modo família, SÓ o token pessoal do próprio usuário.
    O token de operadora não lê memória de ninguém. Fora do modo família, vale o token geral."""
    if not config.FAMILY_MODE:
        return require_token(authorization)
    token = authorization.removeprefix("Bearer ").strip()
    member = memory.get_member_by_token(token) if token else None
    if not member or member["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Apenas a própria pessoa acessa sua memória")


def family_gate(user_id):
    """Portaria do modo família: True se a pessoa pode conversar com a Giu."""
    if not config.FAMILY_MODE:
        return True
    member = memory.get_member(user_id)
    if not member:
        return False
    if member["status"] != "active":
        memory.activate_member(user_id)
    return True


DECLINE_MESSAGE = (
    "Oi! Eu sou a Giu, uma assistente pessoal de família — e este espaço é só dos "
    "membros cadastrados. Não vou guardar nada do que você enviou. 💛"
)


@app.get("/")
def status():
    from giu.integrations import google_calendar
    return {
        "giu": "online",
        "tagline": "Você não precisa segurar tudo sozinha. Eu estou aqui.",
        "modo_familia": config.FAMILY_MODE,
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


@app.post("/chat")
def chat(req: ChatRequest, authorization: str = Header(default="")):
    # Em modo família, só a própria pessoa conversa em seu nome (token pessoal)
    require_self(req.user_id, authorization)
    reply = brain.think(req.user_id, req.message, channel="web")
    return {"reply": reply}


# ─── Governança da memória (os dados pertencem à pessoa) ─────────────────────
# Em modo família estes endpoints exigem o token PESSOAL do próprio usuário;
# o token de operadora não lê a memória de ninguém.

@app.get("/memories/{user_id}", dependencies=[Depends(require_self)])
def list_memories(user_id: str):
    return {"facts": memory.get_facts(user_id, limit=500)}


@app.delete("/memories/{user_id}/{fact_id}", dependencies=[Depends(require_self)])
def delete_memory(user_id: str, fact_id: int):
    if not memory.delete_fact(user_id, fact_id):
        raise HTTPException(status_code=404, detail="Fato não encontrado")
    return {"deleted": fact_id}


@app.get("/pending-actions/{user_id}", dependencies=[Depends(require_self)])
def pending_actions(user_id: str):
    return {"pending": memory.list_pending_actions(user_id)}


@app.get("/summary/{user_id}", dependencies=[Depends(require_self)])
def summary(user_id: str):
    """Resumo diário: pendências, lembretes, agenda, saúde + um cuidado."""
    return routines.daily_summary(user_id)


# ─── Família (cadastro — token de operadora; nunca dá acesso a memória) ──────

class MemberRequest(BaseModel):
    user_id: str
    name: str
    role: str = "member"
    emergency_contact: str | None = None


@app.post("/family/members", dependencies=[Depends(require_token)])
def add_family_member(req: MemberRequest):
    token = memory.add_member(req.user_id, req.name, req.role, req.emergency_contact)
    return {
        "user_id": req.user_id,
        "name": req.name,
        "token": token,
        "aviso": "Guarde este token pessoal AGORA — ele não será mostrado de novo.",
    }


@app.get("/family/members", dependencies=[Depends(require_token)])
def family_members():
    return {"members": memory.list_members()}


@app.delete("/family/members/{user_id}", dependencies=[Depends(require_token)])
def delete_family_member(user_id: str):
    if not memory.remove_member(user_id):
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return {"removed": user_id, "nota": "A memória da pessoa NÃO foi apagada; apague a pedido dela via /memories."}


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
        if not family_gate(number):
            log.info("WhatsApp de número não registrado — recusado sem processar")
            await whatsapp.send_message(number, DECLINE_MESSAGE)
            return {"status": "ok"}
        # Metadados apenas — conteúdo de conversa NUNCA vai para logs
        log.info("WhatsApp: mensagem de %s (%d caracteres)", number, len(text))
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
        if not family_gate(chat_id):
            log.info("Telegram de chat não registrado — recusado sem processar")
            await telegram.send_message(chat_id, DECLINE_MESSAGE)
            return {"status": "ok"}
        # Metadados apenas — conteúdo de conversa NUNCA vai para logs
        log.info("Telegram: mensagem de %s (%d caracteres)", chat_id, len(text))
        # O chat_id é a identidade da pessoa no cérebro
        reply = brain.think(chat_id, text, channel="telegram")
        await telegram.send_message(chat_id, reply)
    return {"status": "ok"}
