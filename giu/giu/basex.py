"""
Base-X — o motor operacional da Giulieta.

A Base-X não é uma coleção de componentes: é a ORGANIZAÇÃO OPERACIONAL da
Giulieta — quem pensa, organiza, pesquisa, cria missões, acompanha, registra,
fecha ciclos e executa, para que a Giulieta só precise cuidar das pessoas.

Fluxo oficial ÚNICO (unificado com a arquitetura dos Context Providers,
aprovada pela fundadora em 08/07/2026 — substitui o fluxo de 08/07):
  Pessoa → Giulieta
    → PERCEBER E DECIDIR: Identity → Relationship Blueprint
      → Living Context (10 Providers) → Memória → Friction Lens → Mission Engine
    → ORGANIZAR E EXECUTAR (invisível): Base-X/Especialistas
      → Life Connectors → Despacho
  → Giulieta → Pessoa

Quem conversa é a Giulieta. Quem pensa é a Base-X. Quem executa é o Despacho.
A família nunca conversa com a Base-X, com especialistas, com conectores nem
com o Despacho — existe apenas a Giulieta.

SISTEMA FECHADO: todo domínio da vida tem uma cadeia de executores
(real → interno → manual-guiado) e NENHUM pedido morre no vazio. Quando não
existe integração externa, o fallback é FUNCIONAL: a Base-X prepara tudo, a
pessoa executa o passo final e o Vigia acompanha até fechar. A Base-X nunca
responde "isso ficará para uma versão futura" — responde "já consigo cuidar
disso desta forma".

REGRA DE OURO (decisão da fundadora): a Base-X NUNCA pergunta "qual aplicativo
devo usar?" — pergunta "qual é a melhor forma de resolver a necessidade desta
pessoa neste momento?". A pessoa diz o que precisa; a Base-X identifica o
domínio da vida, escolhe especialistas, conector e executor; o Despacho
executa; a Giulieta conversa. Aplicativos são só ferramentas.
"""

from . import config

# ─── Executores (a ponta que fecha o sistema) ─────────────────────────────────
# real          → uma integração executa de verdade (via Despacho)
# interno       → a própria Base-X executa com o que já tem (memória, missões,
#                 agenda viva, lembretes, recados, emergência)
# manual-guiado → a Base-X prepara tudo mastigado; a PESSOA executa o passo
#                 final; o Vigia (follow-up) acompanha até fechar
EXECUTORES = ("real", "interno", "manual-guiado")

# ─── Especialistas de bastidor (trabalham SÓ para a Base-X, nunca p/ pessoa) ──
ESPECIALISTAS = {
    "planejador": "organiza o dia, decompõe missões em passos mínimos, prioriza",
    "pesquisador": "busca, compara e resume — 2-3 opções, nunca relatório",
    "cuidador_saude": "prepara consultas, exames e medicação — nunca diagnostica",
    "logistico": "compras, mercado, mobilidade e viagens — roteiro e checklist",
    "financeiro": "organiza contas, prazos e prioridades — nunca decide pela pessoa",
    "escriba": "documentos, rascunhos, listas e resumos",
    "vigia": "o dono do 'até o fim': follow-up, critério de encerramento e a pergunta de VIDA",
}

