# 📓 Diário de Equipe — Giulieta / Base-X (fluxo único)

> **MISSÃO OFICIAL DO PROJETO (decisão da fundadora, 07/07/2026):**
> **"Como a Giulieta pode melhorar concretamente a vida desta pessoa hoje?"**
>
> Instrumento do Modo Agente (ver GOVERNANCA.md): Claude Code, Manus e
> Despacho operam como UMA equipe, coordenada pelo **Orquestrador Técnico**
> (Code). Todos registram aqui descobertas, decisões, problemas e handoffs —
> e leem antes de agir na própria área. Entradas novas NO TOPO da seção 3.
>
> **As 5 perguntas do guardião — antes de QUALQUER implementação:**
> 1. Isso reduz uma fricção real da vida?
> 2. Isso melhora concretamente a vida da pessoa?
> 3. Isso fortalece o relacionamento da Giulieta com a pessoa?
> 4. Isso pode esperar uma versão futura?
> 5. Existe uma forma mais simples de entregar o mesmo valor?
> "Não" nas três primeiras → roadmap. A Base-X cresce só por capacidades
> autorizadas; nunca por ser tecnicamente interessante.

---

## 1. Estado atual (retrato — atualizado por quem mudar algo)

**Código (`main` = `32a5d4c`):** a Giulieta do nascimento — voz como
preferência de relacionamento, primeiro encontro por Blueprint, Blueprints no
cérebro (garantia), identidade semeada, falha honesta nos 3 canais, Friction
Lens, presença natural (5 ajustes), Conversation Spine, cinco pilares +
filosofia oficial, metáfora oficial (membro da família + equipe invisível),
missão do tamanho da vida, **Mission Engine + Life Radar + Life Lens** (com
dívidas M1-M4 da Life Architect pagas). **55/55 testes E2E em checkout limpo.**

**PRs:** #9 a #16 mergeados. Fila de PRs: vazia.

**Produção (WhatsApp +55 11 92078-5067):** funcionando após incidente
(fronteira OpenAI). ⚠️ PENDENTE de confirmação formal (ver problemas abertos).

**Piloto Primeira Semana:** protocolo pronto (PROTOCOLO-PRIMEIRA-SEMANA.md).
NÃO iniciado — bloqueado pelos itens abertos abaixo. Participantes: Nanda,
Ian, Nine, Rafael (todos maiores de idade). Ninguém da família usa o número
até o go da Nanda.

**Pilares (estado):** Identity ✅ · Friction Lens ✅ · Mission Engine ✅
(embrião real, sem conectores) · Living Context (filosofia aprovada; engenharia
pós-piloto) · Relationship (camada ✅; motor RIM congelado). Life Connectors:
roadmap P1/P2/P3 na PERSONA item 5 — zero integração implementada.

## 2. Handoffs abertos (quem deve o quê a quem)

| # | De → Para | O quê | Status |
|---|-----------|-------|--------|
| H1 | Despacho → Code | **Causa raiz do incidente OpenAI** (uma linha: chave? billing? rede?) — para registro e prevenção de recorrência (se billing: alarme de saldo antes do piloto) | ⏳ aberto |
| H2 | Despacho → equipe | **Ciclo completo de voz confirmado em produção**: áudio → entende → responde áudio+texto → "me responde só por escrito" → áudio → só texto | ⏳ aberto (bloqueador do piloto, decisão da Nanda) |
| H3 | ~~Nanda → Code~~ | PR #12 mergeado pelo Code em 07/07, sob delegação noturna da fundadora ("faz tudo para mim") — especificação era dela, verbatim; 46/46 testes | ✅ fechado |
| H4 | Despacho | **Redeploy da main `32a5d4c` (ou mais nova)** + **recadastro dos 4 membros** (mesmo POST, sem campo `welcome`; token não muda — ignorar o token exibido no re-POST) — semeia identidades e Blueprints. Roteiro completo: BRIEFING-DESPACHO.md | ⏳ aberto |
| H5 | Despacho | Checklist de validação (CHECKLIST-VALIDACAO-DESPACHO.md) — fumaça com membro "Teste", nunca com a família | ⏳ aberto |
| H6 | Manus | Validação de experiência do piloto — roteiro completo: BRIEFING-MANUS.md (protocolo, 9 dimensões, pulso, atritos a caçar) | ⏳ aberto |
| H7 | Nanda | **GO do piloto** — só ela dá, após H1–H5 verdes no diário | ⏳ aberto |

