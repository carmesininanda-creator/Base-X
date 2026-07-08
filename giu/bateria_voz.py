"""
Gerador da BATERIA CEGA da Sprint da Voz (ver SPRINT-VOZ.md).

Gera as amostras para a família ouvir às cegas: 4 vozes candidatas ×
4 estilos × 3 textos-de-vida, com nomes cegos (voz-A/B/C/D) e um
gabarito.json separado (só a operadora abre, DEPOIS da bateria).

Uso (Despacho ou Nanda, com a chave no ambiente):
    OPENAI_API_KEY=sk-... python bateria_voz.py
Saída em ./bateria-voz/: amostra-<VOZ_CEGA>-<estilo>-<texto>.mp3 + gabarito.json

Custo aproximado: 48 áudios curtos (~10s cada) no gpt-4o-mini-tts — centavos.
"""

import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from giu import voice  # noqa: E402  (IDENTIDADE_VOCAL + ESTILOS do charter)

from openai import OpenAI  # noqa: E402

MODEL = "gpt-4o-mini-tts"
VOZES = ["shimmer", "nova", "coral", "sage"]  # as candidatas do painel

# Os 3 textos-de-vida do charter (passam pelo vocefy como um turno real)
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
    "T3-celebracao": (
        "Espera… você conseguiu?! Ai, que coisa boa… eu sabia, viu — desde "
        "que você me contou que ia tentar. Hoje merece um cafezinho "
        "especial… me conta como foi?"
    ),
}

# Estilos da bateria: neutro (linha de base) + 3 adaptações do charter
ESTILOS_BATERIA = {
    "neutro": None,  # sem instructions — a voz "de fábrica"
    "manha": voice.instrucao_vocal("modo_manha"),
    "acolhimento": voice.instrucao_vocal("modo_companhia"),
    "celebracao": voice.IDENTIDADE_VOCAL + " " + (
        "Energia de celebração pequena: viva, quente e genuinamente feliz "
        "pela pessoa — o brilho de quem torceu junto. Sem exagero de "
        "comercial: a alegria é dela; você acompanha, não rouba a cena."
    ),
}


def main():
    client = OpenAI()
    os.makedirs("bateria-voz", exist_ok=True)
    cegas = dict(zip(random.sample(VOZES, len(VOZES)), "ABCD"))
    gabarito = {f"voz-{letra}": voz for voz, letra in cegas.items()}
    total = 0
    for voz, letra in cegas.items():
        for nome_estilo, instrucao in ESTILOS_BATERIA.items():
            for nome_texto, texto in TEXTOS.items():
                kwargs = dict(model=MODEL, voice=voz,
                              input=voice.vocefy(texto), response_format="mp3")
                if instrucao:
                    kwargs["instructions"] = instrucao
                resp = client.audio.speech.create(**kwargs)
                caminho = f"bateria-voz/amostra-voz{letra}-{nome_estilo}-{nome_texto}.mp3"
                with open(caminho, "wb") as f:
                    f.write(resp.read())
                total += 1
                print(f"✓ {caminho}")
    with open("bateria-voz/gabarito.json", "w") as f:
        json.dump(gabarito, f, ensure_ascii=False, indent=2)
    print(f"\n{total} amostras geradas. O gabarito.json só se abre DEPOIS da "
          "bateria — ninguém (nem a operadora) sabe qual é qual durante a escuta.")


if __name__ == "__main__":
    main()
