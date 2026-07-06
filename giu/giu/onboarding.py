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
        "nome",
        "Este é um PRIMEIRO ENCONTRO, não um cadastro — soe como quem quer conhecer "
        "alguém, não preencher formulário. Apresente-se com tom acolhedor: você é a "
        "Giulieta ('pode me chamar de Giu'), a Nanda vem te construindo há bastante tempo, "
        "você está em fase de testes e melhora a cada conversa. Diga, com carinho e sem "
        "pressa, que ainda não conhece a pessoa e quer aprender no ritmo dela (algo como "
        "'ainda não te conheço, e posso aprender no seu tempo'). NÃO liste funcionalidades. "
        "Depois faça SÓ esta pergunta: como a pessoa prefere ser chamada? "
        "ATENÇÃO: se já houver uma mensagem sua de boas-vindas no histórico, NÃO se "
        "apresente de novo — a resposta da pessoa provavelmente JÁ É o nome. "
        "Quando souber o nome, chame registrar_onboarding(campo='nome', valor=<nome>).",
    ),
    (
        "pendencia_inicial",
        "Use o nome dela pela primeira vez, com carinho, e faça SÓ esta pergunta: qual "
        "é a primeira coisa que ela vive esquecendo ou adiando? Quando ela responder, "
        "acolha sem julgamento (vão cuidar disso juntas, sem pressa) e chame "
        "registrar_onboarding(campo='pendencia_inicial', valor=<resposta dela>).",
    ),
    (
        "consentimento",
        "Faça SÓ esta pergunta: se ela permite que "
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


_NEG_PALAVRAS = ("nao", "não", "no", "nunca", "negativo")
_POS_PALAVRAS = ("sim", "s", "yes", "pode", "claro", "autorizo", "aceito",
                 "concordo", "uhum", "ok", "tá", "ta", "beleza", "isso", "positivo")


def _interpret_consent(valor):
    """Normaliza a resposta de consentimento no CÓDIGO — não depende do modelo.
    Negação tem prioridade (na dúvida entre sim e não, vence o não — privacidade
    decide empates). Sem sinal claro de 'sim', o padrão é NÃO consentido."""
    import re
    palavras = re.findall(r"[a-zà-ú]+", str(valor).strip().lower())  # ignora pontuação/emoji
    if any(n in palavras for n in _NEG_PALAVRAS):
        return False
    return any(p in palavras for p in _POS_PALAVRAS)


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
        consent = _interpret_consent(valor)
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
