"""
Diagnóstico da fronteira OpenAI — incidente "Giulieta não ouve, não fala, não pensa".

RODAR DENTRO DO AMBIENTE DE PRODUÇÃO (com as MESMAS variáveis do serviço):
  - Railway: painel do serviço → aba do container/shell → `python diagnostico_openai.py`
  - ou localmente com o CLI logado no projeto: `railway run python diagnostico_openai.py`

NÃO imprime segredos. Imprime só: presença/formato das variáveis, alcance de rede
e a classe/status EXATOS de cada erro. Copie a saída inteira e cole para o Code.
"""

import os
import socket
import sys
import traceback


def secao(t):
    print(f"\n{'='*60}\n{t}\n{'='*60}")


def resultado(nome, ok, detalhe=""):
    print(f"  [{'OK' if ok else 'FALHA'}] {nome}" + (f" — {detalhe}" if detalhe else ""))


# ─── 1. Variáveis de ambiente (presença e formato, nunca o valor) ─────────────
secao("1. VARIÁVEIS DE AMBIENTE")
key = os.getenv("OPENAI_API_KEY", "")
model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
resultado("OPENAI_API_KEY presente", bool(key), f"len={len(key)}")
if key:
    resultado("sem espaços/aspas/quebra de linha nas pontas",
              key == key.strip().strip('"').strip("'"),
              "ATENÇÃO: a chave tem caractere invisível nas pontas — refazer a variável" if key != key.strip().strip('"').strip("'") else "")
    resultado("prefixo esperado (sk-)", key.strip().startswith("sk-"), f"começa com: {key.strip()[:3]}...")
print(f"  OPENAI_MODEL = {model!r}")
print(f"  GIU_TTS_MODEL = {os.getenv('GIU_TTS_MODEL', '(padrão tts-1)')!r}")
print(f"  GIU_STT_MODEL = {os.getenv('GIU_STT_MODEL', '(padrão whisper-1)')!r}")
print(f"  GIU_VOICE = {os.getenv('GIU_VOICE', '(padrão shimmer)')!r}")

# ─── 2. Biblioteca ────────────────────────────────────────────────────────────
secao("2. AMBIENTE PYTHON")
print(f"  python = {sys.version.split()[0]}")
try:
    import openai
    resultado("import openai", True, f"versão {openai.__version__}")
except Exception as e:
    resultado("import openai", False, f"{type(e).__name__}: {e}")
    print("  → CAUSA RAIZ PROVÁVEL: dependência quebrada no deploy. Saída completa:")
    traceback.print_exc()
    sys.exit(1)

# ─── 3. Rede: o Railway alcança a OpenAI? ─────────────────────────────────────
secao("3. REDE (egress do container)")
try:
    ip = socket.gethostbyname("api.openai.com")
    resultado("DNS api.openai.com", True, ip)
except Exception as e:
    resultado("DNS api.openai.com", False, f"{type(e).__name__}: {e}")
try:
    s = socket.create_connection(("api.openai.com", 443), timeout=10)
    s.close()
    resultado("TCP 443 api.openai.com", True)
except Exception as e:
    resultado("TCP 443 api.openai.com", False, f"{type(e).__name__}: {e}")
    print("  → Se DNS/TCP falham: CAUSA RAIZ = rede/egress, não a chave.")

# ─── 4. Autenticação + os três serviços, um a um ─────────────────────────────
from openai import OpenAI  # noqa: E402
client = OpenAI(api_key=key)


def teste(nome, fn):
    try:
        detalhe = fn()
        resultado(nome, True, detalhe or "")
        return True
    except Exception as e:
        status = getattr(e, "status_code", getattr(getattr(e, "response", None), "status_code", "?"))
        resultado(nome, False, f"{type(e).__name__} (HTTP {status}): {str(e)[:300]}")
        return False


secao("4. AUTENTICAÇÃO (models.list)")
auth_ok = teste("listar modelos (valida a CHAVE)", lambda: f"{len(client.models.list().data)} modelos visíveis")
if not auth_ok:
    print("  → 401 = chave inválida/revogada · 429 = cota/billing · timeout = rede")

secao("5. CÉREBRO (chat.completions)")
teste(f"completions com {model!r}",
      lambda: repr(client.chat.completions.create(
          model=model, max_tokens=5,
          messages=[{"role": "user", "content": "diga oi"}]).choices[0].message.content))
print("  → Se SÓ este falha com 404: OPENAI_MODEL aponta para modelo inexistente.")

secao("6. VOZ — TTS (audio.speech)")
_tts_bytes = {}
def _tts():
    r = client.audio.speech.create(model=os.getenv("GIU_TTS_MODEL", "tts-1"),
                                   voice=os.getenv("GIU_VOICE", "shimmer"),
                                   input="oi, eu sou a Giulieta", response_format="opus")
    _tts_bytes["b"] = r.read()
    return f"{len(_tts_bytes['b'])} bytes de áudio gerados"
teste("sintetizar fala", _tts)

secao("7. OUVIDO — STT (audio.transcriptions)")
def _stt():
    import io
    if "b" not in _tts_bytes:
        return "PULADO (TTS falhou antes — sem áudio para transcrever)"
    f = io.BytesIO(_tts_bytes["b"]); f.name = "diag.ogg"
    r = client.audio.transcriptions.create(model=os.getenv("GIU_STT_MODEL", "whisper-1"), file=f)
    return f"transcrito: {r.text!r}"
teste("transcrever o áudio do passo 6 (loop completo voz→texto)", _stt)

secao("FIM — copie TODA a saída acima e envie para o Code")
