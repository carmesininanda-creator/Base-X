"""
Google Calendar — a agenda de verdade.

Quando configurado, a Agenda Viva da Giu passa a operar em cima do
Google Calendar: agendar cria eventos reais e ver_agenda mostra os
próximos eventos. A agenda interna (SQLite) continua funcionando como
fallback quando o Google não está configurado.

Autenticação: OAuth com refresh token (obtido uma única vez — ver README).
"""

from datetime import datetime, timedelta, timezone

import httpx

from .. import config

TOKEN_URL = "https://oauth2.googleapis.com/token"
CALENDAR_URL = "https://www.googleapis.com/calendar/v3"


OAUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
SCOPE = "https://www.googleapis.com/auth/calendar.events"


def app_configured():
    """Portão de plataforma: o app Google existe no deploy."""
    return bool(config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET)


def is_connected(user_id):
    """Portão de PESSOA: ela conectou a própria agenda (opt-in, revogável)."""
    from .. import memory
    return bool(memory.google_token(user_id))


def is_configured(user_id=None):
    """Sem user_id: modo global antigo (env). Com user_id: SOMENTE a agenda DA
    PESSOA — turno pessoal NUNCA cai no token/calendário global (D1 da Life
    Architect: evento na agenda errada é vida, não detalhe). Sem conexão dela,
    a cadeia cai para a Agenda Viva interna."""
    if user_id is not None:
        return app_configured() and is_connected(user_id)
    return app_configured() and bool(config.GOOGLE_REFRESH_TOKEN)


def _refresh_token_for(user_id=None):
    if user_id:
        from .. import memory
        token = memory.google_token(user_id)
        if token:
            return token
    return config.GOOGLE_REFRESH_TOKEN


def _calendar_id_for(user_id=None):
    if user_id:
        from .. import memory
        if memory.google_token(user_id):
            return "primary"  # a agenda principal DA pessoa
    return config.GOOGLE_CALENDAR_ID


def _redirect_uri():
    return config.BASE_URL.rstrip("/") + "/connectors/google/callback"


def auth_url(state):
    """Link de consentimento que a PRÓPRIA pessoa abre para conectar a agenda."""
    from urllib.parse import urlencode
    return OAUTH_URL + "?" + urlencode({
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": _redirect_uri(),
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    })


def exchange_code(code):
    """Troca o código do consentimento pelo refresh token da pessoa."""
    resp = httpx.post(
        TOKEN_URL,
        data={
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": _redirect_uri(),
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("refresh_token", "")


def _access_token(user_id=None):
    """Troca o refresh token (da pessoa, ou o global) por um access token (~1h)."""
    resp = httpx.post(
        TOKEN_URL,
        data={
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "refresh_token": _refresh_token_for(user_id),
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def list_events(max_results=10, user_id=None):
    """Próximos eventos do calendário (o DA PESSOA, quando conectada)."""
    token = _access_token(user_id)
    resp = httpx.get(
        f"{CALENDAR_URL}/calendars/{_calendar_id_for(user_id)}/events",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "timeMin": datetime.now(timezone.utc).isoformat(),
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        },
        timeout=30,
    )
    resp.raise_for_status()
    events = []
    for item in resp.json().get("items", []):
        start = item.get("start", {})
        events.append({
            "title": item.get("summary", "(sem título)"),
            "start": start.get("dateTime") or start.get("date") or "",
            "location": item.get("location", ""),
        })
    return events


def create_event(title, date, time=None, notes=None, duration_minutes=60,
                 user_id=None, location=None):
    """Cria um evento (na agenda DA PESSOA, quando conectada)."""
    token = _access_token(user_id)
    event = {"summary": title}
    if notes:
        event["description"] = notes
    if location:
        event["location"] = location  # o "onde" espelha no Google (T8)

    if time:
        start = datetime.fromisoformat(f"{date}T{time}")
        end = start + timedelta(minutes=duration_minutes)
        event["start"] = {"dateTime": start.isoformat(), "timeZone": config.TIMEZONE}
        event["end"] = {"dateTime": end.isoformat(), "timeZone": config.TIMEZONE}
    else:
        # Evento de dia inteiro: o Google exige end.date exclusivo (dia seguinte)
        next_day = (datetime.fromisoformat(date) + timedelta(days=1)).date().isoformat()
        event["start"] = {"date": date}
        event["end"] = {"date": next_day}

    resp = httpx.post(
        f"{CALENDAR_URL}/calendars/{_calendar_id_for(user_id)}/events",
        headers={"Authorization": f"Bearer {token}"},
        json=event,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("htmlLink", "")
