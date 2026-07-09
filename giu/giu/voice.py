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
# Telefones (com hífen — inambíguo) e números de emergência conhecidos:
# ouvido não relê; telefone se fala DÍGITO A DÍGITO (prescrição V0 da
# Voice Architect), com fôlego entre os grupos.
_TELEFONE = re.compile(r"(?:\+?55[\s.]?)?(?:\(?0?\d{2}\)?[\s.]?)?\d{4,5}-\d{4}\b")
_EMERGENCIA = re.compile(r"\b(188|190|192|193)\b")
_MOEDA = re.compile(r"R\$\s?(\d[\d.]*)(?:,(\d{2}))?")
# Unidades de medida/remédio logo após "n/n" → NÃO é data (protege "1/2 comprimido"
# de virar "dia 1 do 2"). Segurança primeiro: dose nunca pode ser lida como data.
_MEDIDA = (r"(?!\s*(?:comprimidos?|comp\b|c[áa]psulas?|caps?\b|colher(?:es)?|colh|"
           r"doses?|g[oa]tas?|ml|mg|g\b|un(?:idades?)?|x[íi]caras?|copos?))")
_DATA = re.compile(r"\b([0-3]?\d)/([01]?\d)(?:/(\d{2,4}))?\b" + _MEDIDA, re.IGNORECASE)


def _fala_moeda(m):
    """R$ 1.500,00 → '1500 reais'; R$ 50,90 → '50 reais e 90 centavos'."""
    inteiro = m.group(1).replace(".", "")
    cent = m.group(2)
    txt = f"{inteiro} reais"
    if cent and cent != "00":
        txt += f" e {int(cent)} centavos"
    return txt


def _fala_data(m):
    """19/07 → 'dia 19 do 7'; 19/07/2025 → 'dia 19 do 7 de 2025'. Só quando é
    data plausível (dia 1–31, mês 1–12); senão deixa como está (não corrompe)."""
    d, mth, y = int(m.group(1)), int(m.group(2)), m.group(3)
    if not (1 <= d <= 31 and 1 <= mth <= 12):
        return m.group(0)
    base = f"dia {d} do {mth}"
    return f"{base} de {int(y)}" if y else base


def _fala_telefone(m):
    """'11 92078-5067' → '1 1… 9 2 0 7 8… 5 0 6 7' — dígito a dígito, com
    fôlego entre os grupos, como uma pessoa dita um número ao telefone."""
    grupos = [g for g in re.split(r"\D+", m.group(0)) if g]
    return "… ".join(" ".join(g) for g in grupos)


# Fôlego humano (prescrição V0 da Voice Architect): frase longa demais para
# um fôlego ganha pausa (…) na vírgula mais próxima do meio — nenhuma palavra
# muda; só a respiração entra. "A pausa é conteúdo."
_FOLEGO_MAX_PALAVRAS = 14


def _folego(texto):
    def _respira(frase):
        palavras = frase.split()
        if len(palavras) <= _FOLEGO_MAX_PALAVRAS or ", " not in frase:
            return frase
        # vírgula mais próxima do meio (em palavras) vira pausa de respiração
        indices = [i for i, p in enumerate(palavras) if p.endswith(",")]
        if not indices:
            return frase
        meio = len(palavras) / 2
        corte = min(indices, key=lambda i: abs(i - meio))
        antes = " ".join(palavras[:corte + 1])[:-1]  # tira a vírgula
        depois = " ".join(palavras[corte + 1:])
        return _respira(antes) + "… " + _respira(depois)

    # preserva os terminadores ao dividir em frases
    partes = re.split(r"([.!?…]+\s*)", texto)
    return "".join(_respira(p) if i % 2 == 0 else p for i, p in enumerate(partes))


# ─── Identidade vocal + energia adaptativa (Sprint da Voz) ────────────────────
# "A Giulieta continua sendo a mesma pessoa. Ela apenas adapta sua energia."
# A IDENTIDADE entra em TODA instrução; o estilo só ajusta a energia do momento.
# Só o gpt-4o-mini-tts aceita instructions; no tts-1 tudo isto é ignorado
# (a adaptação chega trocando UMA env var — e volta do mesmo jeito).

# Versão refinada aprovada pela fundadora (09/07/2026) — Sprint da Presença:
# não é um personagem, é uma presença. Escuta primeiro; nunca tem pressa.
IDENTIDADE_VOCAL = (
    "Você conversa naturalmente. Nunca interpreta um personagem e nunca "
    "parece estar lendo um texto. Fale como uma mulher inteligente, "
    "calma, prática e muito querida pela família. Você escuta primeiro, "
    "pensa antes de responder e conversa como alguém que conhece profundamente "
    "a pessoa e gosta genuinamente de ajudá-la. Sua presença transmite "
    "tranquilidade, competência e proximidade. Nunca tenha pressa."
)

