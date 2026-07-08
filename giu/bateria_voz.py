"""
BATERIA AMPLA da Sprint da Voz — fase de DIREÇÃO ARTÍSTICA (ver SPRINT-VOZ.md).

Decisão da fundadora: "não quero procurar a melhor voz da OpenAI — quero
procurar A VOZ DA GIULIETA". A pergunta da escuta não é "qual soa melhor?";
é: "COM QUAL DELAS EU GOSTARIA DE CONVERSAR DURANTE MUITOS ANOS?"

Gera: 8 vozes femininas/neutras × 3 direções artísticas × 2 textos-de-vida
= 48 amostras cegas (voz-A..H) + gabarito lacrado (só se abre DEPOIS).

Uso (Despacho/Nanda): OPENAI_API_KEY=sk-... python bateria_voz.py
Saída em ./bateria-voz/. Custo: centavos.
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from giu import voice  # noqa: E402

from openai import OpenAI  # noqa: E402

MODEL = "gpt-4o-mini-tts"

# TODAS as vozes femininas/neutras do catálogo — jovens, maduras, leves,
# sorridentes, naturais. Nenhum veto prévio: os ouvidos da família decidem.
VOZES = ["alloy", "ballad", "coral", "fable", "nova", "sage", "shimmer", "verse"]

TEXTOS = {
    "T1-bomdia": (
        "Bom dia… acordou bem? Tá um céu bonito hoje — abre a janela um "
        "pouquinho antes do café. Ah, e só uma coisinha pra hoje: a consulta "
        "é às 15:00. O resto… deixa comigo."
    ),
    "T2-acolhimento": (
        "Ei… vem cá. Não precisa resolver nada agora, tá? Dia difícil a "
        "gente não carrega sozinha — me conta o que pesou mais… eu tô aqui, "
        "sem pressa nenhuma."
    ),
}

# As 3 DIREÇÕES ARTÍSTICAS (não parâmetros — direção de atriz):
DIRECOES = {
    "neutra": None,  # a voz "de fábrica" — linha de base
    "sorridente": (
        "Direção de cena: você é uma atriz brasileira de trinta e poucos anos "
        "gravando uma nota de voz para alguém que você AMA e com quem fala todo "
        "dia. Você está genuinamente feliz de falar com essa pessoa — dá para "
        "OUVIR o sorriso. Fala de verdade, com respiração, micro-pausas de quem "
        "pensa, uma leve risada guardada atrás das palavras. Zero locução, zero "
        "leitura: é uma mensagem íntima de quem gosta da vida e dessa pessoa. "
        "Ritmo natural de conversa, nunca lento."
    ),
    "intimista": (
        "Direção de cena: fim de tarde, você liga no viva-voz enquanto faz um "
        "café para alguém da sua família. Voz próxima do microfone, quente, "
        "baixa sem ser sussurro — a intimidade de quem não precisa impressionar "
        "ninguém. Curiosidade genuína nas perguntas, carinho sem açúcar, e a "
        "segurança tranquila de quem conhece essa pessoa há anos. Fala viva, "
        "presente, jamais melancólica."
    ),
}


def main():
    client = OpenAI()
    os.makedirs("bateria-voz", exist_ok=True)
    letras = "ABCDEFGH"
    cegas = dict(zip(random.sample(VOZES, len(VOZES)), letras))
    gabarito = {f"voz-{letra}": voz for voz, letra in cegas.items()}
    total = 0
    for voz, letra in cegas.items():
        for nome_dir, direcao in DIRECOES.items():
            for nome_texto, texto in TEXTOS.items():
                kwargs = dict(model=MODEL, voice=voz,
                              input=voice.vocefy(texto), response_format="mp3")
                if direcao:
                    kwargs["instructions"] = direcao
                resp = client.audio.speech.create(**kwargs)
                caminho = f"bateria-voz/voz{letra}-{nome_dir}-{nome_texto}.mp3"
                with open(caminho, "wb") as f:
                    f.write(resp.read())
                total += 1
                print(f"✓ {caminho}")
    with open("bateria-voz/gabarito.json", "w") as f:
        json.dump(gabarito, f, ensure_ascii=False, indent=2)
    print(f"\n{total} amostras. Escute no CELULAR, como nota de voz, sozinha. "
          "A pergunta não é 'qual soa melhor?' — é: 'com qual eu gostaria de "
          "conversar durante muitos anos?'. O gabarito só se abre no fim.")


if __name__ == "__main__":
    main()
