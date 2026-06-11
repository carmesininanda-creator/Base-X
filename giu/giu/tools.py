"""
As mãos da Giu — ferramentas que o cérebro pode usar durante a conversa.

Execução com autorização real: ações que mudam o mundo (agendar, criar
lembrete) NÃO executam direto. Elas criam uma ação pendente; a Giu apresenta
o resumo, a pessoa confirma na conversa, e só então confirmar_acao executa.
O fluxo propõe → confirma → executa deixa de depender só do modelo: está
registrado e auditável na tabela pending_actions.
"""

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from . import config, memory
from .integrations import google_calendar

log = logging.getLogger("giu.tools")


# ─── Validação de datas (o modelo erra; o sistema confere) ────────────────────

def _local_now():
    return datetime.now(ZoneInfo(config.TIMEZONE)).replace(tzinfo=None)


def _validate_date(value):
    """YYYY-MM-DD válido e não no passado. Retorna mensagem de erro ou None."""
    try:
        d = datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return f"Data inválida: '{value}'. Use o formato YYYY-MM-DD."
    if d < _local_now().date():
        return f"A data {value} já passou. Confirme a data com a pessoa."
    return None


def _validate_time(value):
    """HH:MM válido. Retorna mensagem de erro ou None."""
    try:
        datetime.strptime(value, "%H:%M")
    except (ValueError, TypeError):
        return f"Horário inválido: '{value}'. Use o formato HH:MM."
    return None


def _validate_due(value):
    """Data-hora ISO futura. Retorna mensagem de erro ou None."""
    try:
        due = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return f"Data-hora inválida: '{value}'. Use o formato YYYY-MM-DDTHH:MM."
    if due <= _local_now():
        return f"{value} já passou. Confirme com a pessoa quando ela quer o lembrete."
    return None


# ─── Definições no formato de function calling da OpenAI ─────────────────────

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
                        "enum": ["pessoas", "saude", "preferencias", "comunicacao", "rotina", "trabalho", "geral"],
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
            "description": (
                "Propõe adicionar um compromisso. NÃO executa: cria uma ação pendente. "
                "Apresente o resumo à pessoa e, quando ela confirmar, chame confirmar_acao."
            ),
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
            "name": "criar_lembrete",
            "description": (
                "Propõe um lembrete proativo. NÃO executa: cria uma ação pendente. "
                "Apresente o resumo à pessoa e, quando ela confirmar, chame confirmar_acao."
            ),
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
            "name": "confirmar_acao",
            "description": (
                "Executa uma ação pendente. Use SOMENTE depois que a pessoa confirmou "
                "explicitamente na conversa ('sim', 'pode', 'confirmo')."
            ),
            "parameters": {
                "type": "object",
                "properties": {"action_id": {"type": "integer"}},
                "required": ["action_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "listar_acoes_pendentes",
            "description": "Lista as ações propostas que ainda aguardam confirmação da pessoa.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propor_acao",
            "description": (
                "Propõe uma ação genérica que precisa de confirmação (para tipos que não têm "
                "ferramenta própria). Cria uma ação pendente com resumo e nível de risco."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string"},
                    "resumo": {"type": "string", "description": "Resumo claro do que será feito"},
                    "payload": {"type": "object", "description": "Dados necessários para executar"},
                    "risco": {"type": "string", "enum": ["baixo", "medio", "alto"]},
                },
                "required": ["tipo", "resumo"],
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


# ─── Execução das ações confirmadas ───────────────────────────────────────────

def _execute_agendar(user_id, payload):
    item_id = memory.add_agenda(
        user_id, payload["titulo"], payload.get("data"), payload.get("hora"), payload.get("notas")
    )
    result = f"Compromisso #{item_id} adicionado à Agenda Viva."
    if google_calendar.is_configured() and payload.get("data"):
        try:
            link = google_calendar.create_event(
                payload["titulo"], payload["data"], payload.get("hora"), payload.get("notas")
            )
            result += f" Também criei no Google Calendar: {link}"
        except Exception as e:
            log.warning("Falha ao criar evento no Google Calendar: %s", e)
            result += " (não consegui criar no Google Calendar, mas está salvo aqui)"
    return result


def _execute_criar_lembrete(user_id, payload):
    memory.add_reminder(user_id, payload["texto"], payload["quando"], payload.get("channel", "web"))
    return f"Lembrete criado para {payload['quando']}."


EXECUTORS = {
    "agendar": _execute_agendar,
    "criar_lembrete": _execute_criar_lembrete,
}


def execute_tool(name, arguments, user_id, channel="web"):
    """Executa uma ferramenta e devolve o resultado como texto para o modelo."""
    args = json.loads(arguments) if isinstance(arguments, str) else arguments

    if name == "lembrar_fato":
        memory.remember_fact(user_id, args["fato"], args.get("categoria", "geral"))
        return "Fato guardado na memória permanente."

    if name == "agendar":
        if args.get("data") and (err := _validate_date(args["data"])):
            return err
        if args.get("hora") and (err := _validate_time(args["hora"])):
            return err
        summary = f"Agendar: {args['titulo']} — {args.get('data') or 'sem data'} {args.get('hora') or ''}".strip()
        action_id = memory.add_pending_action(user_id, "agendar", summary, args, "baixo")
        return (
            f"Ação pendente #{action_id} criada: {summary}. "
            "Apresente o resumo e pergunte se a pessoa confirma. "
            f"Se ela confirmar, chame confirmar_acao com action_id={action_id}."
        )

    if name == "criar_lembrete":
        if err := _validate_due(args["quando"]):
            return err
        payload = {**args, "channel": channel}
        summary = f"Lembrete: {args['texto']} em {args['quando']}"
        action_id = memory.add_pending_action(user_id, "criar_lembrete", summary, payload, "baixo")
        return (
            f"Ação pendente #{action_id} criada: {summary}. "
            "Apresente o resumo e pergunte se a pessoa confirma. "
            f"Se ela confirmar, chame confirmar_acao com action_id={action_id}."
        )

    if name == "propor_acao":
        action_id = memory.add_pending_action(
            user_id, args["tipo"], args["resumo"], args.get("payload", {}), args.get("risco", "medio")
        )
        return f"Ação pendente #{action_id} criada: {args['resumo']}. Pergunte se a pessoa confirma."

    if name == "confirmar_acao":
        action = memory.get_pending_action(user_id, args["action_id"])
        if not action:
            return "Não encontrei essa ação pendente."
        if action["status"] != "pending":
            return f"Essa ação já está com status '{action['status']}' — nada a fazer."
        executor = EXECUTORS.get(action["type"])
        if not executor:
            memory.mark_action_executed(user_id, action["id"])
            return (
                f"Ação '{action['type']}' confirmada e registrada, mas ainda não sei executá-la "
                "automaticamente. Diga à pessoa o que ela pode fazer manualmente."
            )
        result = executor(user_id, action["payload"])
        memory.mark_action_executed(user_id, action["id"])
        return result

    if name == "listar_acoes_pendentes":
        actions = memory.list_pending_actions(user_id)
        if not actions:
            return "Nenhuma ação aguardando confirmação."
        return "\n".join(
            f"#{a['id']} [{a['risk_level']}] {a['summary']}" for a in actions
        )

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

    if name == "buscar_memoria":
        facts = memory.search_facts(user_id, args["consulta"])
        if not facts:
            return "Nada encontrado na memória sobre isso."
        return "\n".join(f"[{f['category']}] {f['content']}" for f in facts)

    return f"Ferramenta desconhecida: {name}"
