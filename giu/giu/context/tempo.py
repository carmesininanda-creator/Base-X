"""
⏰ Time Provider — área 1 (Tempo) do Living Context.

Dimensão: o palco onde a vida acontece — o agora. Data, hora, dia da semana,
estação, feriados, clima, nascer/pôr do sol, datas queridas.

Piso interno (zero conector, zero rede): data, hora, dia da semana em
português, estação e feriados nacionais fixos — cálculo puro. É o piso
garantido do retrato inteiro: o Living Context nunca nasce vazio.

Enriquecimentos autorizados: datas queridas que a pessoa pediu para lembrar
(anotar_data) e clima/sol pela CIDADE que ela autorizou (definir_cidade —
nível cidade, nunca localização precisa; revogável). Fricção que reduz: o
tempo que pega a pessoa de surpresa — a data querida que passa em branco, o
feriado esquecido, o frio que chegou sem aviso.
"""

import time as _time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx

from .. import config, memory

# ─── Piso interno: calendário humano em português (cálculo puro) ──────────────

DIAS_SEMANA = ("segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
               "sexta-feira", "sábado", "domingo")

# Feriados nacionais FIXOS (honestidade de escopo: os móveis — Carnaval,
# Sexta-feira Santa, Corpus Christi — ficam para a fase de evolução).
FERIADOS_FIXOS = {
    "01-01": "Confraternização Universal",
    "04-21": "Tiradentes",
    "05-01": "Dia do Trabalho",
    "09-07": "Independência do Brasil",
    "10-12": "Nossa Senhora Aparecida",
    "11-02": "Finados",
    "11-15": "Proclamação da República",
    "11-20": "Dia da Consciência Negra",
    "12-25": "Natal",
}


def estacao(dt):
    """Estação no hemisfério sul (fronteiras aproximadas nos dias 21/23)."""
    md = dt.strftime("%m-%d")
    if "03-21" <= md <= "06-20":
        return "outono"
    if "06-21" <= md <= "09-22":
        return "inverno"
    if "09-23" <= md <= "12-20":
        return "primavera"
    return "verão"


def _agora():
    return datetime.now(ZoneInfo(config.TIMEZONE))


def _linha_agora(now):
    linha = (f"AGORA: {DIAS_SEMANA[now.weekday()]}, {now.strftime('%d/%m/%Y %H:%M')} "
             f"(fuso {config.TIMEZONE}) — {estacao(now)}")
    hoje = FERIADOS_FIXOS.get(now.strftime("%m-%d"))
    amanha = FERIADOS_FIXOS.get((now + timedelta(days=1)).strftime("%m-%d"))
    if hoje:
        linha += f" · hoje é feriado ({hoje})"
    elif amanha:
        linha += f" · amanhã é feriado ({amanha})"
    return linha


# ─── Datas queridas (o que ELA pediu para lembrar — anotar_data) ──────────────

def _e_bissexto(ano):
    return ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)


def _acorda_em(mmdd, ano):
    """Em ano não bissexto, quem nasceu em 29/02 acorda em 28/02 (T1) — o
    aniversário existe todo ano; o calendário é que às vezes não colabora."""
    if mmdd == "02-29" and not _e_bissexto(ano):
        return "02-28"
    return mmdd


def _bate(d, dia):
    """A data acorda neste `dia`? Recorrente compara o MM-DD (com a regra do
    29/02); única compara a data completa — data única de ano passado JAMAIS
    volta a acordar (T2)."""
    alvo = d.get("data", "")
    if d.get("recorrente", len(alvo) == 5):
        return len(alvo) >= 5 and _acorda_em(alvo[-5:], dia.year) == dia.strftime("%m-%d")
    return alvo == dia.strftime("%Y-%m-%d")


