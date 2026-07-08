"""
Rotinas humanas da Giu — check-in diário e resumo do dia.

O check-in é o início da sensação de companhia: a Giu aparece de manhã
e à noite, sem ser chamada, com UMA mensagem leve. O resumo diário junta
o invisível do dia (pendências, lembretes, agenda, saúde) com um toque
de cuidado — incluindo o ambiente.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from . import config, memory

# Sugestões leves de bem-estar — incluem o ambiente, porque a casa também cuida
WELLBEING_SUGGESTIONS = [
    "Que tal abrir a janela por uns minutos? Luz natural faz bem.",
    "Um copo de água agora pode ser um bom começo.",
    "Se der, uma caminhada curta hoje — sem meta, só pelo ar.",
    "Uma música calma de fundo pode deixar o dia mais leve.",
    "Cinco minutos de silêncio antes de começar também é cuidado.",
    "Um café ou chá sem pressa conta como pausa, viu?",
    "À noite, luz mais baixa ajuda o corpo a desacelerar.",
    "Um banho quente hoje pode ser o seu momento só seu.",
]

CARE_PHRASES = [
    "Estou por aqui o dia todo, no seu ritmo.",
    "Uma coisa de cada vez — o resto eu seguro pra você.",
    "Você não precisa dar conta de tudo hoje. Só do hoje.",
    "Se o dia apertar, me chama. Pra isso eu existo.",
    "O que você esquecer, eu lembro. Combinado?",
    "Hoje pode ser leve. Eu cuido do invisível.",
]


def _local_now():
    return datetime.now(ZoneInfo(config.TIMEZONE))


def _pending_count(user_id):
    """O bom dia fala do DIA. Pendências sem data têm porta própria (retrato
    da Comunicação, com a lei da oferta única) — contá-las toda manhã seria
    cobrança de baixa intensidade diária (dívida M4 da Life Architect, paga)."""
    today = _local_now().date().isoformat()
    agenda = [i for i in memory.get_agenda(user_id) if i["date"] and i["date"] <= today]
    return len(agenda) + len(memory.list_pending_actions(user_id))


def morning_message(user_id):
    """Mensagem de bom dia do check-in — curta, com no máximo um convite."""
    profile = memory.get_profile(user_id)
    name = profile["name"] or "você"
    n = _pending_count(user_id)
    if n == 0:
        return f"Bom dia, {name}. Hoje está leve por aqui: nenhuma pendência urgente. Como você acordou?"
    coisa = "coisa importante" if n == 1 else "coisas importantes"
    return (
        f"Bom dia, {name}. Hoje eu cuido das pendências com você. "
        f"Temos {n} {coisa}. Quer começar pela mais simples?"
    )


def night_message(user_id):
    """Mensagem de fechamento do dia."""
    return "Antes de encerrar o dia, quer que eu veja se ficou alguma pendência importante para amanhã?"


def daily_summary(user_id):
    """Resumo do dia: pendências, lembretes, agenda, saúde + um cuidado."""
    now = _local_now()
    today = now.date().isoformat()
    day_index = now.timetuple().tm_yday

    agenda = memory.get_agenda(user_id)
    agenda_hoje = [i for i in agenda if i["date"] == today]
    pendencias = [i for i in agenda if not i["date"] or i["date"] <= today]
    lembretes = [r for r in memory.reminders_today(user_id)]
    saude = [f["content"] for f in memory.get_facts(user_id) if f["category"] == "saude"][-3:]

    return {
        "data": today,
        "pendencias_hoje": [
            {"id": i["id"], "titulo": i["title"], "hora": i["time"]} for i in pendencias
        ],
        "lembretes": [{"texto": r["text"], "quando": r["due_at"]} for r in lembretes],
        "agenda": [
            {"titulo": i["title"], "hora": i["time"], "notas": i["notes"]} for i in agenda_hoje
        ],
        "saude": saude,
        "sugestao_bem_estar": WELLBEING_SUGGESTIONS[day_index % len(WELLBEING_SUGGESTIONS)],
        "frase_cuidado": CARE_PHRASES[day_index % len(CARE_PHRASES)],
    }