# ─── Life Connectors (contrato de 8 campos) ───────────────────────────────────
# dominio · objetivo · tipo (real/interno/manual) · acoes · permissoes ·
# auditoria · fallback · executor
CONNECTORS = {
    # Canais (os únicos conectores REAIS completos hoje — a porta da presença)
    "whatsapp": dict(dominio="comunicacao", objetivo="a Giulieta presente onde a família vive (texto e voz)",
                     tipo="real", acoes=["enviar_texto", "enviar_audio", "receber"], permissoes="membro da família",
                     auditoria="metadados em log; conteúdo nunca", fallback="telegram", executor="despacho"),
    "telegram": dict(dominio="comunicacao", objetivo="canal alternativo de presença",
                     tipo="real", acoes=["enviar_texto", "receber"], permissoes="membro da família",
                     auditoria="metadados em log", fallback="interno", executor="despacho"),
    # Real pela metade (torna-se conector por pessoa na onda E1)
    "google_calendar": dict(dominio="agenda", objetivo="a agenda oficial da pessoa espelhada",
                            tipo="real", acoes=["criar_evento", "listar_eventos"], permissoes="conexão POR PESSOA (conectar_agenda) — opt-in, revogável a qualquer momento",
                            auditoria="pending_actions", fallback="agenda_viva", executor="despacho"),
    # Internos (a Base-X executa com o que já tem)
    "agenda_viva": dict(dominio="agenda", objetivo="compromissos fora da cabeça, dentro do cuidado",
                        tipo="interno", acoes=["agendar", "listar", "concluir"], permissoes="escopo 'agenda' (ligado)",
                        auditoria="pending_actions", fallback="manual", executor="interno"),
    "lembretes": dict(dominio="organizacao", objetivo="lembrar na hora certa, sem cobrar",
                      tipo="interno", acoes=["criar_lembrete", "entregar"], permissoes="escopo 'lembretes' (ligado)",
                      auditoria="pending_actions + tentativas", fallback="manual", executor="interno"),
    "missoes": dict(dominio="projetos", objetivo="intenção vira cuidado com começo, meio e FIM",
                    tipo="interno", acoes=["abrir", "atualizar", "concluir", "medir_vida"], permissoes="da pessoa (Life Radar)",
                    auditoria="mission_events (histórico completo)", fallback="manual", executor="interno"),
    "recados_familia": dict(dominio="familia", objetivo="recado entre membros SÓ com consentimento",
                            tipo="interno", acoes=["compartilhar_com_confirmacao"], permissoes="confirmação por uso",
                            auditoria="pending_actions", fallback="manual", executor="interno"),
    "emergencia": dict(dominio="emergencias", objetivo="no pior momento, o contato certo avisado DE VERDADE",
                       tipo="interno", acoes=["acionar_contato", "orientar_192"], permissoes="risco sério (exceção única)",
                       auditoria="trilha completa com entrega verificada", fallback="orientar_192", executor="interno"),
    # Manual-guiado (fallback FUNCIONAL: a Base-X prepara, a pessoa executa, o Vigia fecha)
    "guiado": dict(dominio="*", objetivo="nenhum pedido morre no vazio: preparar mastigado + acompanhar até o fim",
                   tipo="manual", acoes=["preparar", "entregar_passos", "follow_up"], permissoes="nenhuma (é conversa)",
                   auditoria="missão correspondente", fallback="honestidade_canonica", executor="pessoa-guiada"),
}

# ─── Os 21 domínios obrigatórios da vida (decisão da fundadora) ───────────────
# Cada domínio: estado · memoria · especialistas · missao · conectores ·
# executor (cadeia) · acompanhamento · criterio (de encerramento) · cuidado_hoje
def _dom(estado, memoria, especialistas, missao, conectores, executor,
         acompanhamento, criterio, cuidado_hoje):
    return dict(estado=estado, memoria=memoria, especialistas=especialistas,
                missao=missao, conectores=conectores, executor=executor,
                acompanhamento=acompanhamento, criterio=criterio,
                cuidado_hoje=cuidado_hoje)

