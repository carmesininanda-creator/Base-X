"""
Voz da Giu — componente de canal, configurável e desacoplado.

A voz NÃO é um motor novo: é a casca de entrada/saída do canal. O cérebro
(brain.think) continua recebendo texto e devolvendo texto; aqui só acontece
a transformação áudio↔texto e a preparação do texto para soar humano.

Toda a identidade sonora (timbre, velocidade, modelos) vem de config —
trocar a voz definitiva no futuro é mudar variáveis de ambiente, nada mais.

Segue o parecer da psicóloga cognitiva:
- diretriz 1 (voz-âncora): preset único e calmo, vindo de config
- diretriz 2 (escrever para o ouvido): vocefy() antes do TTS
"""

import io
import re

from openai import OpenAI

from . import config

_URL = re.compile(r"https?://\S+")
_HORA = re.compile(r"\b(\d{1,2}):(\d{2})\b")
_DATA = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")


def _client():
    return OpenAI(api_key=config.OPENAI_API_KEY)


def transcrever(audio_bytes, filename="audio.ogg"):
    """STT: áudio → texto. Retorna o texto ou None em falha (nunca levanta)."""
    if not config.OPENAI_API_KEY:
        return None
    try:
        f = io.BytesIO(audio_bytes)
        f.name = filename  # a API infere o formato pelo nome
        resp = _client().audio.transcriptions.create(model=config.STT_MODEL, file=f)
        return (resp.text or "").strip() or None
    except Exception:
        return None


def sintetizar(texto):
    """TTS: texto → bytes de áudio (Opus, formato de nota de voz do WhatsApp).
    Retorna os bytes ou None em falha (nunca levanta)."""
    if not config.OPENAI_API_KEY:
        return None
    try:
        resp = _client().audio.speech.create(
            model=config.TTS_MODEL,
            voice=config.VOICE_NAME,
            speed=config.VOICE_SPEED,
            input=vocefy(texto),
            response_format="opus",
        )
        return resp.read()
    except Exception:
        return None


def vocefy(texto):
    """Prepara o texto para o OUVIDO (diretriz 2 da psicóloga): tira emoji e
    markdown, e expande números/horas/datas para forma falada — para o TTS não
    soar robótico. NÃO reescreve o conteúdo (isso é papel do prompt); só limpa a
    superfície que o TTS lê mal. Reticências e travessões são mantidos (viram
    pausa no TTS)."""
    t = texto
    # Emoji e símbolos que o TTS verbaliza mal
    t = _remove_emoji(t)
    t = t.replace("**", "").replace("*", "").replace("`", "").replace("#", "")
    t = _URL.sub("(link enviado por mensagem)", t)
    t = t.replace("R$", "").replace("%", " por cento")
    # Horas: 15:00 → "15 horas"; 15:30 → "15 e 30"
    t = _HORA.sub(lambda m: f"{int(m.group(1))} horas" if m.group(2) == "00"
                  else f"{int(m.group(1))} e {int(m.group(2))}", t)
    # Datas: 19/07 → "dia 19 do 7"
    t = _DATA.sub(lambda m: f"dia {int(m.group(1))} do {int(m.group(2))}", t)
    # Espaços redundantes
    return re.sub(r"[ \t]{2,}", " ", t).strip()


def _remove_emoji(t):
    return "".join(c for c in t if c == "\n" or c == "…" or ord(c) < 0x1F000 and not (0x2600 <= ord(c) <= 0x27BF))
