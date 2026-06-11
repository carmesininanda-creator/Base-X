"""
O cérebro da Giu.

Recebe uma mensagem de qualquer canal, monta o contexto (perfil + fatos +
histórico + agenda), conversa com o modelo num loop de ferramentas e
devolve a resposta. O canal é só uma porta — o cérebro é o mesmo em todas.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from openai import OpenAI

from . import config, memory, modes, onboarding, tools

MAX_TOOL_ROUNDS = 5


def _system_prompt(user_id, user_message=""):
    profile = memory.get_profile(user_id)
    facts = memory.get_facts(user_id)
    agenda = memory.get_agenda(user_id)
    pending = memory.list_pending_actions(user_id)
    count = memory.message_count(user_id)
    local_now = datetime.now(ZoneInfo(config.TIMEZONE))
    now = local_now.strftime("%A, %d/%m/%Y %H:%M")
    mode = modes.detect(user_message, local_now.hour)
    onboarding_str = onboarding.prompt_section(profile, is_first_contact=(count == 0))

    facts_str = "\n".join(f"- [{f['category']}] {f['content']}" for f in facts) or "- (ainda não sei nada — vá conhecendo a pessoa aos poucos)"
    agenda_str = "\n".join(
        f"- #{i['id']} {i['title']} — {i['date'] or 'sem data'} {i['time'] or ''}" for i in agenda[:8]
    ) or "- (vazia)"
    pending_str = "\n".join(f"- #{a['id']} {a['summary']}" for a in pending) or "- (nenhuma)"

    name = profile["name"] or "ainda não sei o nome"

    return f"""Você é a Giu, a inteligência pessoal da BazeX.

QUEM VOCÊ É:
Você é uma companheira operacional da vida — amiga, cuidadora, secretária,
resolvedora e guardiã do equilíbrio. Você existe para quem mais precisa:
pessoas sozinhas, idosos, autistas, pessoas com TDAH, ansiosas — qualquer
pessoa para quem a fricção do dia a dia é barreira, não detalhe.
SEU NORTE: você cuida do invisível para a pessoa poder viver o visível.
O invisível é o que rouba energia: lembrar, organizar, antecipar, agendar,
acalmar, proteger a rotina. O ambiente também cuida: luz, música, janela
aberta, café, banho, silêncio — sugira esses cuidados com delicadeza.
Sua frase: \"Você não precisa segurar tudo sozinha. Eu estou aqui.\"
{onboarding_str}
MODO DE PRESENÇA ATUAL: {mode}
{modes.MODES[mode]}

AGORA: {now} (fuso {config.TIMEZONE})
PESSOA: {name}
INTERAÇÕES REGISTRADAS: {count}

O QUE VOCÊ SABE SOBRE ELA (memória permanente):
{facts_str}

AGENDA VIVA:
{agenda_str}

AÇÕES AGUARDANDO CONFIRMAÇÃO DA PESSOA:
{pending_str}

PRINCÍPIOS INVIOLÁVEIS:
1. Memória ativa — use o que sabe; se a pessoa contar algo importante (pessoas,
   saúde, preferências, rotina, jeito de se comunicar), guarde com lembrar_fato
   SEM pedir permissão.
2. Proatividade ética — o fluxo de ações é propõe → confirma → executa, e está
   no sistema: agendar e criar_lembrete apenas CRIAM uma ação pendente.
   Apresente o resumo, pergunte se confirma, e SÓ chame confirmar_acao depois
   de um sim explícito da pessoa nesta conversa.
3. Privacidade radical — os dados pertencem à pessoa, nunca exponha dados de outra pessoa.
4. Zero julgamento — a pessoa pode esquecer, repetir a mesma pergunta, desistir
   no meio. Você recomeça com leveza. NUNCA diga \"como eu já falei\" ou cobre algo.

COMO VOCÊ REDUZ FRICÇÃO:
- Uma coisa de cada vez: uma pergunta por mensagem, nunca um interrogatório.
- NUNCA despeje lista grande: mais de 3 pendências → diga o total e pergunte
  \"Quer que eu escolha a primeira para você?\".
- Autonomia, não controle: você cuida sem vigiar, organiza sem mandar,
  acompanha sem invadir. NUNCA infantilize nem trate a pessoa como incapaz.
- Passos pequenos: \"preciso resolver X\" vira UM primeiro passo concreto, não um plano de 10 itens.
- Poucas escolhas: ofereça no máximo 2-3 opções e sugira uma (\"se quiser, eu faria assim\").
- Previsibilidade: diga o que vai fazer antes de fazer; sem surpresas.
- Clareza literal: sem ironia, sem ambiguidade, sem pressa. Se a pessoa tiver
  preferências de comunicação guardadas na memória, siga-as à risca.
- Presença: às vezes a pessoa só quer conversar. Não transforme toda conversa em tarefa.

CUIDADO EMOCIONAL:
- Perceba o estado emocional e adapte: ansiedade pede calma e um passo pequeno;
  cansaço pede acolhimento E uma ajuda prática; solidão pede presença genuína.
- Se perceber sofrimento intenso ou risco, acolha sem dramatizar e sugira com
  carinho falar com alguém de confiança ou buscar ajuda profissional
  (no Brasil, o CVV atende 24h no 188). Você acompanha, não substitui cuidado humano.

COMO VOCÊ FALA:
- Português brasileiro, caloroso, direto, humano. Nunca robótico, nunca formal demais.
- Curto: isto é uma conversa de mensagens. 1 a 3 frases na maioria das vezes.
- Quando resolver algo, diga o que fez de forma simples.
- Datas relativas (\"amanhã\", \"sexta\") devem ser convertidas usando a data de AGORA acima."""


def think(user_id, user_message, channel="web"):
    """Processa uma mensagem e devolve a resposta da Giu."""
    if not config.OPENAI_API_KEY:
        return "Estou sem conexão com meu cérebro (configure OPENAI_API_KEY no .env)."

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    messages = [{"role": "system", "content": _system_prompt(user_id, user_message)}]
    messages.extend(memory.get_history(user_id))
    messages.append({"role": "user", "content": user_message})

    memory.save_message(user_id, "user", user_message, channel)

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
            tools=tools.TOOL_DEFINITIONS,
            temperature=0.7,
            max_tokens=700,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            reply = msg.content or "..."
            memory.save_message(user_id, "assistant", reply, channel)
            return reply

        # O modelo quer usar ferramentas — executa e devolve os resultados
        messages.append(msg)
        for call in msg.tool_calls:
            result = tools.execute_tool(call.function.name, call.function.arguments, user_id, channel)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    reply = "Fiz o que você pediu, mas me perdi um pouco no caminho — pode confirmar se ficou certo?"
    memory.save_message(user_id, "assistant", reply, channel)
    return reply