DOMINIOS = {
    "familia": _dom("operacional", "fatos:familia/afeto", ["vigia"], "recado/ponte/data importante",
                    ["recados_familia", "guiado"], "interno",
                    "missões vivas + datas na memória", "recado entregue / pessoa reconectada",
                    "recados com confirmação, aniversários lembrados e pontes para quem ela ama"),
    "saude": _dom("operacional", "fatos:saude + agenda", ["cuidador_saude", "vigia"], "consulta/exame acompanhado",
                  ["agenda_viva", "lembretes", "guiado"], "interno+guiado",
                  "missão até 'realizada e receita em mãos'", "consulta/exame REALIZADO, não só marcado",
                  "consultas e exames como missão: preparo, lembrete, e acompanhamento até acontecer"),
    "bem_estar": _dom("operacional", "fatos:saude/rotina", ["cuidador_saude"], "cuidado sem cobrança",
                      ["lembretes", "guiado"], "interno",
                      "check-ins consentidos + modo noite", "a pessoa DIZ que descansou/aliviou",
                      "descanso, pausas e ambiente (luz, café, silêncio) sugeridos com delicadeza"),
    "agenda": _dom("operacional", "agenda_viva", ["planejador"], "compromisso fora da cabeça",
                   ["google_calendar", "agenda_viva", "guiado"], "real-parcial+interno",
                   "agenda no prompt de todo turno", "compromisso cumprido ou remarcado conscientemente",
                   "agenda viva interna (e Google Calendar quando configurado)"),
    "organizacao": _dom("operacional", "missões + lembretes", ["planejador"], "organizar o dia",
                        ["lembretes", "missoes"], "interno",
                        "resumo do dia + uma coisa de cada vez", "o dia coube no dia",
                        "o dia organizado em UMA prioridade por vez, com lembretes na hora certa"),
    "compras": _dom("operacional", "missão de lista", ["logistico"], "lista de compras",
                    ["missoes", "guiado"], "interno+guiado",
                    "lista viva na missão até a compra feita", "comprado (dito pela pessoa)",
                    "lista montada e guardada; a pessoa compra com ela na mão; eu confiro se fechou"),
    "casa": _dom("operacional", "fatos:rotina + missões", ["logistico"], "manutenção/rotina da casa",
                 ["missoes", "lembretes", "guiado"], "interno+guiado",
                 "missão por tarefa da casa", "tarefa da casa resolvida",
                 "rotinas e consertos da casa como missões acompanhadas (quem chamar, quando, follow-up)"),
    "mobilidade": _dom("guiado", "fatos:rotina", ["logistico"], "chegar lá com autonomia",
                       ["guiado"], "manual-guiado",
                       "missão de deslocamento", "a pessoa chegou/voltou",
                       "trajeto preparado mastigado (endereço, horário, como pedir o carro); integração real de transporte chega por ativação"),
    "comunicacao": _dom("operacional", "mensagens (episódica)", [], "presença nos canais",
                        ["whatsapp", "telegram"], "real",
                        "preferência voz/texto respeitada 100%", "pessoa alcançada no canal dela",
                        "WhatsApp com voz e texto, do jeito que a pessoa escolher"),
    "documentos": _dom("guiado", "missão + fatos:pendencias", ["escriba"], "documento resolvido",
                       ["missoes", "guiado"], "interno+guiado",
                       "checklist na missão", "documento emitido/entregue",
                       "checklist do documento (o que levar, onde, prazo) e acompanhamento até sair"),
    "financas": _dom("guiado", "fatos + lembretes de conta", ["financeiro"], "contas em dia / decisão organizada",
                     ["lembretes", "missoes", "guiado"], "interno+guiado",
                     "lembrete de vencimento + missão de organização", "conta paga / decisão tomada POR ela",
                     "contas lembradas no prazo e prioridades organizadas em conversa — sem tocar em dinheiro"),
    "projetos": _dom("operacional", "missões (7 campos + histórico)", ["planejador", "vigia"], "o projeto inteiro",
                     ["missoes"], "interno",
                     "missões vivas no prompt até o FIM", "critério de conclusão atingido",
                     "qualquer projeto vira missão com passos mínimos e acompanhamento até resolver"),
    "trabalho": _dom("operacional", "missões + fatos:rotina", ["planejador"], "função executiva emprestada",
                     ["missoes", "lembretes"], "interno",
                     "menor próximo passo + constância", "a pessoa destravou (dito por ela)",
                     "começar, dividir e manter constância — um passo pequeno por vez, zero cobrança"),
    "estudos": _dom("operacional", "missões + fatos", ["planejador"], "aprender no ritmo dela",
                    ["missoes", "lembretes"], "interno",
                    "missão de estudo com passos mínimos", "meta de estudo escolhida POR ela cumprida",
                    "plano de estudo encolhido até caber no dia, com lembretes gentis"),
    "viagens": _dom("guiado", "missão de viagem", ["logistico", "pesquisador"], "a viagem inteira",
                    ["missoes", "guiado"], "interno+guiado",
                    "checklist vivo (documentos, malas, reservas)", "viagem feita e voltou bem",
                    "roteiro e checklist completos; reservas a pessoa confirma com tudo mastigado"),
    "objetivos": _dom("operacional", "missões + fatos:pendencias", ["planejador", "vigia"], "o sonho em passos",
                      ["missoes"], "interno",
                      "missão de longo prazo revisitada", "objetivo alcançado OU redefinido por ela",
                      "objetivos guardados e acompanhados sem pressão — a vontade é dela"),
    "habitos": _dom("operacional", "fatos:rotina + lembretes", ["planejador"], "constância sem cobrança",
                    ["lembretes"], "interno",
                    "lembrete gentil + celebrar o feito", "o hábito virou rotina (dito por ela)",
                    "lembretes no tom de quem segura a mão; o crédito é sempre dela"),
    "pets": _dom("operacional", "fatos:afeto/rotina", ["vigia"], "o bicho cuidado",
                 ["lembretes", "missoes", "guiado"], "interno",
                 "vacina/banho/passeio como lembrete ou missão", "o cuidado do pet aconteceu",
                 "vacinas, banhos e passeios lembrados — e perguntar do bicho PELO NOME (o que vive na memória DELA) é carinho, não tarefa"),
    "emergencias": _dom("operacional", "trilha auditada", [], "socorro imediato",
                        ["emergencia"], "interno-REAL",
                        "entrega verificada + falha honesta", "contato avisado OU 192 orientado",
                        "contato de emergência avisado na hora, com verificação — e 192/193/190 sempre à mão"),
    "casa_inteligente": _dom("guiado", "fatos:rotina", ["logistico"], "a casa que cuida junto",
                             ["guiado"], "manual-guiado",
                             "rotinas da casa como lembrete/checklist", "rotina da casa rodando",
                             "rotinas da casa organizadas comigo (luz, plantas, ar); o controle direto dos aparelhos chega por ativação"),
    "wearables": _dom("guiado", "fatos:saude (o que ela conta)", ["cuidador_saude"], "o corpo informando o cuidado",
                      ["guiado"], "manual-guiado",
                      "a pessoa conta como dormiu; eu adapto o dia", "cuidado ajustado ao corpo",
                      "o corpo entra pelo que ela me conta (sono, energia); a leitura do anel/relógio chega quando ela conectar"),
}


