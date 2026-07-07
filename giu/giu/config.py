"""Configuração central da Giu — tudo vem de variáveis de ambiente."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ─── IA ───────────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ─── Memória ──────────────────────────────────────────────────────────────────
DB_PATH = os.getenv("GIU_DB_PATH", str(Path(__file__).resolve().parent.parent / "giu_memory.db"))

# ─── Segurança ────────────────────────────────────────────────────────────────
# Token de operadora: gerencia membros; em modo família NÃO lê memória de ninguém
GIU_API_TOKEN = os.getenv("GIU_API_TOKEN", "")

# ─── Modo Família ─────────────────────────────────────────────────────────────
# 1 = só membros registrados conversam; memória via API exige token pessoal
FAMILY_MODE = os.getenv("GIU_FAMILY_MODE", "0") == "1"

# ─── WhatsApp Cloud API (Meta) ────────────────────────────────────────────────
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "giu-bazex")
# App Secret da Meta — valida a assinatura X-Hub-Signature-256 dos webhooks
META_APP_SECRET = os.getenv("META_APP_SECRET", "")

# ─── Telegram Bot API ─────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Secret enviado pelo Telegram no header X-Telegram-Bot-Api-Secret-Token
TELEGRAM_SECRET_TOKEN = os.getenv("TELEGRAM_SECRET_TOKEN", "")

# ─── Google Calendar (OAuth com refresh token) ────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")

# ─── Voz (identidade sonora — 100% configurável) ──────────────────────────────
# A voz definitiva da Giu será decidida por teste de percepção com usuários.
# 'shimmer' é apenas o PADRÃO DO PILOTO — o mais alinhado ao parecer da
# psicóloga (calor contido, calma, presença). Trocar = mudar só estas variáveis.
VOICE_ENABLED = os.getenv("GIU_VOICE_ENABLED", "1") == "1"
VOICE_NAME = os.getenv("GIU_VOICE", "shimmer")           # timbre do TTS
VOICE_SPEED = float(os.getenv("GIU_VOICE_SPEED", "0.92"))  # ~0,9x: "tenho tempo pra você"
TTS_MODEL = os.getenv("GIU_TTS_MODEL", "tts-1")
STT_MODEL = os.getenv("GIU_STT_MODEL", "whisper-1")
# Quando a pessoa manda áudio, a Giu responde em áudio (espelha o canal)
VOICE_REPLIES = os.getenv("GIU_VOICE_REPLIES", "1") == "1"

# ─── URL pública do serviço (callbacks OAuth dos Life Connectors) ─────────────
BASE_URL = os.getenv("GIU_BASE_URL", "")

# ─── Geral ────────────────────────────────────────────────────────────────────
TIMEZONE = os.getenv("GIU_TIMEZONE", "America/Sao_Paulo")

# ─── Check-in diário (horário local HH:MM) ────────────────────────────────────
MORNING_CHECKIN = os.getenv("GIU_MORNING_CHECKIN", "08:00")
NIGHT_CHECKIN = os.getenv("GIU_NIGHT_CHECKIN", "21:00")


def startup_issues():
    """Valida a configuração na inicialização.

    Retorna (erros, avisos). Erros impedem o servidor de subir — são
    combinações inseguras. Avisos degradam funcionalidade, mas não segurança.
    """
    errors, warnings = [], []

    if FAMILY_MODE and not GIU_API_TOKEN:
        errors.append(
            "GIU_FAMILY_MODE=1 exige GIU_API_TOKEN: sem ele, os endpoints de "
            "cadastro da família ficariam abertos a qualquer pessoa."
        )

    if not OPENAI_API_KEY:
        warnings.append("OPENAI_API_KEY ausente — a Giu não conseguirá pensar nem responder.")
    if not GIU_API_TOKEN:
        warnings.append("GIU_API_TOKEN ausente — API aberta (aceitável apenas em desenvolvimento).")
    if WHATSAPP_TOKEN and not META_APP_SECRET:
        warnings.append(
            "WhatsApp configurado sem META_APP_SECRET — webhooks não terão a assinatura validada."
        )
    if TELEGRAM_BOT_TOKEN and not TELEGRAM_SECRET_TOKEN:
        warnings.append(
            "Telegram configurado sem TELEGRAM_SECRET_TOKEN — webhooks não terão o secret validado."
        )
    if not WHATSAPP_TOKEN and not TELEGRAM_BOT_TOKEN:
        warnings.append("Nenhum canal de mensagens configurado — apenas a porta web estará ativa.")

    return errors, warnings
