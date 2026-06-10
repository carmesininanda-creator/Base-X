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

# ─── WhatsApp Cloud API (Meta) ────────────────────────────────────────────────
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "giu-bazex")

# ─── Geral ────────────────────────────────────────────────────────────────────
TIMEZONE = os.getenv("GIU_TIMEZONE", "America/Sao_Paulo")
