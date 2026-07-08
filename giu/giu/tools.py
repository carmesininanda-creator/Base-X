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

from . import config, memory, onboarding
from .channels import telegram, whatsapp
from .integrations import google_calendar


def _send_now_sync(target_user_id, text):
    """Entrega SÍNCRONA e verificada a um destino, pelo canal com push dele.
    Retorna True se entregue. Para fluxos que não podem esperar o scheduler."""
    channel = memory.last_push_channel(target_user_id)
    if channel == "whatsapp":
        return whatsapp.send_message_sync(target_user_id, text)
    if channel == "telegram":
        return telegram.send_message_sync(target_user_id, text)
    # Sem canal com push conhecido: tenta WhatsApp direto (contato de emergência
    # externo que ainda não conversou com a Giu)
    return whatsapp.send_message_sync(target_user_id, text)

log = logging.getLogger("giu.tools")

# Escopos de permissão: núcleo liberado; ações futuras nascem DESLIGADAS
SCOPES = {
    "agenda": True,
    "lembretes": True,
    "compartilhamento": True,  # sempre com confirmação por uso
    "email": False,
    "transporte": False,
    "comida": False,
    "pagamentos": False,
    "casa": False,
}
# Mapeia tipo de ação pendente → escopo exigido
ACTION_SCOPES = {
    "agendar": "agenda",
    "remarcar": "agenda",
    "cancelar_compromisso": "agenda",
    "criar_lembrete": "lembretes",
    "compartilhar": "compartilhamento",
    "email": "email",
    "transporte": "transporte",
    "comida": "comida",
    "pagamentos": "pagamentos",
    "casa": "casa",
}


