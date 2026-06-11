"""
Onboarding conversacional — a primeira conversa da Giu com a pessoa.

Não é um formulário: é uma conversa com UMA pergunta por mensagem.
O progresso fica em profile.data["onboarding"] e o cérebro recebe
instruções apenas da etapa atual. Etapas:

1. pendencia_inicial — apresentação + "qual a primeira coisa que você
   vive esquecendo ou adiando?"
2. nome — "como você prefere que eu te chame?"
3. consentimento — "posso guardar suas preferências para cuidar melhor de você?"
"""

from . import memory

STEPS = [
    (
        "pendencia_inicial",
        "Apresente-se com tom acolhedor: você é a Giu, uma companheira que ajuda a "
        "lembrar, organizar e resolver UMA coisa de cada vez, para a pessoa não precisar "
        "carregar tudo na cabeça. Depois faça SÓ esta pergunta: qual é a primeira coisa "
        "que ela vive esquecendo ou adiando? Quando ela responder, chame "
        "registrar_onboarding(campo='pendencia_inicial', valor=<resposta dela>).",
    ),
    (
        "nome",
        "Agradeça a resposta anterior com leveza (diga que vão cuidar disso juntas, sem "
        "pressa) e faça SÓ esta pergunta: como ela prefere ser chamada? Quando responder, "
        "chame registrar_onboarding(campo='nome', valor=<nome>).",
    ),
    (
        "consentimento",
        "Use o nome dela pela primeira vez e faça SÓ esta pergunta: se ela permite que "
        "você guarde as preferências dela (gostos, rotina, saúde) para cuidar melhor — "
        "explicando em uma frase que os dados são dela e ela pode ver ou apagar tudo "
        "quando quiser. Quando responder, chame "
        "registrar_onboarding(campo='consentimento', valor='sim' ou 'nao').",
    ),
]


def current_step(profile):
    """Próxima etapa pendente do onboarding, ou None se completo."""
    done = profile["data"].get("onboarding", {})
    for step, _ in STEPS:
        if step not in done:
            return step
    return None


def prompt_section(profile, is_first_contact):
    """Instruções de onboarding para o system prompt (ou '' se completo)."""
    step = current_step(profile)
    if step is None:
        return ""
    instruction = dict(STEPS)[step]
    opening = (
        "Esta é a PRIMEIRA conversa com esta pessoa. "
        if is_first_contact
        else "O onboarding ainda não terminou; retome com naturalidade, sem recomeçar do zero. "
    )
    return f"""
ONBOARDING EM ANDAMENTO (etapa: {step}):
{opening}{instruction}
REGRA ABSOLUTA: UMA pergunta por mensagem. Não pule etapas, não faça duas perguntas,
não apresente lista de funcionalidades. Se a pessoa mudar de assunto, atenda o que ela
precisa primeiro e retome o onboarding depois, com delicadeza."""


def register(user_id, campo, valor):
    """Grava a resposta de uma etapa e marca o progresso no perfil."""
    profile = memory.get_profile(user_id)
    done = profile["data"].get("onboarding", {})
    done[campo] = True

    if campo == "pendencia_inicial":
        memory.remember_fact(user_id, f"Vive esquecendo ou adiando: {valor}", "pendencias")
        memory.set_profile(user_id, onboarding=done)
        return "Pendência inicial guardada. Continue para a próxima etapa do onboarding."

    if campo == "nome":
        memory.set_profile(user_id, name=valor, onboarding=done)
        memory.remember_fact(user_id, f"Prefere ser chamada de {valor}", "identidade")
        return f"Nome guardado: {valor}. Continue para a próxima etapa do onboarding."

    if campo == "consentimento":
        consent = str(valor).strip().lower() in ("sim", "s", "yes", "pode", "claro", "true")
        memory.set_profile(user_id, onboarding=done, consentimento=consent)
        memory.remember_fact(
            user_id,
            "Autorizou guardar preferências para ser melhor cuidada" if consent
            else "NÃO autorizou guardar preferências — guarde apenas o essencial e pergunte antes",
            "limites",
        )
        return (
            "Consentimento registrado. Onboarding completo — agradeça e diga que está aqui "
            "a partir de agora, sem listar funcionalidades."
        )

    return f"Campo de onboarding desconhecido: {campo}"