ESTILOS = {
    "modo_manha": (
        "É começo de dia: energia suave e clara, como quem abre a janela e "
        "gosta da luz que entra. Tom levemente mais alto e desperto que o "
        "normal, mas sem euforia — um bom dia de cozinha, não de rádio. "
        "Termine com leveza, deixando o dia parecer possível."
    ),
    "modo_pendencias": (
        "A conversa é prática: ritmo um pouco mais direto e resoluto, de quem "
        "arregaça as mangas junto. Mantenha o calor — você é a amiga "
        "organizada, não uma atendente. Clareza nos dados importantes, sem "
        "soar burocrática nem apressada."
    ),
    "modo_saude": (
        "O assunto é saúde: fale um pouco mais devagar APENAS nos dados que "
        "importam (nome do remédio, dose, horário), com articulação nítida — "
        "o resto no seu ritmo natural. Tom de cuidado sereno e adulto: zero "
        "alarme, zero voz de falar com criança. Você transmite 'tô aqui e a "
        "gente cuida disso juntas'."
    ),
    "modo_companhia": (
        "A pessoa quer presença, não tarefas. Se ela está bem: acompanhe com "
        "energia viva e curiosa, quase divertida. Se ela desabafa ou está "
        "triste: voz mais baixa, mais lenta nas pausas (não nas palavras), "
        "acolhimento de quem senta do lado — jamais pena, jamais tom fúnebre; "
        "o sorriso discreto vira serenidade, mas não desaparece."
    ),
    "modo_noite": (
        "É noite: baixe o volume interno da voz — tom mais grave e envolvente, "
        "ritmo desacelerando de leve como a casa apagando as luzes. Frases "
        "curtas com pausas mais longas. Termine em suspensão suave, como quem "
        "diz 'durma bem' sem precisar dizer."
    ),
    "modo_emergencia": (
        "Situação de possível emergência: voz FIRME, clara e estável — a calma "
        "de quem sabe o que fazer, não a doçura de quem consola. Ritmo "
        "controlado, sem urgência na voz (pânico contagia; firmeza ancora), "
        "articulação perfeita em números e instruções. Zero suavidade "
        "decorativa, zero pausa longa: presença total, frases curtas, cada "
        "palavra segura a pessoa."
    ),
}

# Regra anti-caricatura do painel: a adaptação nunca passa de ±15% do centro;
# na dúvida do detector, o estilo cai para o neutro-âncora (identidade pura) —
# instrucao_vocal(momento desconhecido) já faz exatamente isso, por construção.

def _suporta_instrucoes():
    """instructions só existe nos modelos gpt-*-tts; no tts-1, silêncio."""
    return config.TTS_MODEL.startswith("gpt-")


def instrucao_vocal(momento=None):
    """A instrução completa do turno: identidade SEMPRE + energia do momento."""
    estilo = ESTILOS.get(momento or "", "")
    return (IDENTIDADE_VOCAL + " " + estilo).strip()


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


def sintetizar(texto, momento=None):
    """TTS: texto → bytes de áudio (Opus, formato de nota de voz do WhatsApp).
    `momento` (modo de presença do turno) adapta a ENERGIA da voz quando o
    modelo aceita instruções — a identidade nunca muda. Retorna os bytes ou
    None em falha (nunca levanta)."""
    if not config.OPENAI_API_KEY:
        return None
    try:
        resp = _client().audio.speech.create(**_tts_kwargs(texto, momento))
        return resp.read()
    except Exception:
        return None


def _tts_kwargs(texto, momento=None):
    """Monta a chamada certa por modelo: gpt-*-tts recebe instructions e NÃO
    recebe speed (o ritmo vem da instrução; enviar speed derrubaria o áudio
    inteiro em silêncio); tts-1 recebe speed e ignora o resto."""
    kwargs = dict(
        model=config.TTS_MODEL,
        voice=config.VOICE_NAME,
        input=vocefy(texto),
        response_format="opus",
    )
    if _suporta_instrucoes():
        kwargs["instructions"] = instrucao_vocal(momento)
    else:
        kwargs["speed"] = config.VOICE_SPEED
    return kwargs


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
    # Telefone dita-se dígito a dígito (antes das demais regras de número)
    t = _TELEFONE.sub(_fala_telefone, t)
    t = _EMERGENCIA.sub(lambda m: " ".join(m.group(1)), t)
    # Valor: "R$ 50" → "50 reais" (mantém a unidade; não some com o número)
    t = _MOEDA.sub(_fala_moeda, t)
    t = t.replace("R$", "").replace("%", " por cento")
    # Horas: 15:00 → "15 horas"; 15:30 → "15 e 30"
    t = _HORA.sub(lambda m: f"{int(m.group(1))} horas" if m.group(2) == "00"
                  else f"{int(m.group(1))} e {int(m.group(2))}", t)
    # Datas: 19/07 → "dia 19 do 7" (com ano quando houver; nunca sobre dose)
    t = _DATA.sub(_fala_data, t)
    # Fôlego humano: frase longa ganha respiração na vírgula do meio
    t = _folego(t)
    # Espaços redundantes
    return re.sub(r"[ \t]{2,}", " ", t).strip()


def _remove_emoji(t):
    return "".join(c for c in t if c == "\n" or c == "…" or ord(c) < 0x1F000 and not (0x2600 <= ord(c) <= 0x27BF))
