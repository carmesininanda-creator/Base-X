"""
Open-Meteo — Life Connector de clima e sol (dívida T7 da Life Architect).

A fronteira com o fornecedor mora AQUI, como o Google Calendar mora em
google_calendar.py: nenhum Provider conhece URL, SDK ou formato de resposta
de fornecedor — o Time Provider pergunta "como está o tempo nessa
coordenada?" e recebe vida, não payload.

Privacidade: nenhum dado pessoal sai daqui além da coordenada da CIDADE que
a própria pessoa autorizou (definir_cidade — nível cidade, nunca localização
precisa). Sem chave, sem conta, sem rastreio.
"""

import httpx

# Teto de tempo do turno: conector lento é conector mudo (garantia 10)
TIMEOUT = 2.5

_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# Códigos WMO → língua de vida
_WMO = {
    0: "céu limpo", 1: "quase limpo", 2: "parcialmente nublado", 3: "nublado",
    45: "neblina", 48: "neblina", 51: "garoa", 53: "garoa", 55: "garoa",
    61: "chuva fraca", 63: "chuva", 65: "chuva forte", 66: "chuva gelada",
    67: "chuva gelada", 71: "neve", 73: "neve", 75: "neve", 77: "neve",
    80: "pancadas de chuva", 81: "pancadas de chuva", 82: "pancadas fortes de chuva",
    95: "tempestade", 96: "tempestade com granizo", 99: "tempestade com granizo",
}


def geocodificar(cidade, timeout=6):
    """Nome da cidade → (nome oficial, lat, lon), ou None se não encontrar.
    Usado UMA vez, no momento em que a pessoa autoriza a cidade."""
    resp = httpx.get(
        _GEOCODING_URL,
        params={"name": cidade, "count": 1, "language": "pt", "format": "json"},
        timeout=timeout,
    )
    resultados = resp.json().get("results") or []
    if not resultados:
        return None
    r = resultados[0]
    return r.get("name", cidade), r["latitude"], r["longitude"]


def previsao(lat, lon, timezone):
    """Tempo agora + máx/mín + sol do dia, em dicionário de VIDA:
    {temperatura, descricao, maxima, minima, nascer, por}.
    Levanta em falha — quem chama decide o silêncio (contrato do Provider)."""
    resp = httpx.get(
        _FORECAST_URL,
        params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset",
            "timezone": timezone, "forecast_days": 1,
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    dados = resp.json()
    atual, dia = dados["current"], dados["daily"]
    return {
        "temperatura": round(atual["temperature_2m"]),
        "descricao": _WMO.get(atual.get("weather_code"), ""),
        "maxima": round(dia["temperature_2m_max"][0]),
        "minima": round(dia["temperature_2m_min"][0]),
        "nascer": dia["sunrise"][0][11:16],
        "por": dia["sunset"][0][11:16],
    }
