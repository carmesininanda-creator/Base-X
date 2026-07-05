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


def is_configured():
    return bool(
        config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET and config.GOOGLE_REFRESH_TOKEN
    )


def _access_token():
    """Troca o refresh token por um access token válido (~1h)."""
    resp = httpx.post(
        TOKEN_URL,
        data={
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "refresh_token": config.GOOGLE_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def list_events(max_results=10):
    """Próximos eventos do calendário, como lista de dicts simples."""
    token = _access_token()
    resp = httpx.get(
        f"{CALENDAR_URL}/calendars/{config.GOOGLE_CALENDAR_ID}/events",
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


def create_event(title, date, time=None, notes=None, duration_minutes=60):
    """Cria um evento. Com hora vira evento normal de 1h; sem hora, dia inteiro."""
    token = _access_token()
    event = {"summary": title}
    if notes:
        event["description"] = notes

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
        f"{CALENDAR_URL}/calendars/{config.GOOGLE_CALENDAR_ID}/events",
        headers={"Authorization": f"Bearer {token}"},
        json=event,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("htmlLink", "")
