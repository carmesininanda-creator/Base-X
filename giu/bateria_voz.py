"""
BATERIA DE CENAS da SPRINT DA PRESENÇA DA GIULIETA (multi-provedor).

"Não estamos procurando um TTS. Estamos procurando uma PRESENÇA." A
referência é uma sensação — alguém que inspira confiança imediatamente,
transmite inteligência tranquila, escuta antes de responder, nunca parece
apressada, nunca interpreta um personagem, nunca lê texto. A escolha é da
Voice Architect como IDENTIDADE; a tecnologia se adapta a ela — nunca o
contrário. A sprint fecha quando a Nanda ouvir e sentir: "Essa é a Giu."

Decisão da fundadora: "Esqueçam por um momento a tecnologia. Quero encontrar
a voz que faça alguém sorrir quando ouvir 'Oi…'. Se isso exigir outro
provedor de TTS, clonagem licenciada ou qualquer outra solução, vamos
avaliar. A identidade da Giulieta vale mais do que a tecnologia usada para
produzi-la."

O BRIEFING (dela): mulher madura (sensação de 45–60), naturalmente
sorridente sem ser animadora, segura sem autoritária, elegante sem formal,
curiosa, acolhedora, como quem está na mesma sala. A EXPERIÊNCIA que
atrizes como Annette Bening transmitem — presença, confiança, humanidade —
SEM copiar voz ou identidade de ninguém. Nunca jovem, nunca teatral, nunca
infantil, nunca melancólica. "Nós vamos resolver isso juntas."

Provedores (cada um liga com a própria chave no ambiente; sem chave = pulado
com aviso — a bateria roda com o que houver):
  OPENAI_API_KEY                        → OpenAI gpt-4o-mini-tts (com direção)
  ELEVENLABS_API_KEY                    → ElevenLabs multilingual v2
  AZURE_SPEECH_KEY + AZURE_SPEECH_REGION→ Azure Neural pt-BR
  GOOGLE_TTS_API_KEY                    → Google Cloud TTS pt-BR

Uso: python bateria_voz.py   →   ./bateria-voz/ (amostras cegas + gabarito lacrado)
A escuta: no celular, sozinha, como nota de voz. A única pergunta:
"COM QUAL VOZ EU GOSTARIA DE CONVERSAR DURANTE MUITOS ANOS?"
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from giu import voice  # noqa: E402  (vocefy + a identidade madura)

TEXTOS = {
    # As 7 CENAS da fundadora — conversas reais, não frases de teste
    "C1-oi": "Oi… sou eu.",
    "C2-bomdia": (
        "Bom dia… acordou bem? Tá um céu bonito lá fora. Vai com calma no "
        "café — o dia deixa."
    ),
    "C3-comofoi": (
        "E aí… como foi o seu dia? De verdade, assim — do jeito que você "
        "contaria pra alguém de casa."
    ),
    "C4-juntas": (
        "Ei. Respira comigo um instante… Isso não precisa ser resolvido "
        "hoje, e muito menos sozinha. Nós vamos resolver isso juntas."
    ),
    "C5-ficofeliz": (
        "Fico feliz que você tenha me contado isso… De verdade. Coisa "
        "guardada pesa mais — e agora ela é nossa, não só sua."
    ),
    "C6-silencio": (
        "Tô aqui… … … Não precisa dizer nada agora… … Eu fico com você."
    ),
    "C7-despedida": (
        "Vou deixar você descansar agora… O dia foi longo, e você deu "
        "conta dele. Durma bem… amanhã eu tô aqui."
    ),
}

# A direção de cena única da fase 3 (para provedores que aceitam direção):
DIRECAO_MADURA = (
    "Direção de cena: você é uma atriz brasileira madura — a sensação de "
    "alguém de uns cinquenta anos que já viveu muito, escuta antes de falar "
    "e não precisa elevar a voz para transmitir segurança. Está gravando uma "
    "nota de voz para alguém que ama. Inteligência calorosa, humor sutil "
    "guardado atrás das palavras, um sorriso discreto que dá para OUVIR. "
    "Ritmo natural de quem está na mesma sala. Nunca teatral, nunca "
    "infantil, nunca melancólica, nunca locutora."
)


# ─── Provedores ────────────────────────────────────────────────────────────────

def _openai():
    if not os.getenv("OPENAI_API_KEY"):
        return []
    from openai import OpenAI
    client = OpenAI()

    def synth(voz):
        def f(texto):
            r = client.audio.speech.create(
                model="gpt-4o-mini-tts", voice=voz, input=voice.vocefy(texto),
                instructions=DIRECAO_MADURA, response_format="mp3")
            return r.read()
        return f
    # as mais maduras do catálogo + as anteriores (defendem o posto às cegas)
    return [(f"openai/{v}", synth(v)) for v in
            ("sage", "coral", "shimmer", "alloy", "ballad")]


def _elevenlabs():
    chave = os.getenv("ELEVENLABS_API_KEY")
    if not chave:
        return []
    import httpx

    def synth(vid, nome):
        def f(texto):
            r = httpx.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
                headers={"xi-api-key": chave},
                json={"text": voice.vocefy(texto),
                      "model_id": "eleven_multilingual_v2",
                      "voice_settings": {"stability": 0.45,
                                         "similarity_boost": 0.8,
                                         "style": 0.35}},
                timeout=60)
            r.raise_for_status()
            return r.content
        return f
    # Premades maduras/quentes (ponto de partida — a Voice Library pt-BR
    # licenciada é a mina de ouro; Despacho/Nanda podem adicionar IDs via
    # ELEVEN_VOICES="id1:Nome1,id2:Nome2")
    vozes = [("XrExE9yKIg1WjnnlVkGX", "Matilda"), ("Xb7hH8MSUJpSbSDYk0k2", "Alice"),
             ("EXAVITQu4vr4xnSDxMaL", "Sarah")]
    extra = os.getenv("ELEVEN_VOICES", "")
    for par in extra.split(","):
        if ":" in par:
            vid, nome = par.split(":", 1)
            vozes.append((vid.strip(), nome.strip()))
    return [(f"eleven/{nome}", synth(vid, nome)) for vid, nome in vozes]


def _azure():
    chave, regiao = os.getenv("AZURE_SPEECH_KEY"), os.getenv("AZURE_SPEECH_REGION")
    if not (chave and regiao):
        return []
    import httpx

    def synth(nome_voz):
        def f(texto):
            ssml = (f"<speak version='1.0' xml:lang='pt-BR'>"
                    f"<voice name='{nome_voz}'><prosody rate='1.0'>"
                    f"{voice.vocefy(texto)}</prosody></voice></speak>")
            r = httpx.post(
                f"https://{regiao}.tts.speech.microsoft.com/cognitiveservices/v1",
                headers={"Ocp-Apim-Subscription-Key": chave,
                         "Content-Type": "application/ssml+xml",
                         "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3"},
                content=ssml.encode(), timeout=60)
            r.raise_for_status()
            return r.content
        return f
    return [(f"azure/{v.split('-')[-1].replace('Neural','')}", synth(v)) for v in
            ("pt-BR-FranciscaNeural", "pt-BR-ThalitaNeural", "pt-BR-ManuelaNeural")]


def _google():
    chave = os.getenv("GOOGLE_TTS_API_KEY")
    if not chave:
        return []
    import base64
    import httpx

    def synth(nome_voz):
        def f(texto):
            r = httpx.post(
                f"https://texttospeech.googleapis.com/v1/text:synthesize?key={chave}",
                json={"input": {"text": voice.vocefy(texto)},
                      "voice": {"languageCode": "pt-BR", "name": nome_voz},
                      "audioConfig": {"audioEncoding": "MP3"}},
                timeout=60)
            r.raise_for_status()
            return base64.b64decode(r.json()["audioContent"])
        return f
    return [(f"google/{v.split('-')[-1]}", synth(v)) for v in
            ("pt-BR-Neural2-A", "pt-BR-Neural2-C", "pt-BR-Chirp3-HD-Aoede")]


def _cartesia():
    chave = os.getenv("CARTESIA_API_KEY")
    vozes_env = os.getenv("CARTESIA_VOICES", "")  # "voice_id:Nome,voice_id:Nome"
    if not (chave and vozes_env):
        return []
    import httpx

    def synth(vid):
        def f(texto):
            r = httpx.post(
                "https://api.cartesia.ai/tts/bytes",
                headers={"X-API-Key": chave, "Cartesia-Version": "2024-06-10"},
                json={"model_id": "sonic-2", "language": "pt",
                      "voice": {"mode": "id", "id": vid},
                      "transcript": voice.vocefy(texto),
                      "output_format": {"container": "mp3",
                                        "bit_rate": 128000, "sample_rate": 44100}},
                timeout=60)
            r.raise_for_status()
            return r.content
        return f
    pares = [p.split(":", 1) for p in vozes_env.split(",") if ":" in p]
    return [(f"cartesia/{nome.strip()}", synth(vid.strip())) for vid, nome in pares]


def _playht():
    uid, chave = os.getenv("PLAYHT_USER_ID"), os.getenv("PLAYHT_API_KEY")
    vozes_env = os.getenv("PLAYHT_VOICES", "")  # "voice_url_ou_id:Nome,..."
    if not (uid and chave and vozes_env):
        return []
    import httpx

    def synth(vid):
        def f(texto):
            r = httpx.post(
                "https://api.play.ht/api/v2/tts/stream",
                headers={"X-USER-ID": uid, "AUTHORIZATION": chave,
                         "accept": "audio/mpeg"},
                json={"text": voice.vocefy(texto), "voice": vid,
                      "voice_engine": "PlayDialog", "language": "portuguese",
                      "output_format": "mp3"},
                timeout=120)
            r.raise_for_status()
            return r.content
        return f
    pares = [p.split(":", 1) for p in vozes_env.split(",") if ":" in p]
    return [(f"playht/{nome.strip()}", synth(vid.strip())) for vid, nome in pares]


def main():
    candidatas = (_openai() + _elevenlabs() + _azure() + _google()
                  + _cartesia() + _playht())
    if not candidatas:
        print("Nenhuma chave configurada — veja o cabeçalho do arquivo.")
        return
    faltando = [n for n, tem in (("ElevenLabs", os.getenv("ELEVENLABS_API_KEY")),
                                 ("Azure", os.getenv("AZURE_SPEECH_KEY")),
                                 ("Google", os.getenv("GOOGLE_TTS_API_KEY")),
                                 ("Cartesia", os.getenv("CARTESIA_API_KEY")),
                                 ("PlayHT", os.getenv("PLAYHT_API_KEY"))) if not tem]
    if faltando:
        print(f"⚠ Sem chave (pulados): {', '.join(faltando)} — a bateria fica "
              "menor do que a fundadora pediu até o Despacho provisionar.")
    os.makedirs("bateria-voz", exist_ok=True)
    random.shuffle(candidatas)
    gabarito, total, falhas = {}, 0, []
    for i, (rotulo, synth) in enumerate(candidatas, 1):
        cega = f"voz-{i:02d}"
        gabarito[cega] = rotulo
        for nome_texto, texto in TEXTOS.items():
            try:
                audio = synth(texto)
                with open(f"bateria-voz/{cega}-{nome_texto}.mp3", "wb") as f:
                    f.write(audio)
                total += 1
                print(f"✓ {cega}-{nome_texto}  ")
            except Exception as e:
                falhas.append(f"{rotulo}/{nome_texto}: {type(e).__name__}")
    with open("bateria-voz/gabarito.json", "w") as f:
        json.dump(gabarito, f, ensure_ascii=False, indent=2)
    if falhas:
        print(f"\n⚠ Falhas (honestidade): {'; '.join(falhas)}")
    print(f"\n{total} amostras de {len(gabarito)} vozes. Escute a C1 ('Oi…') "
          "primeiro — a voz que te fizer sorrir ali merece o resto. Gabarito "
          "lacrado até o fim.")


if __name__ == "__main__":
    main()