def _scope_allowed(user_id, scope):
    perms = memory.get_profile(user_id)["data"].get("permissoes", {})
    return perms.get(scope, SCOPES.get(scope, False))


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
                        # 'limites' é reservada aos registros internos de consentimento/
                        # permissão (escritos por código confiável) — fora do enum, o modelo
                        # não pode usá-la para contornar o gate de consentimento.
                        "enum": ["identidade", "comunicacao", "preferencias", "saude", "rotina",
                                 "familia", "pendencias", "afeto", "geral"],
                    },
                },
                "required": ["fato"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_onboarding",
            "description": (
                "Registra a resposta de uma etapa do onboarding (primeira conversa). "
                "Use assim que a pessoa responder a pergunta da etapa atual."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "campo": {"type": "string", "enum": ["pendencia_inicial", "nome", "consentimento"]},
                    "valor": {"type": "string"},
                },
                "required": ["campo", "valor"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "abrir_missao",
            "description": (
                "Abre uma MISSÃO: um cuidado com começo, acompanhamento e fim (ex.: organizar "
                "o dia, lembrar algo importante, montar lista de compras, organizar consulta ou "
                "exame, ajudar numa decisão prática). LIFE RADAR: use SOMENTE quando existir "
                "fricção REAL ou a pessoa pedir ajuda — NUNCA transforme conversa em tarefa. "
                "INVISÍVEL: nunca diga 'abri uma missão' — diga 'deixa comigo' e converse natural."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "objetivo": {"type": "string", "description": "O que esta missão cuida. Ex: 'Organizar a consulta da mãe da Nanda'"},
                    "contexto": {"type": "string", "description": "O que importa saber (quem, quando, por quê)"},
                    "prioridade": {"type": "string", "enum": ["baixa", "normal", "alta"]},
                    "proximo_passo": {"type": "string", "description": "O menor próximo passo concreto"},
                    "criterio_conclusao": {"type": "string", "description": "Como saberemos que está RESOLVIDO de verdade (não só lembrado). Ex: 'consulta realizada e receita em mãos'"},
                },
                "required": ["objetivo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "atualizar_missao",
            "description": (
                "Registra progresso numa missão viva: nota de histórico, novo próximo passo, "
                "estado (aberta/em_andamento/aguardando) ou prioridade. Use sempre que algo "
                "andar — é assim que você acompanha até o fim. Nota é permitida até em missão "
                "concluída (ex.: registrar 'VIDA: ...' com a resposta da pessoa)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "missao_id": {"type": "integer"},
                    "nota": {"type": "string", "description": "O que aconteceu/mudou"},
                    "proximo_passo": {"type": "string"},
                    "estado": {"type": "string", "enum": ["aberta", "em_andamento", "aguardando"]},
                    "prioridade": {"type": "string", "enum": ["baixa", "normal", "alta"]},
                },
                "required": ["missao_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "concluir_missao",
            "description": (
                "Fecha uma missão quando o CRITÉRIO DE CONCLUSÃO foi atingido (resolvido de "
                "verdade, não só lembrado) — OU quando a pessoa disser que não quer/não "
                "precisa mais: desistir também encerra, com ZERO julgamento (resultado ex.: "
                "'encerrada a pedido dela'). Confirme com a pessoa antes, se houver dúvida."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "missao_id": {"type": "integer"},
                    "resultado": {"type": "string", "description": "Como terminou. Ex: 'consulta feita, receita em mãos'"},
                },
                "required": ["missao_id", "resultado"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ver_missao",
            "description": "Detalhes e histórico de uma missão da pessoa (para retomar com contexto).",
            "parameters": {
                "type": "object",
                "properties": {"missao_id": {"type": "integer"}},
                "required": ["missao_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "anotar_fio",
            "description": (
                "Anota um item na ESPINHA DA CONVERSA ATUAL (Conversation Spine) para "
                "não perder o fio em conversas longas. Use na hora em que surgir: decisão "
                "importante, frase forte da pessoa, hipótese nova, mudança de direção, "
                "insight, preferência revelada, compromisso assumido, tema que não pode se "
                "perder. NÃO é memória permanente (isso é lembrar_fato): a espinha expira; "
                "serve para você acompanhar ESTA conversa do início ao fim."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nota": {"type": "string", "description": "O item do fio, curto e claro. Ex: 'DECISÃO: prioridade da semana é o prazo do projeto, não a mudança' ou 'Ela disse: \"eu só queria uma pausa\"'"},
                },
                "required": ["nota"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "anotar_data",
            "description": (
                "Guarda uma DATA QUERIDA ou importante que a pessoa contou (aniversário de "
                "alguém, data marcante, evento anual) para você lembrar NO DIA e na véspera "
                "com carinho — nunca como notificação. Use quando ela contar uma data que "
                "importa para a vida dela. Datas de compromisso com hora marcada continuam "
                "na agenda (agendar); aqui vivem as datas do coração e do calendário dela."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "description": "O que é a data, em linguagem de vida. Ex: 'Aniversário da mãe dela (dona Cida)'"},
                    "data": {"type": "string", "description": "'MM-DD' = repete todo ano (aniversários; ex: '09-21'). 'YYYY-MM-DD' = data única (não volta no ano seguinte)"},
                    "recorrente": {"type": "boolean", "description": "Só para 'YYYY-MM-DD' com ano conhecido que deva repetir todo ano (ex: aniversário '1967-09-21'). 'MM-DD' já é sempre anual"},
                },
                "required": ["titulo", "data"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "esquecer_fato",
            "description": (
                "APAGA da memória permanente os fatos que contêm o trecho — imediato. "
                "Use quando a pessoa pedir para esquecer algo, quando um fato estiver "
                "errado, ou quando uma pendência guardada como fato foi RESOLVIDA "
                "('já resolvi' também é motivo de apagar). Registros de consentimento "
                "não são apagáveis por aqui."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "trecho": {"type": "string", "description": "Trecho do fato a esquecer (mínimo 3 letras). Ex: 'comprovante para o consulado'"},
                },
                "required": ["trecho"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "silenciar_pendencia",
            "description": (
                "Quando a pessoa disser que NÃO QUER ajuda com uma pendência (sem tê-la "
                "resolvido), silencia a OFERTA para sempre — a pendência continua viva em "
                "ver_agenda, mas você nunca mais oferece; só a pessoa reabre o assunto. "
                "NUNCA use concluir_compromisso para isso: seria fingir que foi feito."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "description": "Título exato da pendência (como está em ver_agenda). Ex: 'Renovar CNH'"},
                },
                "required": ["titulo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "esquecer_data",
            "description": (
                "ESQUECE uma data guardada, imediatamente — 'esquece essa data' tem a mesma "
                "dignidade de 'esquece minha cidade'. Use quando a pessoa pedir para não "
                "lembrar mais de uma data (ou quando registrou errado e vai corrigir)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "description": "Título (ou parte dele) da data a esquecer. Ex: 'aniversário do ex'"},
                },
                "required": ["titulo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "definir_cidade",
            "description": (
                "Registra a CIDADE da pessoa (nível cidade, NUNCA localização precisa) — "
                "permite você falar do clima, do frio que chegou e do pôr do sol com "
                "naturalidade. SÓ use depois que ela contar a cidade E topar que você "
                "acompanhe o tempo de lá (opt-in explícito; é opcional e revogável). "
                "Para ESQUECER a cidade quando ela pedir, chame com cidade vazia ''."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cidade": {"type": "string", "description": "Nome da cidade (ex: 'São Paulo'). String vazia '' = esquecer a cidade agora"},
                },
                "required": ["cidade"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "definir_preferencia_voz",
            "description": (
                "Registra como a pessoa prefere RECEBER as respostas daqui pra frente: "
                "'voz', 'texto' ou 'ambos'. É uma preferência de RELACIONAMENTO (a decisão "
                "é dela, não uma configuração), respeitada de forma determinística. Use "
                "quando ela disser como prefere (ex.: 'me responde só por escrito', "
                "'pode mandar áudio'). Ela pode mudar quando quiser."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "preferencia": {"type": "string", "enum": ["voz", "texto", "ambos"]},
                },
                "required": ["preferencia"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "conectar_agenda",
            "description": (
                "Gera o link pessoal para a pessoa conectar a agenda Google DELA "
                "(opt-in, revogável a qualquer momento). Use SOMENTE quando ela pedir "
                "para conectar a agenda, ou aceitar uma oferta sua explícita. NUNCA "
                "insista; 'não' encerra o assunto."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "desconectar_agenda",
            "description": (
                "Desconecta a agenda Google da pessoa IMEDIATAMENTE (revogação). "
                "Use quando ela pedir ('desconecta minha agenda'). Sem julgamento, "
                "sem perguntar por quê."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "resumo_do_dia",
            "description": (
                "Resumo do dia da pessoa: pendências, lembretes, agenda, saúde e uma sugestão "
                "de bem-estar. Use quando ela perguntar 'o que tenho hoje?' ou no check-in."
            ),
            "parameters": {"type": "object", "properties": {}},
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
                    "lugar": {"type": "string", "description": "ONDE acontece (clínica, endereço, bairro) — vale ouro para a véspera e o deslocamento"},
                    "duracao_minutos": {"type": "integer", "description": "Quanto dura, em minutos, se souber — protege a agenda de sobreposição"},
                    "notas": {"type": "string", "description": "Médico, preparos, o que levar, etc."},
                },
                "required": ["titulo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remarcar_compromisso",
            "description": (
                "Propõe REMARCAR um compromisso existente (nova data/hora/lugar/duração). "
                "NÃO executa: cria uma ação pendente — apresente o resumo ('dentista vai de "
                "terça 15h para quinta 10h, fecho?') e chame confirmar_acao após o sim. "
                "O id vem de ver_agenda. A vida remarca o tempo todo: isto é cuidado, não falha."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "id do compromisso (ver_agenda)"},
                    "nova_data": {"type": "string", "description": "YYYY-MM-DD, se mudar"},
                    "nova_hora": {"type": "string", "description": "HH:MM, se mudar"},
                    "novo_lugar": {"type": "string", "description": "se mudar"},
                    "nova_duracao_minutos": {"type": "integer", "description": "se souber"},
                },
                "required": ["id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancelar_compromisso",
            "description": (
                "Propõe CANCELAR um compromisso que não vai mais acontecer. NÃO executa: "
                "cria uma ação pendente — confirme com a pessoa e chame confirmar_acao. "
                "Cancelar é DIFERENTE de concluir (nunca finja que foi feito) e de "
                "silenciar (a pendência que ela não quer ajuda continua viva). "
                "O id vem de ver_agenda."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "id do compromisso (ver_agenda)"},
                },
                "required": ["id"],
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
                    "quando": {"type": "string", "description": "PRIMEIRA ocorrência, ISO: YYYY-MM-DDTHH:MM"},
                    "recorrencia": {"type": "string", "description": "Se repete: 'diario' | 'semanal' (na mesma semana-dia do 'quando') | 'mensal' (no mesmo dia do mês; 31 vira o último) | 'dias:seg,qua,sex'. Omitir = lembrete único"},
                },
                "required": ["texto", "quando"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "parar_lembrete",
            "description": (
                "'PODE PARAR' É LEI: encerra na hora os lembretes ativos que contêm o "
                "trecho (únicos ou recorrentes). Use quando a pessoa disser 'pode parar "
                "de lembrar', 'não preciso mais', 'a fisio acabou'. ZERO culpa, zero "
                "'tem certeza?' — parar é tão fácil quanto criar; recomeçar também."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "trecho": {"type": "string", "description": "Trecho do texto do lembrete (mín. 3 letras). Ex: 'fisioterapia'"},
                },
                "required": ["trecho"],
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
            "name": "compartilhar_com_familia",
            "description": (
                "Envia um recado da pessoa para OUTRO membro da família. NÃO executa: cria "
                "ação pendente. Mostre a mensagem exata e o destinatário e peça confirmação. "
                "Só a mensagem é enviada — nunca o histórico. Use apenas quando a pessoa pedir."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "para": {"type": "string", "description": "Nome do membro da família que vai receber"},
                    "mensagem": {"type": "string", "description": "O recado exato a enviar"},
                },
                "required": ["para", "mensagem"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "gerenciar_permissao",
            "description": (
                "Liga ou desliga uma permissão de ação futura (email, transporte, comida, "
                "pagamentos, casa). Use apenas quando a pessoa pedir explicitamente."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "escopo": {"type": "string", "enum": ["email", "transporte", "comida", "pagamentos", "casa", "compartilhamento"]},
                    "conceder": {"type": "boolean"},
                },
                "required": ["escopo", "conceder"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "acionar_emergencia",
            "description": (
                "SOMENTE em risco sério (saúde/segurança): avisa o contato de emergência da "
                "pessoa com um TEMPLATE FIXO (o motivo fica só no registro interno, nunca é "
                "enviado). Pergunte UMA vez antes, exceto se a pessoa pediu socorro explicitamente."
            ),
            "parameters": {
                "type": "object",
                "properties": {"motivo": {"type": "string", "description": "Motivo para o registro interno de auditoria. Ex: 'pediu ajuda agora'"}},
                "required": ["motivo"],
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
            "description": "Marca um compromisso da agenda como concluído, pelo id (o id vem de ver_agenda).",
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
        user_id, payload["titulo"], payload.get("data"), payload.get("hora"),
        payload.get("notas"), payload.get("lugar"), payload.get("duracao_minutos"),
    )
    result = f"Compromisso #{item_id} adicionado à Agenda Viva."
    if google_calendar.is_configured(user_id) and payload.get("data"):
        try:
            link = google_calendar.create_event(
                payload["titulo"], payload["data"], payload.get("hora"), payload.get("notas"),
                duration_minutes=payload.get("duracao_minutos") or 60,
                user_id=user_id, location=payload.get("lugar"),
            )
            result += f" Também criei no Google Calendar: {link}"
        except Exception as e:
            log.warning("Falha ao criar evento no Google Calendar: %s", e)
            result += " (não consegui criar no Google Calendar, mas está salvo aqui)"
    return result


def _execute_remarcar(user_id, payload):
    item = memory.reschedule_agenda(
        user_id, payload["id"], payload.get("nova_data"), payload.get("nova_hora"),
        payload.get("novo_lugar"), payload.get("nova_duracao_minutos"),
    )
    if not item:
        return "Não encontrei esse compromisso ativo desta pessoa — nada foi remarcado."
    quando = f"{item['date'] or 'sem data'} {item['time'] or ''}".strip()
    resultado = f"Compromisso #{item['id']} remarcado: {item['title']} — {quando}"
    if item.get("lugar"):
        resultado += f" @ {item['lugar']}"
    if google_calendar.is_configured(user_id):
        resultado += (". HONESTIDADE: o espelho no Google ainda NÃO atualiza — se o evento "
                      "existe lá, avise a pessoa com leveza que lá continua o horário antigo.")
    return resultado + "."


def _execute_cancelar(user_id, payload):
    ok = memory.cancel_agenda(user_id, payload["id"])
    if not ok:
        return "Não encontrei esse compromisso ativo desta pessoa — nada foi cancelado."
    resultado = ("Compromisso cancelado (não vira 'feito' — cancelar é cancelar). "
                 "Confirme com leveza, sem lamento.")
    if google_calendar.is_configured(user_id):
        resultado += (" HONESTIDADE: no Google o evento continua — avise a pessoa "
                      "que lá ela precisa remover, por enquanto.")
    return resultado


def _execute_criar_lembrete(user_id, payload):
    memory.add_reminder(user_id, payload["texto"], payload["quando"],
                        payload.get("channel", "web"), payload.get("recorrencia"))
    if payload.get("recorrencia"):
        return (f"Lembrete recorrente criado (primeira vez: {payload['quando']}). "
                "Dito uma vez, cuidado para sempre — e lembre a pessoa, em UMA frase "
                "leve, que 'pode parar' encerra quando ela quiser.")
    return f"Lembrete criado para {payload['quando']}."


def _deliver_now(target_user_id, text):
    """Entrega uma mensagem proativa a um membro: vira lembrete vencido, que o
    scheduler envia em até 60s pelo canal com push da pessoa."""
    channel = memory.last_push_channel(target_user_id) or "web"
    memory.add_reminder(target_user_id, text, memory._now(), channel)


def _execute_compartilhar(user_id, payload):
    sender = memory.get_member(user_id)
    target = memory.get_member_by_name(payload["para"])
    if not target:
        return f"Não encontrei '{payload['para']}' na família — o recado NÃO foi enviado."
    if target["user_id"] == user_id:
        return "O destinatário é a própria pessoa — nada a enviar."
    sender_name = sender["name"] if sender else "alguém da família"
    _deliver_now(target["user_id"], f"💬 Recado de {sender_name} (pela Giu): {payload['mensagem']}")
    return f"Recado enviado para {target['name']}. Só a mensagem foi compartilhada, nada mais."


EXECUTORS = {
    "agendar": _execute_agendar,
    "remarcar": _execute_remarcar,
    "cancelar_compromisso": _execute_cancelar,
    "criar_lembrete": _execute_criar_lembrete,
    "compartilhar": _execute_compartilhar,
}


def execute_tool(name, arguments, user_id, channel="web"):
    """Executa uma ferramenta e devolve o resultado como texto para o modelo."""
    args = json.loads(arguments) if isinstance(arguments, str) else arguments

    if name == "lembrar_fato":
        memory.remember_fact(user_id, args["fato"], args.get("categoria", "geral"))
        return "Fato guardado na memória permanente."

    if name == "registrar_onboarding":
        return onboarding.register(user_id, args["campo"], args["valor"])

    if name == "abrir_missao":
        mid = memory.mission_create(
            user_id, args["objetivo"], args.get("contexto"),
            args.get("prioridade", "normal"), args.get("proximo_passo"),
            args.get("criterio_conclusao"),
        )
        return (
            f"Missão #{mid} aberta (invisível para a pessoa — fale natural: 'deixa comigo'). "
            "Conduza um passo de cada vez, no tom do Blueprint dela, e acompanhe até o fim."
        )

    if name == "atualizar_missao":
        ok = memory.mission_update(
            user_id, args["missao_id"], args.get("nota"),
            args.get("proximo_passo"), args.get("estado"), args.get("prioridade"),
        )
        return "Missão atualizada." if ok else "Não encontrei essa missão desta pessoa."

    if name == "concluir_missao":
        ok = memory.mission_conclude(user_id, args["missao_id"], args["resultado"])
        if not ok:
            return "Não encontrei essa missão desta pessoa."
        return (
            "Missão concluída. Diga com naturalidade que está feito ('prontinho — cuidei "
            "disso'), com o crédito na pessoa quando foi ela quem agiu. Depois, com leveza "
            "(pode ser dias depois), verifique se isso tirou um peso DE VERDADE da vida dela "
            "e registre a resposta com atualizar_missao (nota começando com 'VIDA: ...') — "
            "é assim que medimos cuidado, não tarefas."
        )

    if name == "ver_missao":
        m = memory.mission_get(user_id, args["missao_id"])
        if not m:
            return "Não encontrei essa missão desta pessoa."
        eventos = "\n".join(f"  · {e['created_at'][:16]} {e['note']}" for e in m["events"][-6:])
        return (
            f"Missão #{m['id']} [{m['estado']}, prioridade {m['prioridade']}]: {m['objetivo']}\n"
            f"Contexto: {m['contexto'] or '-'}\nPróximo passo: {m['proximo_passo'] or '-'}\n"
            f"Critério de conclusão: {m['criterio_conclusao'] or '-'}\nHistórico recente:\n{eventos}"
        )

    if name == "anotar_fio":
        ok = memory.spine_add(user_id, args["nota"])
        return ("Anotado no fio da conversa." if ok
                else "Nota vazia — nada anotado.")

    if name == "anotar_data":
        ok = memory.dates_add(user_id, args["titulo"], args["data"],
                              args.get("recorrente"))
        if not ok:
            return ("Não consegui guardar (data em formato inválido ou memória "
                    "recusada pela pessoa). Formato: 'MM-DD' anual ou 'YYYY-MM-DD' única.")
        return ("Data guardada. Você vai revê-la no retrato do dia e da véspera — "
                "quando chegar, toque no assunto com carinho e no momento certo, "
                "nunca como notificação.")

    if name == "esquecer_fato":
        removidos = memory.facts_remove(user_id, args["trecho"])
        if not removidos:
            return ("Não encontrei fato com esse trecho (ou o trecho é curto demais — "
                    "use pelo menos 3 letras). Nada foi apagado.")
        return (f"{removidos} fato(s) apagado(s) AGORA. Se foi uma pendência resolvida, "
                "comemore com leveza — o crédito é dela.")

    if name == "silenciar_pendencia":
        ok = memory.pendencia_recusar(user_id, args["titulo"])
        if not ok:
            return "Título vazio — nada silenciado."
        return ("Oferta silenciada PARA SEMPRE (a pendência continua viva em ver_agenda; "
                "só ela reabre o assunto). Respeite: a partir de agora, silêncio total "
                "sobre isso, a menos que ELA puxe.")

    if name == "esquecer_data":
        removidas = memory.dates_remove(user_id, args["titulo"])
        if not removidas:
            return "Não encontrei data guardada com esse título — nada foi esquecido."
        return ("Data esquecida AGORA. Confirme com leveza — e sem drama: "
                "esquecer também é cuidar.")

    if name == "definir_cidade":
        cidade = (args.get("cidade") or "").strip()
        if not cidade:
            memory.city_clear(user_id)
            return ("Cidade esquecida AGORA. Confirme com leveza e ensine o gesto "
                    "de volta: quando quiser que você acompanhe o tempo de novo, é só dizer.")
        lat = lon = None
        nome = cidade
        try:
            from .integrations import open_meteo
            achado = open_meteo.geocodificar(cidade)
            if achado:
                nome, lat, lon = achado
        except Exception:
            pass  # sem geocodificação agora: guarda o nome; o clima chega depois
        if not memory.city_set(user_id, nome, lat, lon):
            return ("A pessoa recusou memória (consentimento) — a cidade NÃO foi "
                    "guardada. Respeite: sem registro, sem clima; a conversa segue normal.")
        if lat is None:
            return (f"Cidade registrada: {nome} — mas não consegui localizar o tempo de lá "
                    "agora (o clima fica de fora por enquanto). Se fizer sentido, confirme "
                    "a grafia com a pessoa e registre de novo; não transforme isso em problema dela.")
        return (f"Cidade registrada: {nome}. Agora o clima e o sol de lá entram no seu "
                "retrato do momento — use com naturalidade, só quando fizer bem. E lembre "
                "a ela, em uma frase leve, que é só a cidade (nada de localização) e que "
                "pode pedir para esquecer quando quiser.")

    if name == "definir_preferencia_voz":
        pref = {"voz": "voice", "texto": "text", "ambos": "both"}.get(args["preferencia"])
        if not pref:
            return "Preferência inválida. Use 'voz', 'texto' ou 'ambos'."
        # Flag determinístico no perfil (consultado no envio) + marca que já
        # perguntamos, para nunca re-perguntar (isso seria cobrança).
        memory.set_profile(user_id, voice_pref=pref, voice_pref_asked=True)
        rotulo = {"voice": "por voz", "text": "só por escrito", "both": "por voz e escrito"}[pref]
        memory.remember_fact(user_id, f"Prefere receber as respostas {rotulo}", "comunicacao")
        return (
            f"Preferência registrada: responder {rotulo}. Confirme isso em voz alta para a "
            "pessoa e ENSINE o gesto — que ela pode mudar quando quiser, é só falar "
            "(ex.: 'fechado, te respondo assim; quando quiser trocar, é só me dizer')."
        )

    if name == "conectar_agenda":
        if not (google_calendar.app_configured() and config.BASE_URL):
            return (
                "A conexão de agenda ainda não está disponível neste ambiente. Honestidade "
                "canônica: diga que poderá fazer isso quando a capacidade estiver disponível "
                "e ela decidir ativá-la — e que, enquanto isso, você já cuida dos compromissos "
                "por aqui (Agenda Viva)."
            )
        if google_calendar.is_connected(user_id):
            return "A agenda desta pessoa JÁ está conectada — diga que está tudo certo por lá."
        state = memory.oauth_state_new(user_id)
        url = google_calendar.auth_url(state)
        return (
            f"Envie este link para ELA MESMA autorizar (vale 15 minutos): {url}\n"
            "Explique leve e curto: é opcional, a agenda é só dela, e desconecta quando "
            "quiser — basta dizer 'desconecta minha agenda'. E diga em UMA frase o que "
            "você passa a ver e fazer: só os eventos da agenda dela (ver e criar), nada "
            "além — nem e-mail, nem contatos; a chave da conexão fica guardada aqui com "
            "a família e some na hora se ela desconectar."
        )

    if name == "desconectar_agenda":
        memory.google_disconnect(user_id)
        return (
            "Agenda desconectada AGORA. Confirme com leveza e ensine o gesto de volta: "
            "quando quiser reconectar, é só pedir."
        )

    if name == "resumo_do_dia":
        from . import routines
        summary = routines.daily_summary(user_id)
        n = len(summary["pendencias_hoje"])
        lines = [f"Pendências em aberto: {n}"]
        if n:
            lines += [f"- #{p['id']} {p['titulo']} {p['hora'] or ''}" for p in summary["pendencias_hoje"][:3]]
        if summary["lembretes"]:
            lines.append("Lembretes de hoje: " + "; ".join(r["texto"] for r in summary["lembretes"]))
        if summary["agenda"]:
            lines.append("Agenda de hoje: " + "; ".join(
                f"{a['titulo']} {a['hora'] or ''}" for a in summary["agenda"]))
        if summary["saude"]:
            lines.append("Saúde (memória): " + "; ".join(summary["saude"]))
        lines.append(f"Sugestão de bem-estar: {summary['sugestao_bem_estar']}")
        if n > 3:
            lines.append(
                f"ATENÇÃO UX: são {n} pendências — NÃO liste todas. Diga o total, "
                "destaque só a mais simples e pergunte: 'Quer que eu escolha a primeira para você?'"
            )
        return "\n".join(lines)

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

    if name == "remarcar_compromisso":
        if args.get("nova_data") and (err := _validate_date(args["nova_data"])):
            return err
        if args.get("nova_hora") and (err := _validate_time(args["nova_hora"])):
            return err
        if not any(args.get(k) for k in ("nova_data", "nova_hora", "novo_lugar",
                                          "nova_duracao_minutos")):
            return "Nada a mudar — confirme com a pessoa o que muda (data, hora, lugar ou duração)."
        item = next((i for i in memory.get_agenda(user_id) if i["id"] == args["id"]), None)
        if not item:
            return "Não encontrei esse compromisso ativo (o id vem de ver_agenda)."
        destino = f"{args.get('nova_data') or item['date'] or 'sem data'} {args.get('nova_hora') or item['time'] or ''}".strip()
        summary = f"Remarcar: {item['title']} → {destino}"
        action_id = memory.add_pending_action(user_id, "remarcar", summary, args, "baixo")
        return (
            f"Ação pendente #{action_id} criada: {summary}. "
            "Apresente o resumo e pergunte se a pessoa confirma. "
            f"Se ela confirmar, chame confirmar_acao com action_id={action_id}."
        )

    if name == "cancelar_compromisso":
        item = next((i for i in memory.get_agenda(user_id) if i["id"] == args["id"]), None)
        if not item:
            return "Não encontrei esse compromisso ativo (o id vem de ver_agenda)."
        summary = f"Cancelar: {item['title']} — {item['date'] or 'sem data'} {item['time'] or ''}".strip()
        action_id = memory.add_pending_action(user_id, "cancelar_compromisso", summary, args, "baixo")
        return (
            f"Ação pendente #{action_id} criada: {summary}. "
            "Confirme com a pessoa (cancelar não é concluir). "
            f"Após o sim, chame confirmar_acao com action_id={action_id}."
        )

    if name == "criar_lembrete":
        if err := _validate_due(args["quando"]):
            return err
        if args.get("recorrencia") and not memory.recorrencia_valida(args["recorrencia"]):
            return ("Recorrência inválida. Use 'diario', 'semanal', 'mensal' ou "
                    "'dias:seg,qua,sex' (dias: seg ter qua qui sex sab dom).")
        payload = {**args, "channel": channel}
        rotulo_rec = {"diario": " (todo dia)", "semanal": " (toda semana)",
                      "mensal": " (todo mês)"}.get(args.get("recorrencia") or "",
                      f" ({args['recorrencia']})" if args.get("recorrencia") else "")
        summary = f"Lembrete: {args['texto']} em {args['quando']}{rotulo_rec}"
        action_id = memory.add_pending_action(user_id, "criar_lembrete", summary, payload, "baixo")
        return (
            f"Ação pendente #{action_id} criada: {summary}. "
            "Apresente o resumo e pergunte se a pessoa confirma. "
            f"Se ela confirmar, chame confirmar_acao com action_id={action_id}."
        )

    if name == "compartilhar_com_familia":
        target = memory.get_member_by_name(args["para"])
        if not target:
            return (
                f"'{args['para']}' não está na família registrada — diga isso à pessoa. "
                "Nada foi enviado."
            )
        summary = f"Enviar para {target['name']}: \"{args['mensagem']}\""
        action_id = memory.add_pending_action(
            user_id, "compartilhar", summary, {"para": target["name"], "mensagem": args["mensagem"]}, "medio"
        )
        return (
            f"Ação pendente #{action_id} criada: {summary}. Mostre a mensagem exata e o "
            f"destinatário e peça confirmação; se confirmar, chame confirmar_acao com action_id={action_id}."
        )

    if name == "gerenciar_permissao":
        profile = memory.get_profile(user_id)
        perms = profile["data"].get("permissoes", {})
        perms[args["escopo"]] = bool(args["conceder"])
        memory.set_profile(user_id, permissoes=perms)
        verbo = "liberada" if args["conceder"] else "desligada"
        memory.remember_fact(
            user_id, f"Permissão '{args['escopo']}' {verbo} pela própria pessoa", "limites"
        )
        return f"Permissão '{args['escopo']}' {verbo} e registrada na memória."

    if name == "acionar_emergencia":
        member = memory.get_member(user_id)
        contact = member and member.get("emergency_contact")
        if not contact:
            return (
                "Esta pessoa não tem contato de emergência configurado. Oriente a ligar "
                "192 (SAMU), 193 (Bombeiros) ou 190 (Polícia) conforme o caso."
            )
        name_str = member["name"] if member else "Um membro da família"
        # Template FIXO e determinístico: o texto do modelo (motivo) NUNCA é
        # enviado ao contato — vai apenas para a trilha de auditoria interna.
        # Entrega SÍNCRONA e verificada: o alerta de risco nunca pode silenciar.
        entregue = _send_now_sync(
            contact,
            f"🚨 EMERGÊNCIA (pela Giu): {name_str} precisa de ajuda AGORA. Entre em contato imediatamente.",
        )
        aid = memory.add_pending_action(
            user_id, "emergencia",
            f"Contato de emergência acionado: {args['motivo']} — entregue={entregue}", args, "alto",
        )
        memory.mark_action_executed(user_id, aid)
        if entregue:
            return "Contato de emergência avisado agora. Fique com a pessoa e, se precisar, ligue 192 (SAMU)."
        # Falha honesta: NÃO fingir que avisou
        return (
            "NÃO consegui avisar o contato de emergência automaticamente. "
            "Oriente a pessoa a ligar AGORA para 192 (SAMU), 193 (Bombeiros) ou 190 (Polícia), "
            "e avise você mesma alguém de confiança."
        )

    if name == "propor_acao":
        action_id = memory.add_pending_action(
            user_id, args["tipo"], args["resumo"], args.get("payload", {}), args.get("risco", "medio")
        )
        return f"Ação pendente #{action_id} criada: {args['resumo']}. Pergunte se a pessoa confirma."

    if name == "parar_lembrete":
        parados = memory.reminders_stop(user_id, args["trecho"])
        if not parados:
            return ("Não encontrei lembrete ativo com esse trecho — nada foi parado "
                    "(confira o texto com a pessoa, sem transformar isso em problema).")
        nomes = "; ".join(f'"{t}"' for t in parados)
        aviso = ("" if len(parados) == 1 else
                 " ATENÇÃO: mais de um parou — NOMEIE todos para ela e pergunte se "
                 "algum era para continuar (você recria na hora, sem drama).")
        return (f"Parado(s) AGORA: {nomes}.{aviso} Confirme com leveza e SEM "
                "lamento ('parei, viu? quando quiser de volta, é só me dizer') — "
                "parar é cuidado tanto quanto lembrar.")

    if name == "confirmar_acao":
        action = memory.get_pending_action(user_id, args["action_id"])
        if not action:
            return "Não encontrei essa ação pendente."
        if action["status"] != "pending":
            return f"Essa ação já está com status '{action['status']}' — nada a fazer."
        scope = ACTION_SCOPES.get(action["type"])
        if scope and not _scope_allowed(user_id, scope):
            return (
                f"A permissão '{scope}' está desligada para esta pessoa — a ação NÃO foi "
                "executada. Explique e pergunte se ela quer liberar (gerenciar_permissao)."
            )
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
        listing = "\n".join(f"#{a['id']} [{a['risk_level']}] {a['summary']}" for a in actions)
        if len(actions) > 3:
            listing = (
                f"ATENÇÃO UX: são {len(actions)} ações — NÃO liste todas. Diga o total e "
                "pergunte: 'Quer que eu escolha a primeira para você?'\n" + listing
            )
        return listing

    if name == "ver_agenda":
        lines = []
        items = memory.get_agenda(user_id)
        if len(items) > 3:
            lines.append(
                f"ATENÇÃO UX: são {len(items)} itens — NÃO liste todos para a pessoa. "
                "Diga o total, destaque só o mais simples ou mais próximo, e pergunte: "
                "'Quer que eu escolha a primeira para você?'"
            )
        if items:
            lines.append("Agenda Viva:")
            lines.extend(
                f"#{i['id']} {i['title']} — {i['date'] or 'sem data'} {i['time'] or ''}"
                + (f" @ {i['lugar']}" if i.get("lugar") else "")
                + (f" ({i['notes']})" if i["notes"] else "")
                for i in items
            )
        if google_calendar.is_configured(user_id):
            try:
                events = google_calendar.list_events(user_id=user_id)
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
