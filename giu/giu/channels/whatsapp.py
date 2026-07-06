"""
Porta WhatsApp — integração oficial via Meta WhatsApp Cloud API.

Fluxo:
1. Meta envia mensagens recebidas para o webhook (POST /webhook/whatsapp)
2. Extraímos o texto e o número de quem mandou
3. O cérebro pensa (brain.think) — a memória é a mesma de todos os canais
4. Respondemos pela Graph API

Setup (uma vez): ver README — criar app na Meta, pegar token e phone_id,
apontar o webhook para este servidor.
"""

import httpx

from .. import config

GRAPH_URL = "https://graph.facebook.com/v21.0"


def is_configured():
    return bool(config.WHATSAPP_TOKEN and config.WHATSAPP_PHONE_ID)


def parse_incoming(payload):
    """Extrai (numero, texto, msg_id) de um webhook de TEXTO da Meta.
    msg_id (wamid) permite deduplicar reenvios. Retorna None se não for texto."""
    try:
        change = payload["entry"][0]["changes"][0]["value"]
        message = change["messages"][0]
        if message.get("type") != "text":
            return None
        return message["from"], message["text"]["body"], message.get("id")
    except (KeyError, IndexError):
        return None


def parse_incoming_audio(payload):
    """Extrai (numero, media_id, msg_id) de um webhook de ÁUDIO/nota de voz.
    Retorna None se não for áudio."""
    try:
        change = payload["entry"][0]["changes"][0]["value"]
        message = change["messages"][0]
        if message.get("type") != "audio":
            return None
        return message["from"], message["audio"]["id"], message.get("id")
    except (KeyError, IndexError):
        return None


def download_media(media_id):
    """Baixa a mídia da Meta (2 passos: media_id → url → bytes).
    Retorna os bytes ou None em falha."""
    if not is_configured():
        return None
    try:
        headers = {"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"}
        meta = httpx.get(f"{GRAPH_URL}/{media_id}", headers=headers, timeout=30)
        meta.raise_for_status()
        url = meta.json()["url"]
        blob = httpx.get(url, headers=headers, timeout=60)
        blob.raise_for_status()
        return blob.content
    except Exception:
        return None


def send_audio(to, audio_bytes, mime="audio/ogg"):
    """Envia áudio (2 passos: upload da mídia → mensagem type=audio).
    Retorna True se entregue, False em qualquer falha — nunca levanta."""
    if not is_configured():
        return False
    try:
        up = httpx.post(
            f"{GRAPH_URL}/{config.WHATSAPP_PHONE_ID}/media",
            headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
            data={"messaging_product": "whatsapp", "type": mime},
            files={"file": ("giu.ogg", audio_bytes, mime)},
            timeout=60,
        )
        up.raise_for_status()
        media_id = up.json()["id"]
        send = httpx.post(
            f"{GRAPH_URL}/{config.WHATSAPP_PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
            json={"messaging_product": "whatsapp", "to": to, "type": "audio",
                  "audio": {"id": media_id}},
            timeout=30,
        )
        send.raise_for_status()
        return True
    except Exception:
        return False


def _payload(to, text):
    return {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}


async def send_message(to, text):
    """Envia uma mensagem de texto para um número via Cloud API."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_URL}/{config.WHATSAPP_PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
            json=_payload(to, text),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


def send_message_sync(to, text):
    """Envio síncrono, para fluxos que não podem esperar o scheduler (emergência).
    Retorna True se entregue, False em qualquer falha — nunca levanta exceção."""
    if not is_configured():
        return False
    try:
        resp = httpx.post(
            f"{GRAPH_URL}/{config.WHATSAPP_PHONE_ID}/messages",
            headers={"Authorization": f"Bearer {config.WHATSAPP_TOKEN}"},
            json=_payload(to, text),
            timeout=30,
        )
        resp.raise_for_status()
        return True
    except Exception:
        return False
