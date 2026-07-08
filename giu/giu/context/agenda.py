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
    return rotulo


def _dd_mm(data_iso):
    return f"{data_iso[8:10]}/{data_iso[5:7]}"


def _linha_conflito(items, hoje_str, hora_agora):
    """Dois compromissos disputando o MESMO horário, daqui para frente — a
    fricção que dói descobrir tarde. Horário que já passou não alarma (C1):
    já doeu ou já se resolveu sozinho. (Janela/duração: limite T9.)"""
    from collections import Counter
    marcados = Counter(
        (i["date"], i["time"]) for i in items
        if i["date"] and i["time"]
        and (i["date"] > hoje_str or (i["date"] == hoje_str and i["time"] >= hora_agora))
    )
    duplicados = sorted(k for k, v in marcados.items() if v > 1)
    if not duplicados:
        return ""
    data, hora = duplicados[0]
    quem = [i["title"] for i in items if i["date"] == data and i["time"] == hora]
    return (f"CONFLITO DE AGENDA: \"{quem[0]}\" e \"{quem[1]}\" marcados para "
            f"{_dd_mm(data)} às {hora} — resolva COM ela, com leveza, antes que doa.")


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
    sem_data = [i for i in items if not i["date"]]

    linhas = []
    if len(por_vir) > 3:
        linhas.append(
            f"AGENDA — dia CHEIO: {len(por_vir)} compromissos ainda por vir hoje. Não despeje "
            "a lista: reduza a UMA prioridade com ela (a lista completa está em ver_agenda)."
        )
    elif por_vir:
        linha = "AGENDA — hoje ainda: " + "; ".join(_fmt(i) for i in por_vir)
        if sem_data:
            linha += f" · {len(sem_data)} pendência(s) sem data (ver_agenda)"
        linhas.append(linha + ".")
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