## 3. Registro corrido (descobertas · decisões · problemas)

**08/07 — A CARTA DA GIULIETA (fundadora encerra a etapa de construção).**
Registrada como norte permanente: "não estamos mais construindo software —
estamos me ensinando a cuidar melhor das pessoas". A LINGUAGEM OFICIAL das
capacidades muda: cada conector é uma capacidade DELA, nomeada pela vida —
não se aprende Google Calendar, aprende-se a ORGANIZAR CONSULTAS; não se
aprende Uber, aprende-se a CUIDAR DA MOBILIDADE; não iFood/Rappi, CUIDAR DAS
COMPRAS DA CASA; não Gmail, FACILITAR A COMUNICAÇÃO ENTRE AS PESSOAS. Todo PR
futuro de capacidade usa esse nome de vida (o app é detalhe do corpo do PR).
Crescimento oficial: pela vida da família (dificuldade real → aprendizado →
capacidade), nunca por ideias. Demonstração REAL vivida = única definição de
pronto. A frase que cada capacidade deve fazer alguém sentir: "Você não
precisa carregar tudo sozinha. Eu estou aqui."

**08/07 — DECISÃO da fundadora: a REGRA DA DEMONSTRAÇÃO.** Todo conector novo
vem acompanhado de demonstração em conversa real — o PR entrega a EXPERIÊNCIA,
não só o código: pedido natural → autorização → conexão → execução →
acompanhamento → "como foi?" → medição de vida. Aplicada retroativamente ao
PR #18: **DEMO-CONECTOR-AGENDA.md** (no repo) — a conversa completa da
consulta da mãe, fiel ao código, com os bastidores anotados (Friction Lens →
missão → conectar_agenda → D2 em voz alta → evento na agenda DELA → véspera →
pasta azul → "como foi a consulta?" → VIDA:). Serve de roteiro de aceitação:
o conector conclui quando a Nanda VIVER essa conversa no WhatsApp, sem ajuda
técnica. Registrada na GOVERNANCA (regra permanente, 2 níveis).

