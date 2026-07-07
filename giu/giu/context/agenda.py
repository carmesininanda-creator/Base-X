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


def _fmt(item):
    rotulo = item["title"]
    if item["time"]:
        rotulo += f" às {item['time']}"
    return rotulo


def _linha_conflito(items, hoje_str):
    """Dois compromissos disputando o MESMO horário, de hoje em diante — a
    fricção que dói descobrir tarde. Aponta o conflito mais próximo."""
    from collections import Counter
    marcados = Counter(
        (i["date"], i["time"]) for i in items
        if i["date"] and i["time"] and i["date"] >= hoje_str
    )
    duplicados = sorted(k for k, v in marcados.items() if v > 1)
    if not duplicados:
        return ""
    data, hora = duplicados[0]
    quem = [i["title"] for i in items if i["date"] == data and i["time"] == hora]
    return (f"CONFLITO DE AGENDA: \"{quem[0]}\" e \"{quem[1]}\" marcados para "
            f"{data} às {hora} — resolva COM ela, com leveza, antes que doa.")


def snapshot(user_id):
    """Como está a AGENDA da vida desta pessoa neste momento? (1-3 linhas)"""
    items = memory.get_agenda(user_id)
    if not items:
        return ""  # agenda vazia é silêncio, não formulário
    now = datetime.now(ZoneInfo(config.TIMEZONE))
    hoje_str = now.strftime("%Y-%m-%d")
    amanha_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    de_hoje = [i for i in items if i["date"] == hoje_str]
    de_amanha = [i for i in items if i["date"] == amanha_str]
    sem_data = [i for i in items if not i["date"]]

    linhas = []
    if len(de_hoje) > 3:
        linhas.append(
            f"AGENDA — dia CHEIO: {len(de_hoje)} compromissos hoje. Não despeje a "
            "lista: reduza a UMA prioridade com ela (a lista completa está em ver_agenda)."
        )
    elif de_hoje:
        linha = "AGENDA — hoje: " + "; ".join(_fmt(i) for i in de_hoje)
        if sem_data:
            linha += f" · {len(sem_data)} pendência(s) sem data (ver_agenda)"
        linhas.append(linha + ".")
    if de_amanha:
        linhas.append(
            "amanhã: " + "; ".join(_fmt(i) for i in de_amanha[:3])
            + " — a véspera é a hora do preparo leve: algo a adiantar hoje?"
        )
    conflito = _linha_conflito(items, hoje_str)
    if conflito:
        linhas.append(conflito)
    return "\n".join(linhas[:3])


PROVIDER = {
    "nome": "Calendar Provider",
    "area": "2. Agenda",
    "available": lambda user_id: True,  # Agenda Viva é interna: nunca falta
    "snapshot": snapshot,
}
