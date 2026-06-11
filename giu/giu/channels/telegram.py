"""
Porta Telegram — integração via Bot API oficial.

Fluxo:
1. Telegram envia updates para o webhook (POST /webhook/telegram)
2. Extraímos o texto e o chat de quem mandou
3. O cérebro pensa (brain.think) — a memória é a mesma de todos os canais
4. Respondemos pela Bot API

Setup (uma vez): criar o bot no @BotFather, colocar TELEGRAM_BOT_TOKEN no .env
e registrar o webhook — ver README.
"""

import httpx

from .. import config


def _api(method):
    return f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/{method}"


def is_configured():
    return bool(config.TELEGRAM_BOT_TOKEN)


def parse_incoming(payload):
    """Extrai (chat_id, texto) de um update do Telegram. None se não for mensagem de texto."""
    message = payload.get("message") or payload.get("edited_message")
    if not message or "text" not in message:
        return None
    return str(message["chat"]["id"]), message["text"]


async def send_message(chat_id, text):
    """Envia uma mensagem de texto para um chat via Bot API."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _api("sendMessage"),
            json={"chat_id": chat_id, "text": text},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()


async def set_webhook(url):
    """Registra a URL do webhook no Telegram (chamar uma vez após o deploy)."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(_api("setWebhook"), json={"url": url}, timeout=30)
        resp.raise_for_status()
        return resp.json()
