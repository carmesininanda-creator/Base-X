"""
As mãos da Giu — ferramentas que o cérebro pode usar durante a conversa.

Cada ferramenta segue o princípio: propõe → confirma → executa.
A confirmação acontece na conversa (o modelo só chama a ferramenta
depois que a pessoa confirma); aqui é só a execução.
"""

import json
import logging

from . import memory
from .integrations import google_calendar

log = logging.getLogger("giu.tools")

# Definições no formato de function calling da OpenAI
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "lembrar_fato",
            "description": (
                "Guarda um fato importante sobre a pessoa na memória permanente. "
                "Use sempre que a pessoa contar algo que vale lembrar para sempre: "
                "pessoas da vida dela, preferências, saúde, rotina, médicos, hábitos."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fato": {"type": "string", "description": "O fato, escrito de forma clara e completa. Ex: 'Pauline é filha da Nanda'"},
                    "categoria": {
                        "type": "string",
                        "enum": ["pessoas", "saude", "preferencias", "rotina", "trabalho", "geral"],
                    },
                },
                "required": ["fato"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "agendar",
            "description": "Adiciona um compromisso na Agenda Viva. Só use depois que a pessoa confirmar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string"},
                    "data": {"type": "string", "description": "Data no formato YYYY-MM-DD, se souber"},
                    "hora": {"type": "string", "description": "Horário HH:MM, se souber"},
                    "notas": {"type": "string", "description": "Endereço, médico, preparos, etc."},
                },
                "required": ["titulo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ver_agenda",
            "description": "Lista os compromissos da Agenda Viva da pessoa.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "concluir_compromisso",
            "description": "Marca um compromisso da agenda como concluído, pelo id.",
            "parameters": {
                "type": "object",
                "properties": {"id": {"type": "integer"}},
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "criar_lembrete",
            "description": "Cria um lembrete que a Giu enviará proativamente no horário marcado.",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto": {"type": "string", "description": "O que lembrar. Ex: 'Tomar o remédio da pressão'"},
                    "quando": {"type": "string", "description": "Data e hora ISO: YYYY-MM-DDTHH:MM"},
                },
                "required": ["texto", "quando"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_memoria",
            "description": "Busca na memória permanente fatos relacionados a um assunto.",
            "parameters": {
                "type": "object",
                "properties": {"consulta": {"type": "string"}},
                "required": ["consulta"],
            },
        },
    },
]


def execute_tool(name, arguments, user_id, channel="web"):
    """Executa uma ferramenta e devolve o resultado como texto para o modelo."""
    args = json.loads(arguments) if isinstance(arguments, str) else arguments

    if name == "lembrar_fato":
        memory.remember_fact(user_id, args["fato"], args.get("categoria", "geral"))
        return "Fato guardado na memória permanente."

    if name == "agendar":
        item_id = memory.add_agenda(
            user_id, args["titulo"], args.get("data"), args.get("hora"), args.get("notas")
        )
        result = f"Compromisso #{item_id} adicionado à Agenda Viva."
        if google_calendar.is_configured() and args.get("data"):
            try:
                link = google_calendar.create_event(
                    args["titulo"], args["data"], args.get("hora"), args.get("notas")
                )
                result += f" Também criei no Google Calendar: {link}"
            except Exception as e:
                log.warning("Falha ao criar evento no Google Calendar: %s", e)
                result += " (não consegui criar no Google Calendar, mas está salvo aqui)"
        return result

    if name == "ver_agenda":
        lines = []
        items = memory.get_agenda(user_id)
        if items:
            lines.append("Agenda Viva:")
            lines.extend(
                f"#{i['id']} {i['title']} — {i['date'] or 'sem data'} {i['time'] or ''}"
                + (f" ({i['notes']})" if i["notes"] else "")
                for i in items
            )
        if google_calendar.is_configured():
            try:
                events = google_calendar.list_events()
                if events:
                    lines.append("Google Calendar (próximos):")
                    lines.extend(
                        f"{e['title']} — {e['start']}" + (f" @ {e['location']}" if e["location"] else "")
                        for e in events
                    )
            except Exception as e:
                log.warning("Falha ao listar Google Calendar: %s", e)
                lines.append("(não consegui consultar o Google Calendar agora)")
        return "\n".join(lines) if lines else "A agenda está vazia."

    if name == "concluir_compromisso":
        ok = memory.complete_agenda(user_id, args["id"])
        return "Compromisso concluído." if ok else "Não encontrei esse compromisso."

    if name == "criar_lembrete":
        memory.add_reminder(user_id, args["texto"], args["quando"], channel)
        return f"Lembrete criado para {args['quando']}."

    if name == "buscar_memoria":
        facts = memory.search_facts(user_id, args["consulta"])
        if not facts:
            return "Nada encontrado na memória sobre isso."
        return "\n".join(f"[{f['category']}] {f['content']}" for f in facts)

    return f"Ferramenta desconhecida: {name}"