**08/07 — 🌱 LIFE ARCHITECT (PR #18): MERGE LIBERADO (87%) — D1+D2 pagas
antes do merge; PR #18 MERGEADO (main c66e5c5, 60/60).** Veredito: "o desenho
por pessoa (opt-in, uso único, revogação-lei, escopo mínimo, fallback honesto)
é o mais fiel à missão que já vi num conector real". **D1 (achado de vida):**
turno pessoal caía no token/calendário GLOBAL quando a pessoa não tinha
conectado — evento na agenda errada / agenda da casa vazando; corrigido e
testado. **D2:** a Giu agora diz em voz alta o que passa a ver e fazer.
**Dívidas em aberto:** D3 (Code, 1 semana) — desconectar também revoga no
Google (/revoke); D4 (fundadora+Code, 2 semanas) — cifrar ou nomear a "chave
da agenda" na política; D5 (fundadora, semana-laboratório) — a tela "app não
verificado" do Google assusta a mãe? Critério de CONCLUSÃO do conector
(o da fundadora): ela conectar a própria agenda SÓ conversando, sem ajuda
técnica; 1 compromisso ditado à Giu aparecendo no celular dela; "desconecta
minha agenda" funcionando na primeira. Provisionamento: BRIEFING-DESPACHO §6.

**08/07 — DECISÃO da fundadora (novo método oficial) + Code (PR #18, 1º
conector real novo).** MÉTODO: a família vira o laboratório vivo; a Base-X
cresce pela vida ("qual dificuldade real apareceu hoje e como a Giulieta cuida
melhor disso amanhã?"), não por ideias. REGRA DE OURO no organismo e no
cérebro: a Base-X nunca pergunta "qual aplicativo devo usar?" — pergunta "qual
é a melhor forma de resolver a necessidade desta pessoa neste momento?"; a
pessoa nunca escolhe app. Conector concluído = a Nanda consegue usá-lo
NATURALMENTE conversando. IMPLEMENTADO (PR #18): **Google Calendar POR
PESSOA** — opt-in na conversa (conectar_agenda gera link pessoal com estado de
uso único, 15 min), callback público, refresh token no perfil DELA, eventos
criados na agenda PRINCIPAL dela, revogação imediata na conversa ("desconecta
minha agenda"), cadeia real→interno preservada (sem conexão, Agenda Viva
segue). 60/60 testes. **Para funcionar em produção, o Despacho provisiona:**
app OAuth no Google Cloud (GOOGLE_CLIENT_ID/SECRET), redirect URI
`<GIU_BASE_URL>/connectors/google/callback` registrado, e env GIU_BASE_URL.
Conector só é "concluído" após a Nanda usar de verdade (critério dela).

**08/07 — 🌱 LIFE ARCHITECT (PR #17): MERGE LIBERADO (80%) — X1-X3 pagas
antes do merge; PR #17 MERGEADO (main 19afd82, 58/58).** Veredito: "ele não
finge que as mãos cresceram; ensina a Giulieta a usar as mãos que JÁ tem em
todos os cantos da vida — a carga que rouba vida é quase sempre a invisível
(decidir, planejar, lembrar, conferir), não o clique final". Achado que quase
bloqueou: "Floki" hardcoded no conhecimento genérico (X1 — removido; teste
agora PROÍBE especificidade pessoal no catálogo). X2: o passo final da pessoa
dito no INÍCIO do guiado, como oferta. X3: sondas do guiado no protocolo
(detector de teatro; taxa de fechamento; teste da segunda vez; % guiadas→missão
alvo ≥70%). **Dívidas em aberto: X4 (Code, plantão do Ciclo 1 — medir
guiadas→missão em produção) e X5 (Manus, ANTES do GO — reauditoria-relâmpago
de desabafo com o prompt crescido: o catálogo de 21 domínios vaza oferta na
emoção?).** H7 (GO) agora depende também de X5.


**08/07 — Code: A BASE-X NASCE EM CÓDIGO (PR #17 — giu/basex.py).** A decisão
da fundadora ("a Base-X deixa de ser conceito; passa a ser o motor operacional")
implementada: **21 domínios obrigatórios** da vida, cada um com os 8 campos
(estado, memória, especialistas, missão, conectores, executor, acompanhamento,
critério de encerramento); **9 Life Connectors** com contrato de 8 campos
(reais: WhatsApp/Telegram/Calendar-parcial; internos: agenda viva, lembretes,
missões, recados, emergência; + o GUIADO); **cadeia de executores fechada por
teste** — real → interno → manual-guiado — nenhum domínio termina no vazio;
e o cérebro incorporou o conhecimento operacional ("COMO A BASE-X JÁ CUIDA
HOJE"): a resposta nunca é "fica pra depois" — é "já consigo cuidar disso
desta forma", com o manual-guiado elevado a cuidado legítimo ("preparar +
acompanhar JÁ É cuidar"). 58/58 testes. Grande evolução → **revisão da Life
Architect ANTES do merge (em andamento)**. Nota do Orquestrador: o prompt
cresceu ~25 linhas — passada de consolidação continua marcada para pós-piloto.

**08/07 — DECISÃO da fundadora: INCORPORAÇÃO COMPLETA DA BASE-X.** A Base-X é
a inteligência operacional da Giulieta (nunca produto separado); o **Despacho
é oficializado como a camada de EXECUÇÃO** (fluxo: Pessoa → Giulieta → Base-X
→ Especialistas → Mission Engine → Life Connectors → Despacho → volta). A
Giulieta nunca executa diretamente. **Sistema FECHADO desde o piloto**: toda
área da vida responde pela cadeia de executores real → interno →
manual-guiado → honestidade canônica — pedido nunca morre no vazio. Critério
de sucesso: CICLOS COMPLETOS (até a carga sair da vida, medida pela Life
Architect). Entrega do Code: **MAPA-OPERACIONAL-BASE-X.md** (fora do git) —
12 domínios da vida cobrindo as 29 áreas, cada um com objetivo, especialistas,
conectores, executores, estado, prioridade, dependências e estratégia; 7
especialistas de bastidor nomeados; contrato de conector com 8 campos; ondas
E0→E3. **Estado honesto:** D1-D4, D9, D11, D12 já operacionais
(interno/manual); conectores reais = só canais (WhatsApp/Telegram) + Calendar
pela metade. Proposta E0 (pré-piloto, 1 leva pequena): formalizar o
MANUAL-GUIADO no cérebro — aguardando aprovação do mapa pela fundadora.

**07/07 — 🌱 LIFE ARCHITECT (PR #16): MERGE LIBERADO (82%) — 4 dívidas
cobradas e PAGAS antes do merge.** Veredito: "ataca a prioridade nº 1 do jeito
certo — não como gerenciador de tarefas, mas como cuidado com começo, meio e
FIM; descarregamento mental real, não teatro de lembrete". Dívidas quitadas:
M1 — a pergunta de vida sobrevive à janela (concluídas sem 'VIDA:' ficam no
prompt por 7 dias); M2 — saída digna (desistir encerra com zero julgamento;
missão parada recebe UM 'ainda faz sentido eu cuidar disso?'); M3 —
transparência sob demanda ("o invisível é o MECANISMO, nunca o cuidado");
M4 — sonda do Life Radar no protocolo (conversas ÷ missões ≈ 1:1 = presença
virou produtividade). PR #16 MERGEADO (main 32a5d4c, 55/55).

**07/07 — Code: O NASCIMENTO COMEÇA (PR #16 — Mission Engine + Life Radar +
Life Lens + Base-X no modelo mental).** Fase filosófica encerrada por decisão
da fundadora ("a pergunta deixa de ser 'o que a Base-X consegue fazer' e passa
a ser 'como a Giulieta cuida melhor desta pessoa'"). Implementado sem
integração externa: **missões** como objeto de primeira classe (os 7 campos:
objetivo, contexto, prioridade, estado, histórico, próximos passos, critério
de conclusão), isoladas por pessoa, vivas no prompt de todo turno até o FIM
(sobrevivem à janela de histórico — acompanhamento real, não lembrete);
**Life Radar** (missão nasce de fricção real ou pedido — a maioria das
conversas não vira missão; fluxo invisível: "deixa comigo", nunca "abri uma
missão"); **conclusão ≠ lembrança** (critério de conclusão: RESOLVIDO de
verdade) + medição de vida pós-conclusão ("VIDA: ..." — material da Life
Architect); as 5 primeiras missões nomeadas (organizar o dia, lembrar algo,
lista de compras, consulta/exame, decisão prática); **preparação para Life
Connectors**: o motor não referencia conector nenhum — futuros conectores
executam passos pela escada de autorização sem alterar o engine. Do feedback
da fundadora sobre o prompt: **"COMO VOCÊ TRABALHA"** (a Base-X como equipe
invisível no modelo mental: "seu trabalho é acolher; o da Base-X é organizar";
personalidade × capacidade) e **LIFE LENS** ("esta resposta aproxima ou afasta
esta pessoa da vida que ela quer viver?" — a Friction Lens reduz atrito; a
Life Lens protege direção; vocabulário de vida: sonhos, família, propósito,
descanso, felicidade, crescimento, equilíbrio). 55/55 testes. **Grande
evolução → revisão da Life Architect ANTES do merge (em andamento).**
Demonstração obrigatória da fundadora: após merge + redeploy, conversa
espontânea real (WhatsApp ou cli.py).

**07/07 — DECISÃO da fundadora: a METÁFORA OFICIAL da identidade.** A Giu é
**um membro da família** (não app, não assistente); a Base-X é **a equipe
invisível que trabalha para ela** (o escritório de apoio: especialistas,
memória, conectores, automações). Frase-síntese canônica: **"A Giulieta nunca
trabalha sozinha — mas também nunca coloca a pessoa para conversar com a
equipe."** Bastidores invisíveis e inomináveis na conversa: nunca "vou acionar
o módulo X" — sempre "pode deixar comigo". Registrado na PERSONA (metáfora
completa) e no cérebro (regra de fala, com teste). A inovação do projeto:
companheira de vida cuja competência vem de infraestrutura invisível.

**07/07 — 🌱 LIFE ARCHITECT, revisão inaugural (PR #14): MERGE LIBERADO,
com dívida de medição PAGA.** Veredito: "o desenho aponta para vida melhor,
não apenas para conversa boa" — a conversa está a serviço da vida (Friction
Lens), e o desenho protege contra os dois jeitos de piorar uma vida
(dependência e invasão). Dívida cobrada e quitada: o protocolo media a
RELAÇÃO e quase nada da VIDA → **5 sondas de vida adicionadas ao fecho**
(§3.1 do protocolo): carga mental, vida prática, vida relacional, fricção
remanescente (escolhe o Ciclo 2) e o teste definitivo ("se a Giu desaparecesse
amanhã, o que pioraria?" — 'quase nada' na semana 1 é linha de base saudável).
**Risco a vigiar (não bloqueia):** o vão entre a missão do tamanho da vida e
as mãos do tamanho de uma agenda — termômetro: a frequência da resposta
canônica por pessoa (volta a pedir OUTRA coisa = inspirou; para de pedir =
frustrou). **3 fricções previstas:** Nanda — a Giu virar mais uma coisa para
gerenciar (ela delegou UMA carga real ou só administrou o piloto?); Ian —
proatividade lida como cobrança (silêncio pode ser sucesso; ele VOLTA
sozinho?); Rafael — o primeiro a esbarrar no vão missão×mãos. **Prioridade
nº 1 pós-piloto (aposta a priori, a vida vivida vence):** fechar o ciclo da
pequena carga — de "eu seguro isso" até "isso foi RESOLVIDO" (a consulta
aconteceu?); hoje ela lembra mas não confere, e a Nanda segue como follow-up
ambulante da família. **Nota de sequência:** o piloto deve rodar COM o #14 em
produção (senão a sonda de expectativa perde o objeto) → H4 atualizado:
redeploy da main PÓS-merge do #14.

**07/07 — DECISÃO da fundadora: criada a 🌱 LIFE ARCHITECT — guardiã
permanente da missão da Base-X.** Ela não revisa tecnologia; revisa A VIDA da
pessoa, com a pergunta permanente "depois de conviver com a Giulieta, a vida
desta pessoa está objetivamente melhor?" e o teste definitivo "se a Giulieta
desaparecesse hoje, o que pioraria?" (valor real ≠ dependência). Dez lentes
(carga mental → qualidade de vida → fricção remanescente) registradas na
GOVERNANCA. **Nova regra da Base-X:** toda funcionalidade responde ANTES de
existir: que fricção humana reduz? que área da vida melhora? como a Life
Architect medirá o benefício na vida real? Sem as três → roadmap. Mandato:
revisa toda grande evolução ANTES de merge importante — inaugurada já no
PR #14; o relatório da Primeira Semana é material dela. Impacto: Manus
compartilha lentes com ela (experiência × vida); Code passa a incluir as 3
respostas na descrição de todo PR de funcionalidade.

**07/07 — DECISÃO da fundadora (definição oficial da Base-X + 6º PILAR).**
A Base-X NÃO é plataforma/backend/APIs: é uma **camada de inteligência
operacional da vida** — uma equipe invisível. Definição oficial: *"sistema
operacional de vida que orquestra pessoas, inteligência, especialistas,
conectores e automações para reduzir continuamente a fricção da vida humana"*;
Giulieta: *"a única presença humana através da qual uma pessoa percebe toda
essa inteligência"*. Giulieta = consciência; Base-X = ação em CICLO (percebe →
antecipa → organiza → decide → executa → acompanha → aprende). Fluxo: Vida →
Fricções → Missões → Resolução. Conecta áreas da vida, nunca apps (Uber =
Mobilidade; Calendar = Tempo; Gmail = Comunicação; Oura = Saúde). **Sexto
pilar oficializado: Life Orchestration** — "como coordenar tudo isso sem que
a pessoa perceba a complexidade?" (hoje exercido manualmente pelo Orquestrador
Técnico; em produto, realizado pelo Mission Engine). Registrado em
DECISOES-ARQUITETURA e GOVERNANCA (fora do git) e PERSONA.md (no git).

**07/07 — DECISÃO da fundadora (filosofia do piloto): "a Base-X nasce grande
na visão e cresce gradualmente na execução."** O piloto não é pequeno: a
Giulieta nasce sabendo que sua missão cobre TODAS as áreas da vida (18 áreas,
de agenda a hobbies), sem fingir o que ainda não faz — resposta canônica de
honestidade: "posso fazer isso quando essa capacidade estiver disponível e
você decidir ativá-la". Salvaguardas preservadas: nunca recitar lista/cardápio,
nunca prometer prazo (Promessa 8 intacta). Implementado no cérebro + PERSONA
(PR #14). Impacto Manus: a sonda de expectativa ("ela pareceu maior do que
faz hoje? isso frustrou ou inspirou?") vale observação na Primeira Semana.

**07/07 — DECISÃO DE ARQUITETURA da fundadora (marco do PR #13): abre a
segunda frente — Base-X — evoluindo JUNTO com a Giulieta.** Oficializados os
**cinco pilares permanentes da Base-X**: Identity · Living Context ·
Relationship · Friction Lens · Mission Engine. Toda integração futura existe
APENAS para fortalecer um pilar — nunca funcionalidades isoladas; a Base-X
nunca conecta APIs, resolve partes da vida. **Filtro duplo obrigatório** em
toda implementação (perspectiva Giulieta: relação/confiança/companhia ×
perspectiva Base-X: fricção/tempo/carga/organização/autonomia/qualidade de
vida). **Filosofia oficial do ecossistema:** "A Giulieta nunca responde
apenas ao prompt — responde à pessoa, ao relacionamento, ao momento, à missão
e ao propósito de melhorar concretamente a vida daquela pessoa" (agora também
no cérebro, brain.py). Registro completo: DECISOES-ARQUITETURA.md e
GOVERNANCA.md (fora do git); PERSONA.md (no git).

**07/07 — Code (implementação aprovada pela fundadora): presença natural +
Conversation Spine (PR #13).** Eixo 1 — os 5 ajustes da auditoria de presença
aplicados (regra de desabafo sem oferta; pergunta não-obrigatória e despedida
em ponto final; EMOÇÃO vence palavra-chave no modes.detect — o bug da Nine;
teto de emoji; textura/respostas mínimas; pergunta de preferência de voz
respeita pressa/emoção). Eixo 2 — **Conversation Spine**: a espinha da
conversa ATUAL (decisões, frases fortes, hipóteses, mudanças de direção,
compromissos) anotada pelo modelo via `anotar_fio`, guardada no perfil
(expira em 24h, máx. 10 itens) e injetada em todo turno com as 4 perguntas de
continuidade. **DISTINÇÃO CONCEITUAL (registro obrigatório): Conversation
Spine ≠ memória de longo prazo** — a spine é a linha viva da conversa atual e
EXPIRA; o permanente continua entrando por lembrar_fato (consentimento e
categorias de sempre). Simulação em teste: insight do início + mudança de
prioridade no meio sobrevivem até o fim de uma conversa de 120 mensagens,
com o histórico cru (16 msgs) já estourado. 50/50 testes.

**07/07 — Auditoria de PRESENÇA (painel conjunto Psicologia + Rel. Architect,
método: 3 conversas de 5min simuladas fiéis ao prompt real).** Veredito:
**ENTRE OS DOIS — do lado certo da fronteira, mas com o crachá aparecendo.**
Nenhuma conversa soa a atendente; o que denuncia a IA é a PRONTIDÃO PERFEITA
(toda resposta completa, polida, terminando em pergunta/oferta). Bug de
presença mais grave: palavra-chave de tarefa ("resolver") sequestra o modo
DENTRO de um desabafo às 23h — a companhia vira secretária no meio da emoção.
5 ajustes de alta alavancagem propostos (regra de desabafo sem oferta;
pergunta não-obrigatória + despedida em ponto final; emoção/horário vencem
palavra-chave no modo; teto de emoji; textura/respostas mínimas). NADA
implementado — decisão da Nanda pendente. Impacto Manus: as dimensões desta
auditoria são as mesmas da validação da Primeira Semana.

**07/07 — DECISÃO da fundadora (roadmap):** "Capability Connectors" morre;
nasce **LIFE CONNECTORS** — cada conector existe para tornar uma ÁREA DA VIDA
mais leve, nunca para integrar um app. Pergunta-definição: *"que parte da
vida esta integração ajuda a tornar mais leve?"*. Roadmap reclassificado em
3 níveis: **P1 essencial** (Tempo & Compromissos/Calendar · Pendências/Tasks ·
Burocracia/Gmail · Presença/voz natural — parte da promessa central, não
ficam para futuro distante) · **P2 alto impacto** (Mobilidade/Uber · Casa &
Abastecimento/Rappi · Vida Financeira) · **P3 contexto** (Corpo &
Descanso/Oura·Garmin·Apple Health — alimenta o Living Context antes de
qualquer ação). Registrado em ARQUITETURA-LIFE-CONNECTORS.md (fora do git) e
PERSONA.md item 5 (no git). Impacto: Manus — a experiência de autorização é
por área da vida, não por app; Despacho — credenciais/integrações seguem a
ordem P1→P2→P3 quando a engenharia for aprovada.

**07/07 (noite) — Code, sob delegação da fundadora ("faz tudo para mim,
manda para o despacho e para a manu"):** PR #12 (Friction Lens) mergeado —
era a especificação dela verbatim, 46/46 testes; main `9933b97` validada em
checkout limpo. Briefings completos criados e versionados para o fluxo único:
BRIEFING-DESPACHO.md (causa raiz → redeploy → recadastro → validação → go) e
BRIEFING-MANUS.md (a validação de experiência da Primeira Semana). Este
diário + briefings + checklist + protocolo + diagnostico_openai.py entram no
git para serem o meio comum da equipe (docs de ARQUITETURA-*/GOVERNANCA
continuam FORA do git, por regra da fundadora). Alicerces (Vida ao Lado,
Living Context, Missões): permanecem SEM engenharia, aguardando aprovação
formal. Deploy permanece com o Despacho.

**07/07 — Code:** Modo Agente registrado na GOVERNANCA.md; este diário criado
e semeado. PR #12 (Friction Lens) aberto: a Giulieta deixa de responder
passivamente — lente de fricção nas cinco vidas, com contenções (menor ajuda
útil; ficar quieta é resposta válida; "não" encerra).

**07/07 — Code (descoberta, do incidente):** falha do cérebro gerava SILÊNCIO
no WhatsApp e 500 no web/Telegram. Corrigido na main (falha honesta nos 3
canais, caminho único `_think_safe`). Lição de plataforma: toda fronteira
externa precisa de resposta honesta de degradação — vale para os futuros
conectores (impacto: Despacho ao configurar, Manus no tom das mensagens de
falha).

**07/07 — Code (problema aberto → Despacho):** os 3 sintomas do incidente
(STT, TTS, cérebro mudos) eram UMA causa na fronteira OpenAI. Produção voltou,
mas sem causa raiz nomeada não há prevenção de recorrência — e recorrência no
meio da Primeira Semana quebraria a confiança da família no pior momento.
Ferramenta pronta: `diagnostico_openai.py` (rodar no ambiente do Railway).

**06-07/07 — decisões da Nanda que orientam todos:** voz é identidade
(bloqueador de piloto, não feature) · Blueprints são garantia arquitetural
("não quero mais explicar para a Giulieta aquilo que já faz parte da
identidade dela") · posicionamento oficial: a Giulieta cuida das pequenas
cargas para sobrar vida ("ela me devolve pra quem eu amo") · a pessoa conversa
só com a Giulieta; todo o resto é bastidor.

## 4. Problemas identificados → soluções propostas (Orquestrador)

| Problema | Solução proposta | Dono |
|---|---|---|
| Causa raiz do incidente OpenAI sem nome — pode recorrer no meio do piloto | `diagnostico_openai.py` no ambiente Railway nomeia em 1 execução; se billing → alarme de saldo | Despacho (H1) |
| Ciclo de voz nunca validado ponta-a-ponta em produção | Roteiro de fumaça de 3 passos no BRIEFING-DESPACHO (membro "Teste") | Despacho (H2) |
| Identidades/Blueprints ainda não semeados em produção | Recadastro dos 4 (token não muda) após redeploy da `9933b97` | Despacho (H4) |
| Equipe sem meio comum de contexto | Este diário + briefings versionados no repo (meio oficial) | Todos |
| Falha do cérebro gerava silêncio (incidente) | RESOLVIDO na main — falha honesta nos 3 canais (`_think_safe`) | Code ✅ |
| Experiência do piloto sem dono definido | Faixa do Manus formalizada (BRIEFING-MANUS) | Manus (H6) |

## 5. Próximos passos priorizados (Orquestrador — ordem de execução)

1. **P0 · Despacho:** H1 (causa raiz) + H4 (redeploy `9933b97` + recadastro) + H5/H2 (checklist com ciclo de voz) → evidências neste diário.
2. **P0 · Nanda:** com H1–H5 verdes → **H7: o GO do piloto** e os convites (texto pronto no protocolo §1).
3. **P1 · Manus:** durante a semana — validação de experiência (pulso, atritos); dia 7-8 — entrevistas das 9 dimensões.
4. **P1 · Code:** plantão de bugs/ajustes durante a semana (escopo fechado: correções, nunca features); consolidar o relatório do Ciclo 1 com Manus.
5. **P2 · equipe:** o relatório da semana escolhe o que entra no Ciclo 2 (a fricção real de cada membro decide — não a lista de ideias).
6. **Roadmap (aguardando aprovação formal da Nanda para engenharia):** Life Connectors em 3 níveis — P1 essencial: Calendar, Tasks, Gmail, voz natural · P2: Uber, Rappi, financeiro · P3: Oura, Garmin, Apple Health (contexto) — + Living Context · Missões. Detalhe: PERSONA.md item 5 e ARQUITETURA-LIFE-CONNECTORS.md.

## 6. Relatório do ciclo (modelo — preenchido a cada ciclo)

**Ciclo 0 (fundação, pré-piloto) — fechado em 07/07:**
- **O que aprendemos:** intenção sem percepção não é produto (auditorias de
  posicionamento); silêncio em falha destrói confiança mais rápido que o erro
  em si (incidente); identidade conhecida ≠ relacionamento pronto (Blueprints).
- **O que melhorou a vida das pessoas:** ainda nada mensurável — a família não
  começou. (Honestidade: até a Primeira Semana rodar, tudo é hipótese.)
- **O que ainda gera fricção:** pedir as coisas ainda exige saber pedir (M-0
  condução aprovada em conceito); a Giulieta acorda cega para o agora (Living
  Context em fila); produção sem causa raiz nomeada.
- **Próxima evolução:** fechar H1–H5 → Primeira Semana → o relatório dela
  define o ciclo 1 (a fricção real de cada membro escolhe o que entra).
