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

# ─── Geral ────────────────────────────────────────────────────────────────────
TIMEZONE = os.getenv("GIU_TIMEZONE", "America/Sao_Paulo")

# ─── Check-in diário (horário local HH:MM) ────────────────────────────────────
MORNING_CHECKIN = os.getenv("GIU_MORNING_CHECKIN", "08:00")
NIGHT_CHECKIN = os.getenv("GIU_NIGHT_CHECKIN", "21:00")
