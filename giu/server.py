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

from giu import brain, config, memory, modes, routines, voice
from giu.channels import telegram, whatsapp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("giu")


async def reminder_loop():
    """Proatividade: a cada 60s, envia lembretes vencidos pelo canal de origem.
    Cada lembrete é isolado: a falha de um NUNCA aborta a fila dos outros, e uma
    falha persistente (ex.: janela de 24h do WhatsApp fechada) desiste após N
    tentativas em vez de retentar para sempre."""
    while True:
        for r in memory.due_reminders():
            try:
                # Recorrente: a pergunta gentil de re-consentimento viaja NA
                # mensagem quando é a vez dela (cerca da Life Architect)
                text = (f"✦ Lembrete: {r['text']}" + memory.atraso_grave(r)
                        + memory.pulso_devido(r))
                if r["channel"] == "whatsapp" and whatsapp.is_configured():
                    await whatsapp.send_message(r["user_id"], text)
                    # R3: o histórico PRECISA saber o que saiu — senão o
                    # "pode parar" da pessoa não tem referente e a promessa quebra
                    memory.save_message(r["user_id"], "assistant", text, "whatsapp")
                    memory.reminder_delivered(r)
                    log.info("Lembrete %s enviado via WhatsApp", r["id"])
                elif r["channel"] == "telegram" and telegram.is_configured():
                    await telegram.send_message(r["user_id"], text)
                    memory.save_message(r["user_id"], "assistant", text, "telegram")
                    memory.reminder_delivered(r)
                    log.info("Lembrete %s enviado via Telegram", r["id"])
                else:
                    # Canais sem push (web/cli): entregue na próxima conversa
                    memory.save_message(r["user_id"], "assistant", text, r["channel"])
                    memory.reminder_delivered(r)
                    log.info("Lembrete %s registrado no histórico", r["id"])
            except Exception:
                # Falha de entrega (ex.: 24h fechada): conta a tentativa e segue
                desistiu = memory.mark_reminder_failed(r["id"])
                log.warning("Lembrete %s falhou (%s)", r["id"],
                            "desistido após N tentativas" if desistiu else "vai retentar")
        await asyncio.sleep(60)


async def _send_push(user_id, channel, text):
    if channel == "whatsapp" and whatsapp.is_configured():
        await whatsapp.send_message(user_id, text)
        # Descoberta nº 2 da Voice Architect: o gesto mais de-família (o
        # check-in que chega sem ser chamado) era MUDO até para quem escolheu
        # voz. Agora o "bom dia" também fala — texto sempre primeiro, como manda a lei.
        if (config.VOICE_ENABLED and config.VOICE_REPLIES
                and memory.voice_pref(user_id) in ("voice", "both")):
            hora = datetime.now(ZoneInfo(config.TIMEZONE)).hour
            momento = "modo_manha" if 5 <= hora < 12 else "modo_noite"
            audio = await asyncio.to_thread(voice.sintetizar, text, momento)
            if audio:
                await asyncio.to_thread(whatsapp.send_audio, user_id, audio)
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
                    # Só com CONSENTIMENTO de fato concedido (o valor, não a etapa):
                    # quem recusou não recebe proativo. E onboarding precisa estar completo.
                    if data.get("consentimento") is not True:
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
    errors, warnings = config.startup_issues()
    for w in warnings:
        log.warning("Configuração: %s", w)
    if errors:
        for e in errors:
            log.error("Configuração: %s", e)
        raise RuntimeError("Configuração insegura — corrija as variáveis acima: " + " | ".join(errors))
    memory.init_db()
    tasks = [asyncio.create_task(reminder_loop()), asyncio.create_task(checkin_loop())]
    yield
    for t in tasks:
        t.cancel()


import giu as _giu

app = FastAPI(title="Giu — BazeX", version=_giu.__version__, lifespan=lifespan)


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

# Falha honesta (lição do incidente do piloto): se o cérebro quebrar, a pessoa
# recebe uma resposta honesta — NUNCA silêncio, em NENHUM canal.
HONEST_FAILURE = (
    "Me perdi agora por um instante… pode mandar de novo? "
    "Se eu continuar assim, me chama daqui a pouquinho que eu volto."
)


def _think_safe(user_id, message, channel, via="text"):
    """brain.think com falha honesta — o caminho único de TODOS os canais."""
    try:
        return brain.think(user_id, message, channel=channel, via=via)
    except Exception:
        log.exception("Turno falhou para %s (conteúdo não vai ao log)", user_id)
        return HONEST_FAILURE


