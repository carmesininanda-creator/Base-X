"""
BATERIA MULTI-PROVEDOR da Sprint da Voz — FASE 3: a caça à voz da Giulieta.

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
    "T0-oi": "Oi… sou eu. Tava aqui pensando em você — como foi o seu dia?",
    "T1-bomdia": (
        "Bom dia… acordou bem? Tá um céu bonito hoje — abre a janela um "
        "pouquinho antes do café. Ah, e a consulta é às 15:00. O resto… "
        "deixa comigo."
    ),
    "T2-juntas": (
        "Ei. Respira comigo um instante… Isso não precisa ser resolvido "
        "hoje, e muito menos sozinha. Me conta com calma — nós vamos "
        "resolver isso juntas."
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


def main():
    candidatas = _openai() + _elevenlabs() + _azure() + _google()
    if not candidatas:
        print("Nenhuma chave configurada — veja o cabeçalho do arquivo.")
        return
    faltando = [n for n, tem in (("ElevenLabs", os.getenv("ELEVENLABS_API_KEY")),
                                 ("Azure", os.getenv("AZURE_SPEECH_KEY")),
                                 ("Google", os.getenv("GOOGLE_TTS_API_KEY"))) if not tem]
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
    print(f"\n{total} amostras de {len(gabarito)} vozes. Escute o T0 ('Oi…') "
          "primeiro — a voz que te fizer sorrir ali merece o resto. Gabarito "
          "lacrado até o fim.")


if __name__ == "__main__":
    main()
