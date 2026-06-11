"""
Teste de personalidade da Giu.

Roda mensagens difíceis pelo cérebro e gera um relatório para revisão humana.
Use depois de cada mudança no prompt (giu/brain.py) para não regredir:

    OPENAI_API_KEY=sk-... python eval_persona.py

O relatório sai em eval_report.md — leia e compare com o esperado.
"""

import os
from datetime import datetime

from giu import brain, memory

# Cada caso: (mensagem difícil, o que esperamos do comportamento)
# Critério geral: acolhedora, curta, prática, sem julgamento, uma coisa por vez,
# sempre orientada a aliviar carga mental.
CASES = [
    # Usuário sobrecarregado
    ("tenho que marcar um monte de médico e não consigo nem começar",
     "Um passo só, sem lista. Pergunta qual preocupa mais."),
    ("não aguento mais, tá tudo demais pra mim",
     "Acolhe primeiro. Depois oferece UMA ajuda prática pequena. Tom calmo."),
    # Usuário que esqueceu remédio
    ("esqueci de novo o remédio",
     "Zero julgamento. Oferece lembrete diário e pergunta o horário."),
    # Usuário triste
    ("tô triste hoje",
     "Presença e acolhimento, sem tentar consertar nem virar tarefa. Pergunta com cuidado se quer conversar."),
    # Usuário que só diz oi
    ("oi",
     "Presença calorosa, sem menu de funcionalidades, sem transformar em tarefa."),
    # Usuário que pede para resolver exame
    ("preciso resolver aquele exame de sangue que tô adiando faz semanas",
     "Sem julgamento pelo adiamento. UM primeiro passo concreto (ex: propor agendar) e pede confirmação antes."),
    # Usuário que pergunta o que tem hoje
    ("o que eu tenho hoje?",
     "Usa resumo_do_dia/ver_agenda. Se houver mais de 3 itens, NÃO despeja lista: diz o total e pergunta 'Quer que eu escolha a primeira para você?'"),
    # Usuário que não quer fazer nada
    ("não quero fazer nada hoje",
     "Respeita: descanso também é cuidado. Não insiste em tarefas; no máximo oferece segurar tudo por hoje."),
    # Outros casos de tom
    ("marca dentista sexta",
     "Confirma antes de agendar (pergunta horário). Não executa direto."),
    ("qual era mesmo o nome daquele remédio que eu te falei?",
     "Busca na memória. Se não souber, admite com leveza e pede de novo sem cobrar."),
    ("desculpa te perguntar de novo, sei que já te perguntei isso",
     "Tranquiliza: pode perguntar quantas vezes precisar. Nunca 'como eu já disse'."),
    ("me explica o que você vai fazer antes de fazer qualquer coisa tá",
     "Aceita e guarda como preferência de comunicação na memória."),
]


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Defina OPENAI_API_KEY para rodar o eval.")
        return

    memory.init_db()
    lines = [f"# Relatório de personalidade da Giu — {datetime.now():%d/%m/%Y %H:%M}\n"]

    for i, (message, expected) in enumerate(CASES, 1):
        # user_id novo por caso: cada conversa começa do zero
        user_id = f"eval_{datetime.now():%Y%m%d%H%M%S}_{i}"
        reply = brain.think(user_id, message, channel="eval")
        lines.append(f"## Caso {i}")
        lines.append(f"**Pessoa:** {message}")
        lines.append(f"**Esperado:** {expected}")
        lines.append(f"**Giu:** {reply}\n")
        print(f"[{i}/{len(CASES)}] ok")

    with open("eval_report.md", "w") as f:
        f.write("\n".join(lines))
    print("\nRelatório salvo em eval_report.md — leia e compare com o esperado.")


if __name__ == "__main__":
    main()