def pending_welcome(user_id):
    """Texto de boas-vindas aprovado pela operadora, se for o primeiro contato.

    A abertura é o momento mais delicado do vínculo: quando existe um texto
    aprovado, ele é enviado VERBATIM (determinístico); da segunda mensagem em
    diante, o cérebro assume com o onboarding normal."""
    member = memory.get_member(user_id)
    if member and member.get("welcome") and memory.message_count(user_id) == 0:
        return member["welcome"]
    return None


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
    return {"reply": _think_safe(req.user_id, req.message, "web")}


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


@app.delete("/memories/{user_id}", dependencies=[Depends(require_self)])
def delete_all_memories(user_id: str):
    """Apagamento total: fatos, conversas, agenda, lembretes e ações. 'Apagou,
    sumiu' de verdade — inclusive o histórico episódico, que antes reentrava no
    contexto. Não remove o cadastro de membro (isso é feito à parte)."""
    counts = memory.forget_user(user_id)
    return {"apagado": counts}


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
    welcome: str | None = None  # abertura personalizada aprovada pela operadora


@app.post("/family/members", dependencies=[Depends(require_token)])
def add_family_member(req: MemberRequest):
    token = memory.add_member(req.user_id, req.name, req.role, req.emergency_contact, req.welcome)
    return {
        "user_id": req.user_id,
        "name": req.name,
        "token": token,
        "aviso": "Guarde este token pessoal AGORA — ele não será mostrado de novo.",
    }


@app.get("/family/members", dependencies=[Depends(require_token)])
def family_members():
    return {"members": memory.list_members()}


class VidaRequest(BaseModel):
    """CC5 (fundadora): semear identidade + VIDA. Conteúdo vem da FICHA
    (FICHA-VIDA-INICIAL.md) preenchida pela família — e JAMAIS entra no git."""
    pessoas: list[str] = []
    projetos: list[str] = []
    objetivos: list[str] = []
    rotina: list[str] = []
    preferencias: list[str] = []
    contexto: list[str] = []
    friccoes: list[str] = []
    interesses: list[str] = []   # o que a pessoa AMA (convites de conexão)
    sonhos: list[str] = []       # o que quer construir nos próximos anos
    desafios: list[str] = []     # onde crescer — cuidar sem julgamento
    datas: list[dict] = []  # {titulo, data 'MM-DD'|'YYYY-MM-DD', recorrente?}


@app.post("/family/members/{user_id}/vida", dependencies=[Depends(require_token)])
def seed_member_life(user_id: str, req: VidaRequest):
    if not memory.get_member(user_id):
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    plantados = memory.seed_life(user_id, req.model_dump())
    bloqueado = memory.get_profile(user_id)["data"].get("consentimento") is False
    return {"user_id": user_id, "semeado": plantados,
            "bloqueado_por_consentimento": bloqueado,  # S6: 0 ≠ recusa
            "nota": "Fatos entram com '[de partida]' — hipótese de contexto; "
                    "o que a pessoa mostrar vivendo prevalece e substitui. "
                    "Se a pessoa recusar consentimento, TODO o semeio é expurgado."}


@app.delete("/family/members/{user_id}", dependencies=[Depends(require_token)])
def delete_family_member(user_id: str):
    if not memory.remove_member(user_id):
        raise HTTPException(status_code=404, detail="Membro não encontrado")
    return {"removed": user_id, "nota": "A memória da pessoa NÃO foi apagada; apague a pedido dela via /memories."}


# ─── Life Connector: Google (callback do consentimento OAuth) ────────────────

@app.get("/connectors/google/callback")
def google_oauth_callback(code: str = "", state: str = ""):
    """A pessoa clicou no link que a Giu mandou, autorizou no Google e caiu
    aqui. Estado de uso único + validade 15 min; o refresh token fica no perfil
    DELA (revogável na conversa: 'desconecta minha agenda')."""
    from giu.integrations import google_calendar
    user_id = memory.oauth_state_take(state)
    if not user_id or not code:
        return Response("Esse link não vale mais — pede um novo pra Giu, tá? 💛",
                        media_type="text/plain; charset=utf-8", status_code=400)
    try:
        refresh = google_calendar.exchange_code(code)
    except Exception:
        log.exception("Troca de código Google falhou para %s", user_id)
        refresh = ""
    if not refresh:
        return Response("Não deu certo agora. Pede um link novo pra Giu que a gente tenta de novo. 💛",
                        media_type="text/plain; charset=utf-8", status_code=502)
    memory.google_connect(user_id, refresh)
    log.info("Agenda Google conectada para %s", user_id)
    return Response("Prontinho! Sua agenda está conectada. Pode voltar pra conversa com a Giu. 💛",
                    media_type="text/plain; charset=utf-8")


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


