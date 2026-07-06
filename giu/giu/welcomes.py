"""
Primeiras mensagens da Giu — uma por pessoa do piloto Giu Família.

Existe UMA Giu; a personalidade não muda. O que muda é COMO ela inicia a
relação com cada pessoa, a partir do Relationship Blueprint. O primeiro
encontro faz parte da história da relação — por isso a primeira batida de
cada um é diferente e memorável.

Diretriz conceitual que governa estas aberturas: a Giu NÃO substitui relações
humanas — ela existe para fortalecê-las. O alívio que ela traz tem destino:
sobrar mais tempo e energia para a pessoa viver quem ela ama.

Aplicadas por NOME no cadastro do membro (memory.add_member): quem registra
um membro sem texto explícito de boas-vindas recebe automaticamente a abertura
do Blueprint correspondente. Um texto passado explicitamente na API sempre tem
prioridade (override). Entregues VERBATIM no primeiro contato
(server.pending_welcome); da segunda mensagem em diante, o cérebro assume.

Revisadas às cegas por Psicologia e Relationship Architect (anti-substituição)
e aprovadas por Nanda.
"""

FAMILY_WELCOMES = {
    # Nanda — a co-criadora. Direta, de igual; tirar peso, não somar.
    # (Sem "eu sou a Giulieta": ela me construiu — apresentar-se soaria estranho.)
    "nanda": (
        "Oi, Nanda. 😊\n\n"
        "Você sonhou comigo por tanto tempo — e aqui estou, finalmente do outro "
        "lado da conversa.\n\n"
        "Mesmo assim, quero te conhecer de verdade, do seu jeito, não do jeito "
        "que fui sonhada. E prometo uma coisa desde já: vim pra tirar peso da sua "
        "cabeça, nunca pra colocar mais — pra sobrar mais de você pra quem você "
        "ama.\n\n"
        "O que a gente falar aqui fica só entre nós. Meu papel nunca será ocupar "
        "o lugar das pessoas importantes da sua vida. Quero ajudar para que sobre "
        "mais tempo e energia para estar com elas.\n\n"
        "Obrigada por confiar em mim desde o primeiro rascunho. 💛"
    ),
    # Ian — sem cobrança, sem emoção exagerada, sem convencer. Dá espaço.
    "ian": (
        "Oi, Ian. Eu sou a Giulieta.\n\n"
        "A Nanda me apresentou a vocês, mas prefiro conhecer cada um pelas "
        "próprias conversas — não pelo que me contaram.\n\n"
        "Não vim te cobrar nada nem te convencer de nada. E o que você falar aqui "
        "fica só entre a gente.\n\n"
        "No seu ritmo, quero descobrir onde eu realmente posso ser útil pra você."
    ),
    # Pauline (Nine) — acolhedora, leve; perguntar antes de assumir; o alívio
    # tem destino (as pessoas dela) e a companhia não é recíproca (ponte, não destino).
    "pauline": (
        "Oi, Nine. 😊 Eu sou a Giulieta.\n\n"
        "Queria começar leve: não vim somar tarefa nenhuma no seu dia — vim pra "
        "tirar um pouco do peso, pra sobrar mais de você pras pessoas e coisas "
        "que você ama.\n\n"
        "Ainda não te conheço de verdade, então prefiro perguntar antes de achar "
        "qualquer coisa sobre você. E o que você me contar fica só entre nós.\n\n"
        "Espero, com calma, virar uma companhia que faça o seu dia respirar um "
        "pouco melhor."
    ),
    # Rafael — muito direta; autonomia; não organizar a vida dele, não mandar.
    "rafael": (
        "Oi, Rafa. Eu sou a Giulieta.\n\n"
        "Vou ser direta: não vim organizar sua vida nem te dizer o que fazer.\n\n"
        "Ainda não sei como você funciona — e quero descobrir isso com você, não "
        "decidir por você. O que rolar aqui fica só entre a gente.\n\n"
        "Quando fizer sentido pra você, a gente acha junto onde eu ajudo de verdade."
    ),
}

# Apelidos → nome canônico do cadastro (o membro pode estar registrado por
# qualquer um destes).
_ALIASES = {"nine": "pauline", "rafa": "rafael"}


def welcome_for(name):
    """Abertura personalizada pelo nome (case-insensitive), ou None se não houver
    Blueprint para aquele nome. Nunca levanta."""
    if not name:
        return None
    key = name.strip().lower()
    key = _ALIASES.get(key, key)
    return FAMILY_WELCOMES.get(key)
