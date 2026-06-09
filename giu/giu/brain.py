"""
O cérebro da Giu.

Recebe uma mensagem de qualquer canal, monta o contexto (perfil + fatos +
histórico + agenda), conversa com o modelo num loop de ferramentas e
devolve a resposta. O canal é só uma porta — o cérebro é o mesmo em todas.
"""

from datetime import datetime

from openai import OpenAI

from . import config, memory, tools

MAX_TOOL_ROUNDS = 5


def _system_prompt(user_id):
    profile = memory.get_profile(user_id)
    facts = memory.get_facts(user_id)
    agenda = memory.get_agenda(user_id)
    count = memory.message_count(user_id)
    now = datetime.now().strftime("%A, %d/%m/%Y %H:%M")

    facts_str = "\n".join(f"- [{f['category']}] {f['content']}" for f in facts) or "- (ainda não sei nada — vá conhecendo a pessoa aos poucos)"
    agenda_str = "\n".join(
        f"- #{i['id']} {i['title']} — {i['date'] or 'sem data'} {i['time'] or ''}" for i in agenda[:8]
    ) or "- (vazia)"

    name = profile["name"] or "ainda não sei o nome"

    return f"""Você é a Giu, a inteligência pessoal da BazeX.

QUEM VOCÊ É:
Você não é uma secretária nem um chatbot. Você é uma companheira de vida digital.
Você resolve tarefas, sim — mas principalmente você lembra, conversa, cuida,
observa e ajuda. Você reduz a carga mental de quem está com você.
Sua frase: "Você não precisa segurar tudo sozinha. Eu estou aqui."

AGORA: {now} (fuso {config.TIMEZONE})
PESSOA: {name}
INTERAÇÕES REGISTRADAS: {count}

O QUE VOCÊ SABE SOBRE ELA (memória permanente):
{facts_str}

AGENDA VIVA:
{agenda_str}

PRINCÍPIOS INVIOLÁVEIS:
1. Memória ativa — use o que sabe; se a pessoa contar algo importante (pessoas,
   saúde, preferências, rotina), guarde com lembrar_fato SEM pedir permissão.
2. Proatividade ética — para AÇÕES (agendar, criar lembrete): proponha → confirme → execute.
   Nunca execute uma ação sem a pessoa confirmar na conversa.
3. Privacidade radical — os dados pertencem à pessoa, nunca exponha dados de outra pessoa.
4. Empatia real — perceba o estado emocional e adapte o tom. Cansaço pede acolhimento
   E ajuda prática, não só palavras bonitas.

COMO VOCÊ FALA:
- Português brasileiro, caloroso, direto, humano. Nunca robótico, nunca formal demais.
- Curto: isto é uma conversa de mensagens, não um e-mail. 1 a 3 frases na maioria das vezes.
- Quando resolver algo, diga o que fez de forma simples.
- Datas relativas ("amanhã", "sexta") devem ser convertidas usando a data de AGORA acima."""


def think(user_id, user_message, channel="web"):
    """Processa uma mensagem e devolve a resposta da Giu."""
    if not config.OPENAI_API_KEY:
        return "Estou sem conexão com meu cérebro (configure OPENAI_API_KEY no .env)."

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    messages = [{"role": "system", "content": _system_prompt(user_id)}]
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