# Processamento em BACKGROUND (opção B): o webhook responde 200 na hora e o
# turno pesado (pensar + STT/TTS) roda numa thread, sem travar os outros membros.
_bg_tasks = set()


def _should_send_audio(number, via):
    """Decide o áudio de forma DETERMINÍSTICA (não pelo modelo), respeitando a
    preferência de relacionamento da pessoa:
    - 'text'  → nunca áudio (ela pediu só escrito; cumprido 100% das vezes)
    - 'voice'/'both' → sempre áudio (ela escolheu ouvir a Giu)
    - None (ainda não escolheu) → espelha o canal: só manda áudio se o turno veio por voz.
    O texto SEMPRE acompanha (em _reply_blocking); isto decide apenas o áudio."""
    if not (config.VOICE_ENABLED and config.VOICE_REPLIES):
        return False
    pref = memory.voice_pref(number)
    if pref == "text":
        return False
    if pref in ("voice", "both"):
        return True
    return via == "voice"


def _reply_blocking(number, reply, via, momento=None):
    """Envia a resposta: SEMPRE texto (registro relegível + fallback se o TTS
    falhar) e, conforme a preferência da pessoa, também o áudio — com a
    energia do momento (Sprint da Voz)."""
    whatsapp.send_message_sync(number, reply)
    if _should_send_audio(number, via):
        audio = voice.sintetizar(reply, momento)
        if audio:
            whatsapp.send_audio(number, audio)


def _turn_blocking(number, text, via):
    """Um turno inteiro (SÍNCRONO — roda numa thread do background).
    FALHA HONESTA: se o cérebro quebrar (ex.: provedor de IA fora), a pessoa
    recebe uma resposta honesta — nunca silêncio (lição do incidente do piloto)."""
    welcome = pending_welcome(number)
    if welcome:
        memory.save_message(number, "user", text, "whatsapp", modality=via)
        memory.save_message(number, "assistant", welcome, "whatsapp")
        _reply_blocking(number, welcome, via)
        return
    # A energia da voz acompanha o momento do turno (Sprint da Voz)
    momento = modes.detect(text, datetime.now(ZoneInfo(config.TIMEZONE)).hour)
    _reply_blocking(number, _think_safe(number, text, "whatsapp", via), via, momento)


def _audio_turn_blocking(number, media_id):
    """Baixa o áudio, transcreve e processa como turno normal (SÍNCRONO).
    Falha NUNCA é um beco sem saída para quem só usa voz: o aviso vai também em
    áudio (via _reply_blocking) e convida a tentar DE NOVO por voz — escrever é
    uma alternativa oferecida, jamais a única porta."""
    audio_bytes = whatsapp.download_media(media_id)
    if not audio_bytes:
        _reply_blocking(number,
            "Acho que seu áudio não chegou inteiro. Pode mandar de novo? Se for mais "
            "fácil, pode escrever também — como for melhor pra você.", via="voice")
        return
    text = voice.transcrever(audio_bytes)
    if not text:
        _reply_blocking(number,
            "Desculpa, não consegui te ouvir direito dessa vez. Tenta de novo, pertinho e "
            "devagar, que eu te escuto. Se preferir, pode escrever — o que for mais fácil.", via="voice")
        return
    _turn_blocking(number, text, via="voice")


def _dispatch(fn, *args):
    """Roda uma função bloqueante numa thread, em background, sem travar o loop."""
    task = asyncio.create_task(asyncio.to_thread(fn, *args))
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


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

    # Texto ou áudio?
    parsed = whatsapp.parse_incoming(payload)
    audio = whatsapp.parse_incoming_audio(payload) if not parsed else None
    if not parsed and not audio:
        return {"status": "ok"}

    number, msg_id = (parsed[0], parsed[2]) if parsed else (audio[0], audio[2])

    # Dedup: a Meta reenvia webhooks; idempotência por id da mensagem (wamid).
    if msg_id and memory.already_processed(f"wa:{msg_id}"):
        log.info("WhatsApp: mensagem duplicada ignorada")
        return {"status": "ok"}
    if not family_gate(number):
        log.info("WhatsApp de número não registrado — recusado sem processar")
        await whatsapp.send_message(number, DECLINE_MESSAGE)
        return {"status": "ok"}

    if parsed:
        text = parsed[1]
        log.info("WhatsApp: mensagem de %s (%d caracteres)", number, len(text))
        _dispatch(_turn_blocking, number, text, "text")
    else:
        log.info("WhatsApp: áudio de %s", number)
        _dispatch(_audio_turn_blocking, number, audio[1])
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
        # O chat_id é a identidade da pessoa no cérebro (com falha honesta)
        reply = _think_safe(chat_id, text, "telegram")
        await telegram.send_message(chat_id, reply)
    return {"status": "ok"}
