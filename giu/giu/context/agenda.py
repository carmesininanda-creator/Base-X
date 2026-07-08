"""
📅 Calendar Provider — área 2 (Agenda) do Living Context.

Dimensão: os compromissos — o que a vida já marcou. Fricção que reduz: a
carga de LEMBRAR (compromisso morando na cabeça), o conflito descoberto
tarde, a véspera sem preparo, o dia que não cabe no dia.

Decisão da fundadora (textual): "Google Calendar será apenas sincronização.
A Agenda Viva continua sendo o cérebro." Este snapshot nasce 100% da Agenda
Viva — zero rede, zero fornecedor; o espelho no Google acontece nas
ferramentas (agendar/ver_agenda), nunca aqui. O retrato mostra o CUIDADO do
dia (hoje, véspera, conflito, sobrecarga); a lista completa vive na
ferramenta ver_agenda, sob demanda.

CP-2 (substituição, não soma): este Provider ABSORVEU o bloco "AGENDA VIVA"
do prompt — o retrato é a única porta da agenda no contexto.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .. import config, memory
from ..integrations import google_calendar


def _fmt(item):
    rotulo = item["title"]
    if item["time"]:
        rotulo += f" às {item['time']}"
    if item.get("lugar"):
        rotulo += f" ({item['lugar']})"  # o "onde" é preparo de véspera (T8)
    return rotulo


def _minutos(hhmm):
    """Robusto a "9:00" (K1): hora de 1 dígito jamais derruba o retrato."""
    h, m = hhmm.split(":")[:2]
    return int(h) * 60 + int(m)


DURACAO_PADRAO = 60  # minutos, quando a pessoa não disse quanto dura


def _dd_mm(data_iso):
    return f"{data_iso[8:10]}/{data_iso[5:7]}"


def _linha_conflito(items, hoje_str, hora_agora):
    """T9 paga: conflito por SOBREPOSIÇÃO real (duração conhecida, ou 60min
    de suposição honesta) — 15:00 e 15:30 não passam mais despercebidos. E o
    quase-conflito ganha voz gentil: "muito próximos". Horário que já passou
    não alarma (C1)."""
    futuros = sorted(
        (i for i in items if i["date"] and i["time"]
         and (i["date"] > hoje_str or (i["date"] == hoje_str and i["time"] >= hora_agora))),
        key=lambda i: (i["date"], i["time"]),
    )
    apertada = ""
    for a, b in zip(futuros, futuros[1:]):
        if a["date"] != b["date"]:
            continue  # duração que cruza meia-noite: fora do radar (K4, registrado)
        inicio_a = _minutos(a["time"])
        fim_a = inicio_a + (a.get("duracao") or DURACAO_PADRAO)
        inicio_b = _minutos(b["time"])
        if inicio_b < fim_a:
            # mesmo horário de início = conflito CERTO, com ou sem duração
            if a.get("duracao") or inicio_b == inicio_a:  # voz de fato
                return (f"CONFLITO DE AGENDA: \"{a['title']}\" e \"{b['title']}\" se "
                        f"sobrepõem em {_dd_mm(a['date'])} ({a['time']} e {b['time']}) — "
                        "resolva COM ela, com leveza, antes que doa.")
            # duração SUPOSTA → voz de hipótese (K2): o alarme vira captura de duração
            return (f"CONFLITO POSSÍVEL em {_dd_mm(a['date'])}: \"{a['title']}\" "
                    f"({a['time']}) e \"{b['title']}\" ({b['time']}) PODEM se sobrepor "
                    f"— contei ~1h para \"{a['title']}\"; vale confirmar COM ela quanto "
                    "tempo dura, sem alarme.")
        if not apertada and inicio_b - fim_a < 30:
            apertada = (f"AGENDA APERTADA em {_dd_mm(a['date'])}: \"{a['title']}\" e "
                        f"\"{b['title']}\" muito próximos ({a['time']} e {b['time']}) — "
                        "dá tempo de ir de um ao outro? Vale conferir COM ela.")
    return apertada  # K3: conflito real sempre vence o aviso menor


def snapshot(user_id, _now=None):
    """Como está a AGENDA da vida desta pessoa neste momento? (1-3 linhas)"""
    items = memory.get_agenda(user_id)
    now = _now or datetime.now(ZoneInfo(config.TIMEZONE))
    hoje_str = now.strftime("%Y-%m-%d")
    hora_agora = now.strftime("%H:%M")
    amanha_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Boa companhia sabe que horas são (C1): o que já foi vivido hoje não é
    # "hoje" — é silêncio (ou, na evolução, um "como foi?").
    por_vir = [i for i in items if i["date"] == hoje_str
               and (not i["time"] or i["time"] >= hora_agora)]
    de_amanha = [i for i in items if i["date"] == amanha_str]
    # Pendências sem data moram no Communication Provider (C5) — uma porta só.

    linhas = []
    if len(por_vir) > 3:
        linhas.append(
            f"AGENDA — dia CHEIO: {len(por_vir)} compromissos ainda por vir hoje. Não despeje "
            "a lista: reduza a UMA prioridade com ela (a lista completa está em ver_agenda)."
        )
    elif por_vir:
        linhas.append("AGENDA — hoje ainda: "
                      + "; ".join(_fmt(i) for i in por_vir) + ".")
    if de_amanha:
        linhas.append(
            "AGENDA — amanhã: " + "; ".join(_fmt(i) for i in de_amanha[:3])
            + " — a véspera é a hora do preparo leve: algo a adiantar hoje?"
        )
    conflito = _linha_conflito(items, hoje_str, hora_agora)
    if conflito:
        linhas.append(conflito)
    # Honestidade sobre o retrato parcial (C2): com Google conectado, eventos
    # criados FORA daqui não aparecem — nunca afirme "dia livre" sem conferir.
    if google_calendar.is_configured(user_id):
        linhas.append(
            "Agenda do Google conectada: este retrato mostra só o que vive aqui — "
            "antes de afirmar como está o dia dela, confirme em ver_agenda."
        )
    return "\n".join(linhas[:3])


PROVIDER = {
    "nome": "Calendar Provider",
    "area": "2. Agenda",
    "available": lambda user_id: True,  # Agenda Viva é interna: nunca falta
    "snapshot": snapshot,
}
