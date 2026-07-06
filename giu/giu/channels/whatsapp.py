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
    """Extrai (numero, texto, msg_id) de um webhook da Meta.
    msg_id (wamid) permite deduplicar reenvios. Retorna None se não for texto."""
    try:
        change = payload["entry"][0]["changes"][0]["value"]
        message = change["messages"][0]
        if message.get("type") != "text":
            return None
        return message["from"], message["text"]["body"], message.get("id")
    except (KeyError, IndexError):
        return None


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