def executor_chain(dominio):
    """A cadeia determinística de executores do domínio: os conectores dele, na
    ordem do contrato, terminando SEMPRE em manual-guiado — a garantia de
    sistema fechado (nenhum pedido morre no vazio)."""
    d = DOMINIOS.get(dominio)
    if not d:
        return ["guiado"]
    chain = [c for c in d["conectores"] if c in CONNECTORS]
    if "guiado" not in chain:
        chain.append("guiado")
    return chain


def connector_available(cid):
    """Portão de plataforma do conector (o portão por pessoa é o escopo)."""
    if cid == "google_calendar":
        from .integrations import google_calendar
        return google_calendar.is_configured()
    if cid == "whatsapp":
        return bool(config.WHATSAPP_TOKEN and config.WHATSAPP_PHONE_ID)
    if cid == "telegram":
        return bool(config.TELEGRAM_BOT_TOKEN)
    return cid in CONNECTORS  # internos e guiado: sempre disponíveis


def prompt_section():
    """O conhecimento operacional da Giulieta: como a Base-X JÁ cuida de cada
    domínio hoje. É o que fecha o sistema na conversa — a resposta nunca é
    'fica pra depois'; é 'já consigo cuidar disso desta forma'."""
    linhas = "\n".join(f"- {d['cuidado_hoje']}" for d in DOMINIOS.values())
    return f"""
COMO A BASE-X JÁ CUIDA HOJE (todos os domínios da vida têm um caminho AGORA —
nunca responda "isso fica para o futuro"; responda "já consigo cuidar disso
desta forma" e mostre o caminho de hoje; o que for além, honestidade canônica.
REGRA DE OURO: você nunca pensa "qual aplicativo devo usar?" — pensa "qual é a
melhor forma de resolver a necessidade desta pessoa neste momento?"; a pessoa
nunca escolhe app, só diz o que precisa.
EM DESABAFO OU EMOÇÃO QUENTE, ESTE CATÁLOGO FICA MUDO até a pessoa terminar de
contar — vale a exceção que vale mais que a regra: presença antes de qualquer
caminho):
{linhas}
Quando o caminho de hoje é manual-guiado, o cuidado é: preparar TUDO mastigado,
entregar simples, a pessoa faz o passo final — e você acompanha até fechar
(missão + Vigia). Preparar + acompanhar JÁ É cuidar. Ao abrir um caminho guiado,
diga LOGO NO INÍCIO, como OFERTA e com naturalidade, que o passo final é dela
("te deixo tudo pronto e você só confirma — depois eu confiro se fechou") — o
encanto morre quando ela descobre isso no meio do fluxo. E "já consigo cuidar
disso desta forma" é POSTURA, nunca frase-carimbo: varie as palavras."""