def _linha_datas(user_id, now):
    datas = memory.dates_all(user_id)
    if not datas:
        return ""
    amanha = now + timedelta(days=1)
    de_hoje = [d["titulo"] for d in datas if _bate(d, now)]
    de_amanha = [d["titulo"] for d in datas if _bate(d, amanha)]
    partes = []
    if de_hoje:
        partes.append("HOJE: " + "; ".join(de_hoje))
    if de_amanha:
        partes.append("amanhã: " + "; ".join(de_amanha))
    if not partes:
        return ""
    return ("DATAS QUERIDAS (ela pediu para lembrar) — " + " · ".join(partes)
            + " — toque com carinho e no momento certo, nunca como notificação; "
            "se JÁ tocou nesta conversa, silêncio — e um 'já resolvi' ou 'não' "
            "ENCERRA o assunto (anote no fio).")


# ─── Clima e sol (cidade AUTORIZADA por ela — enriquecimento, nunca dimensão) ──

_CLIMA_TIMEOUT = 2.5          # teto de tempo: conector lento = conector mudo
_CLIMA_TTL = 30 * 60          # cache técnico volátil (memória do processo)
_clima_cache = {}             # user_id -> (epoch, linha)

_WMO = {
    0: "céu limpo", 1: "quase limpo", 2: "parcialmente nublado", 3: "nublado",
    45: "neblina", 48: "neblina", 51: "garoa", 53: "garoa", 55: "garoa",
    61: "chuva fraca", 63: "chuva", 65: "chuva forte", 66: "chuva gelada",
    67: "chuva gelada", 71: "neve", 73: "neve", 75: "neve", 77: "neve",
    80: "pancadas de chuva", 81: "pancadas de chuva", 82: "pancadas fortes de chuva",
    95: "tempestade", 96: "tempestade com granizo", 99: "tempestade com granizo",
}


def _linha_clima(user_id, now):
    cidade = memory.city_get(user_id)
    if not cidade or cidade.get("lat") is None:
        return ""  # sem cidade autorizada, o Tempo vive sem clima — e vive bem
    # Cache por pessoa E coordenada (T4): trocou de cidade → o céu antigo morre na hora
    chave = (user_id, cidade["lat"], cidade["lon"])
    em_cache = _clima_cache.get(chave)
    if em_cache and _time.time() - em_cache[0] < _CLIMA_TTL:
        return em_cache[1]
    try:
        resp = httpx.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": cidade["lat"], "longitude": cidade["lon"],
                "current": "temperature_2m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
                "timezone": config.TIMEZONE, "forecast_days": 1,
            },
            timeout=_CLIMA_TIMEOUT,
        )
        resp.raise_for_status()
        dados = resp.json()
        atual = dados["current"]
        dia = dados["daily"]
        desc = _WMO.get(atual.get("weather_code"), "")
        sol = (f"o sol nasce às {dia['sunrise'][0][11:16]}" if now.hour < 12
               else f"o sol se põe às {dia['sunset'][0][11:16]}")
        linha = (f"Lá fora em {cidade['nome']}: {round(atual['temperature_2m'])}°C"
                 + (f", {desc}" if desc else "")
                 + f" (máx {round(dia['temperature_2m_max'][0])}° / "
                 f"mín {round(dia['temperature_2m_min'][0])}°); {sol}.")
    except Exception:
        return ""  # degrada em silêncio — a pessoa nunca vê erro de fornecedor
    _clima_cache[chave] = (_time.time(), linha)
    return linha


# ─── O Provider (contrato universal) ──────────────────────────────────────────

def snapshot(user_id):
    """Como está o TEMPO da vida desta pessoa neste momento? (1-3 linhas)"""
    now = _agora()
    linhas = [_linha_agora(now)]
    datas = _linha_datas(user_id, now)
    if datas:
        linhas.append(datas)
    clima = _linha_clima(user_id, now)
    if clima:
        linhas.append(clima)
    return "\n".join(linhas)


PROVIDER = {
    "nome": "Time Provider",
    "area": "1. Tempo",
    "available": lambda user_id: True,  # o piso temporal nunca falta
    "snapshot": snapshot,
}
