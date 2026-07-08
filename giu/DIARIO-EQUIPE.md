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

**Código (`main` = `2f1b961`):** a Giulieta da Fase 2 — tudo do nascimento
(Blueprints por construção, Conversation Spine, Mission Engine + Life Radar +
Life Lens, organismo Base-X com 21 domínios, falha honesta, Energia Vital)
MAIS o **Living Context vivo**: ⏰ Time Provider (retrato "O MOMENTO DE
AGORA", datas queridas com véspera, clima/sol por cidade autorizada) e
📅 Calendar Provider (dia CHEIO → UMA prioridade, conflito por código,
véspera com preparo; "a Agenda Viva é o cérebro, o Google só sincroniza");
voz com fôlego humano e telefone dígito a dígito. **91/91 testes E2E em
checkout limpo.**

**PRs:** #9 a #24 mergeados (#23 e #24 = Fase 2). Fila de PRs: vazia.

**Produção (WhatsApp +55 11 92078-5067):** deploy automático ativo; Time e
Calendar Providers NO AR. ⚠️ Ciclo de voz (H2) e alarme de saldo pendentes.

**Família Fundadora — Primeira Semana:** protocolo pronto
(PROTOCOLO-PRIMEIRA-SEMANA.md). NÃO iniciada — aguarda o go da Nanda
(H2 + H1). Participantes: Nanda, Ian, Nine, Rafael. Fase 3 dos Providers
(validação em uso real) acontece dentro dela.

**Pilares (estado):** Identity ✅ · Friction Lens ✅ · Mission Engine ✅ ·
**Living Context ✅ VIVO (Time + Calendar; próximos na ordem dela:
Communication → Home → Mobility → Health)** · Relationship (camada ✅; motor
RIM congelado). Life Connectors: Google Calendar por pessoa ✅ (aguarda OAuth
do Despacho, §6) · open_meteo ✅ (T7). Duas frentes permanentes: capacidades
+ Voz e Presença.

## 2. Handoffs abertos (quem deve o quê a quem)

| # | De → Para | O quê | Status |
|---|-----------|-------|--------|
| H1 | ~~Despacho → Code~~ | **CAUSA RAIZ NOMEADA: quota/crédito OpenAI (HTTP 429)**. Prevenção pendente: Despacho confirmar ALARME DE SALDO no painel OpenAI (recorrência no meio do piloto é inaceitável) | ✅ causa fechada · ⚠️ alarme pendente |
| H2 | Despacho → equipe | **Ciclo completo de voz confirmado em produção**: áudio → entende → responde áudio+texto → "me responde só por escrito" → áudio → só texto | ⏳ aberto (bloqueador do piloto, decisão da Nanda) |
| H3 | ~~Nanda → Code~~ | PR #12 mergeado pelo Code em 07/07, sob delegação noturna da fundadora ("faz tudo para mim") — especificação era dela, verbatim; 46/46 testes | ✅ fechado |
| H4 | ~~Despacho~~ | Deploy automático GitHub→Railway ATIVO (main "carta da Giulieta" no ar); 4 membros registrados com Blueprints e welcomes; Nanda reconhecida pelo nome na 1ª mensagem, onboarding completo, preferência de voz registrada | ✅ fechado |
| H5 | Despacho | Checklist: fumaça conversacional ✅ (14 msgs com a Nanda). FALTA: **ciclo de voz (H2)** — Nanda escolheu VOZ; confirmar áudio chegando + "só por escrito" respeitado. E OAuth do Google (§6) para a capacidade de agenda | 🟡 parcial |
| H6 | Manus | Validação de experiência do piloto — roteiro completo: BRIEFING-MANUS.md (protocolo, 9 dimensões, pulso, atritos a caçar). **X5 ✅ FECHADO** (painel de presença: PASSA; endurecimento de 1 linha aplicado, PR #19) | 🟡 X5 ✅ · semana ⏳ |
| H7 | Nanda | **GO do piloto** — só ela dá, após H1–H5 verdes no diário | ⏳ aberto |

## 3. Registro corrido (descobertas · decisões · problemas)

**08/07 — 🌱 SEMEAR A VIDA ampliado pela fundadora ("identidade + vida":
interesses, sonhos, desafios; autonomia como OBJETIVO PERMANENTE da relação
com os três filhos) — PR #26 aberto (merge dela). CC1 ✅ (PR #25 mergeado
sob delegação) e CC4 ✅ (M4 paga).** A vida real ditada por ela (interesses
do Ian/Nine/Rafa, desafios de autonomia, o sonho dos EUA do Rafa, peptídeos/
cannabis medicinal com responsabilidade total) virou FICHAS FORA DO GIT
(vida-inicial/, no .gitignore) — aplicação pelo Despacho via endpoint, após
o merge e a revisão dela. LIFE ARCHITECT **BLOQUEOU** e foi atendida antes
do PR: **S1** o "não" no consentimento agora EXPURGA todo o semeio (dados
de terceiros jamais sobrevivem à recusa — o germe de vigilância por
procuração morreu no ovo); **S2** datas semeadas carregam ORIGEM (o retrato
nunca diz "ela pediu"); S3/S4 a FONTE jamais vira argumento + fricção
semeada NUNCA abre assunto + terceiros no mínimo; S5 bom dia sem coleção de
culpas; S6 endpoint distingue recusa de idempotência; S7 dedupe por SQL;
S8 os 4 testes. Blueprint dos filhos ganhou o objetivo permanente de
autonomia (nunca renderiza para a Nanda). 118/118 testes. CAMINHO CRÍTICO
restante: merge do #26 (Nanda) · revisão das fichas + aplicação (Nanda +
Despacho) · H2 teste de voz (Nanda) · alarme de saldo (Despacho) · GO.

**08/07 — 🧊 DECISÃO da fundadora: CONGELAMENTO da expansão genérica +
CHECKLIST DE LANÇAMENTO da Giu Família v1.0 (aguarda aprovação dela).**
Prioridade absoluta: **concluir a Base-X para a Família Fundadora** (Nanda,
Ian, Pauline, Rafael) — sem mercado, sem milhões de usuários, sem
funcionalidades futuras. Filtro de toda priorização: "isso deixa a Base-X
da Família Fundadora mais completa?" (sim → implementa; não → roadmap). As
duas fases NÃO se misturam: primeiro a Giu Família extraordinária; depois a
expansão contínua. TAMBÉM REGISTRADAS as consolidações dela: "a Base-X não
pertence aos Providers — os Providers pertencem à Base-X"; domínios
pertencem às NECESSIDADES humanas; Família Fundadora = LABORATÓRIO VIVO;
**as 5 perguntas obrigatórias** de toda implementação (fricção? vida da
família? missão? domínio? como a Life Architect mede?); ciclo permanente
semanal (aprendizados → fricções → missões → capacidades); Vision inclui
pessoas QUANDO AUTORIZADO; "não estamos construindo software — estamos
construindo um sistema que aprende a melhorar a vida"; **a Life Architect
tem mandato para INTERROMPER implementação que perca o foco**. ENTREGUE:
CHECKLIST-GIU-FAMILIA-V1.md (no git) — as 10 dimensões que ela pediu
(Relação, Voz, Living Context, Family Context, Missões, Memória, Blueprint,
Spine, Friction Lens, Mission Engine) com estado honesto item a item + o
CAMINHO CRÍTICO de 6 itens entre hoje e o uso diário: CC1 merge do PR #25 ·
CC2 teste de voz da Nanda (H2) · CC3 alarme de saldo (Despacho) · CC4
dívida M4 (check-in sem CP-1 — leva curta) · CC5 aniversários dos 4
(decisão dela, D-CP1) · CC6 o GO. Fora isso: as 10 dimensões estão prontas
e testadas (104/104 na branch do PR #25); conectores externos (Gmail, Uber,
Rappi, Oura, Alexa, Vision, Google OAuth) entram como ondas contínuas
DEPOIS do go, puxados pelas fricções reais das semanas.

**08/07 — ✅ FUNDADORA APROVOU a arquitetura de CAPACIDADES DE VIDA (com 3
ajustes dela) + ✉️ COMUNICAÇÃO implementada (PR #25 aberto — o merge é
dela).** Ajustes registrados: (1) os Domínios pertencem às NECESSIDADES da
Família Fundadora, nunca a uma pessoa (casos da seção 6 = ilustrações);
(2) Vision ampliado (documentos, receitas médicas, exames, alimentos,
objetos, ambientes, ROUPAS, MEDICAMENTOS); (3) Communication ampliado (TODA
comunicação relevante — e-mail, mensagens, documentos, notificações — não
apenas Gmail). "A Base-X passa oficialmente a ser organizada por Capacidades
de Vida; os Providers continuam existindo internamente, mas deixam de ser a
forma como pensamos o sistema." IMPLEMENTAÇÃO CONTÍNUA RETOMADA pelo domínio
Comunicação (piso = o que a pessoa CONTA): pendências acordam no retrato
como RESUMO com idade (nunca lista), C5 paga e mudada de casa (uma porta
só). LIFE ARCHITECT **BLOQUEOU** — e o bloqueio foi RESOLVIDO antes do
merge: M1 "risquei daqui" era impossível (nasceu esquecer_fato — a mão real
de apagar; onboarding não planta mais pendência eterna: traço→rotina); M2 o
"não" não tinha memória durável (nasceu silenciar_pendencia — recusa cala a
oferta PARA SEMPRE sem falsificar conclusão; item segue vivo em ver_agenda);
M3 fricção velha ganha contagem "(e mais N)"; M5 idade testada com backdate;
M6 idade orienta a Giu, nunca é dita; M7 desabafo cala a linha (cláusula
explícita); M8 teto do retrato exercido com stub. **M4 = dívida 14 dias**:
check-in matinal conta pendências sem data todo dia sem CP-1 (routines/
server — fechar a segunda porta na próxima leva). 104/104 testes.
DEMO-COMUNICACAO.md entregue. PENDENTE: merge do PR #25 pela fundadora;
próximos domínios na ordem dela (Vision após Communication, D-CV1
recomendação (a), salvo decisão contrária; depois Home → Mobility → Health);
H2 (áudio da Nanda) e alarme de saldo (Despacho) seguem abertos.

**08/07 — 🌳 CORREÇÃO DE DIREÇÃO da fundadora: a Base-X se reorganiza por
CAPACIDADES DE VIDA (revisão completa desenhada; AGUARDA APROVAÇÃO DELA;
implementação PAUSADA por ordem expressa).** "A Base-X não nasce de
componentes. Ela nasce de capacidades de vida. (...) Ela cuida da vida."
12 DOMÍNIOS oficiais: Saúde · Tempo (absorve Agenda) · Casa · Mobilidade ·
Comunicação · Vida Financeira · Família (inclui acompanhamento de idosos) ·
Bem-estar (separa de Saúde) · Aprendizado · Goals (meses/anos) + os NOVOS
👁️ VISION (a Giulieta enxerga: fotos, receitas, exames, plantas — "parte
natural da experiência") e 📡 MULTICANAL ("a Giulieta não pertence ao
WhatsApp"). Providers/Connectors/Especialistas DESCEM para mecânica interna
(nenhum criado/renomeado/extinto; ARQUITETURA-CONTEXT-PROVIDERS segue
vigente como camada de mecânica). REVISÃO em
ARQUITETURA-CAPACIDADES-DE-VIDA.md (fora do git) com parecer da LIFE
ARCHITECT (aprova com ajustes; 8 achados INCORPORADOS — os altos: V1
Emergências só muda de organograma com assinatura dela e garantia P0
escrita; V2 o "hoje" do Multicanal estava inflado — continuidade entre
canais NÃO existe (a mesma pessoa em duas portas = duas memórias); primeira
capacidade real do domínio é identidade unificada; V3 portões do Vision
endurecidos — o que a Giu FALA da imagem também é dado, terceiros/crianças/
trânsito pela OpenAI cobertos; V4 PORTÃO DO CUIDADO DE QUEM NÃO ESCOLHEU —
a mãe da Nanda jamais vigiada: mínimo necessário, sempre pela Nanda, Giu
nunca a contata, desconforto encerra). CRITÉRIO FINAL da fundadora atendido:
caso real DESTA SEMANA por pessoa nos 12 domínios (10 já vivos hoje; Vision
e continuidade multicanal nascem de fricção nomeada da família). CINCO
DECISÕES aguardam ela (D-CV1 posição do Vision na fila; D-CV2 remapeamento;
D-CV3 fila; D-CV4 privacidade do Vision; D-CV5 Emergências). Exceção formal
ao "fim da fase conceitual" registrada em DECISOES-ARQUITETURA.md.

**08/07 — ✅ PR #24 MERGEADO (a pedido dela: "merge") — main 2f1b961,
91/91 em worktree limpo. Time + Calendar Providers e voz com fôlego EM
PRODUÇÃO (deploy automático). Ambos os Providers entram agora na fase 3:
validação em uso real pela Família Fundadora.**

**08/07 — 🏗️ FASE 2 EM RITMO: fundadora MERGEOU o Time Provider (PR #23) e
decidiu o fim da fase conceitual; 📅 CALENDAR PROVIDER + 🎙️ VOZ V0 prontos
no PR #24 (mergeado em seguida, ver acima).** DECISÕES registradas: sem novos
motores/documentos conceituais — só capacidades reais; ordem oficial:
Calendar → Communication (Gmail) → Home (Rappi/iFood/Alexa) → Mobility
(Uber) → Health (Oura/Garmin/Apple Health); DUAS FRENTES PERMANENTES
(capacidades + Voz e Presença); novo portão obrigatório de toda capacidade:
"isso faz a Giulieta parecer mais uma boa companhia ou apenas uma IA mais
capaz?". NO PR #24: (1) Calendar Provider — "Google Calendar será apenas
sincronização; a Agenda Viva continua sendo o cérebro" (dela, textual):
dia CHEIO → UMA prioridade (Blueprint da Pauline em código), véspera com
preparo leve, CONFLITO detectado por código, bloco AGENDA VIVA absorvido
pelo retrato (CP-2); T7 paga (open_meteo virou Life Connector em
integrations/; teste por AST proíbe Provider conhecer fornecedor);
(2) Voz V0 — fôlego humano (frase longa respira na vírgula do meio; nenhuma
palavra muda) + telefone dígito a dígito (dose segue protegida). LIFE
ARCHITECT: aprova com dívidas — C1 ("boa companhia sabe que horas são": o
dia já vivido calava... corrigido ANTES do merge), C2 (Google conectado →
retrato declara o próprio limite; nunca "dia livre" sem conferir), C3
(teste AST), C6, C8 pagas; T9/C5/C7 registradas como limites conhecidos no
DEMO-CALENDAR-PROVIDER.md. 91/91 testes. PENDENTE: merge do PR #24 pela
fundadora; validação em uso real dos dois Providers pela Família Fundadora;
OAuth Google (Despacho, §6); alarme de saldo OpenAI (Despacho); teste de
áudio da Nanda (H2) — agora com fôlego e Energia Vital juntos.

**08/07 — 🏗️ FASE 2 ABERTA: arquitetura APROVADA pela fundadora + ⏰ TIME
PROVIDER implementado (PR #23 aberto — link enviado; O MERGE É DELA).**
Decisões registradas: (a) **estratégia oficial da Fase 2** — a Base-X existe
agora EXCLUSIVAMENTE para a **FAMÍLIA FUNDADORA** (novo nome oficial, por
decisão dela: não é mais "piloto" — quem funda não é experimento); toda
implementação responde primeiro "como isso melhora a vida da Nanda, do Ian,
da Pauline ou do Rafael?"; (b) **sequência obrigatória por Provider**:
arquitetura → Life Architect valida → uso real pela Família Fundadora →
aprendizados registrados → evolução; um de cada vez, completo antes do
próximo; a Life Architect responde ao final: "a vida ficou objetivamente
melhor?". IMPLEMENTADO no PR #23: pacote giu/context (montador do retrato
"O MOMENTO DE AGORA" com contrato universal) + Time Provider — piso puro
(AGORA em português, estação, feriados fixos), datas queridas
(anotar_data/esquecer_data: acordam no dia e na VÉSPERA), clima e sol pela
cidade AUTORIZADA (definir_cidade: opt-in, nível cidade, revogável, teto
2,5s, falha muda); CP-2 cumprido (o retrato SUBSTITUIU o antigo AGORA; um
único AGORA: no prompt; orçamento em teste). REVISÃO DA LIFE ARCHITECT:
aprova com dívidas — **T1–T6 PAGAS ANTES DO MERGE** (29/02 existe; data
única de ano passado jamais volta; esquecer_data é lei; trocar de cidade
mata o céu antigo; o "não" ENCERRA e viaja com o dado; consentimento vale
para cidade). DÍVIDAS COM PRAZO: **T7** — extrair open_meteo para
integrations/ como Life Connector + teste de desacoplamento (ANTES do
Calendar Provider); **T8** — fuso por pessoa e teto wall-clock do snapshot
(limite conhecido, ok para a Família Fundadora hoje). 79/79 testes.
DEMO-TIME-PROVIDER.md entregue (nível 1, cenas com a Nanda). **SEGUNDA ONDA
DESENHADA sem código (ordem dela): 🥇 Calendar (Agenda Viva é o cérebro;
Google só sincroniza) · 🥈 Communication · 🥉 Home · 4️⃣ Mobility** — as 5
respostas de cada um em ARQUITETURA-CONTEXT-PROVIDERS.md §9-A. ⚠️ Esta ordem
substitui a anterior; Family/Projects/Relationship continuam desenhados e
aguardam reposicionamento dela na fila.

**08/07 — 🧬 DECISÃO da fundadora: CONTEXT PROVIDERS — "o passo mais
importante da Base-X" (arquitetura desenhada; AGUARDANDO APROVAÇÃO DELA;
zero código por ordem expressa).** Providers não são fontes de dados: são
DIMENSÕES DA VIDA HUMANA; cada um responde só "como está esta parte da vida
desta pessoa neste momento?". A Giulieta nunca pergunta às APIs — pergunta ao
Living Context, que pergunta aos 10 Providers (Time, Calendar, Communication,
Health, Mobility, Home, Finance, Family, Projects, Relationship), que
perguntam aos Life Connectors autorizados. "A Base-X nunca depende de
fornecedores. Ela depende apenas do conceito da vida humana." Antes de
implementar, ela exigiu a arquitetura definitiva no papel: as 8 respostas por
Provider (dimensão, fricção, piso interno, conectores futuros, vida sem
conector, degradação em falha, conversa com Friction Lens, alimentação do
Mission Engine) + a matriz Dimensão→Provider→Conector→Especialistas→Missões.
FEITO em ARQUITETURA-CONTEXT-PROVIDERS.md (fora do git). REVISÃO DA LIFE
ARCHITECT: **aprova com ajustes — 8 achados, todos incorporados**; os dois
ALTOS: (CP-1) efemeridade total viraria máquina de reoferta — nasceu a lei
"a fricção tem memória": oferta anotada no fio, "não" vira fato `limites`,
fricção com "não" está ENCERRADA (garantia de teste); (CP-2) o retrato
SUBSTITUI os blocos atuais do prompt (AGORA, AGENDA VIVA…), nunca soma —
orçamento global: o prompt não cresce. Também: fluxo oficial UNIFICADO
(perceber-e-decidir → organizar-e-executar, com Memória e Despacho de
volta), mapeamento completo 21 domínios→10 providers (trabalho vive em
Projects+Calendar — área própria é decisão dela), pisos inflados corrigidos
(estação/feriados e lugar-na-agenda ainda não existem no código), e 4 travas
novas de teste (oferta única, teto de tempo por snapshot, presença antes de
oferta, só o testemunhado). SEIS DECISÕES aguardam a fundadora (D-CP1 a
D-CP6): semear aniversários, cidade p/ clima, ordem das ondas, retrato nos
check-ins consentidos, confirmação do fluxo único, trabalho como área.
Implementação Provider por Provider SÓ após o aval dela.

**08/07 — ⚡ DECISÃO da fundadora: ENERGIA VITAL (atributo permanente da voz)
+ correção mergeada (PR #22, main 804a614, 62/62).** "A voz atual transmite
uma sensação de tristeza ou desânimo. Isso não representa a Giulieta." A voz
transmite calma, esperança, curiosidade, carinho, segurança, leveza e VONTADE
DE VIVER — e nunca soa cansada, melancólica, deprimida, excessivamente lenta,
excessivamente séria ou como leitura de texto. Novo portão da Voice Architect
antes de aprovar qualquer voz: **"depois de ouvir esta voz durante cinco
minutos, a pessoa sente mais energia para viver ou menos?"** Aplicado no
código: velocidade 0.92 → 1.0 (o 0.92 uniforme soava sedado — calma é
variação e fôlego, não lentidão) e ENERGIA VITAL como primeira diretriz da
fala ("você soa como alguém que GOSTA da vida — um sorriso discreto na voz").
Novo TESTE EMOCIONAL no protocolo da semana: ouvintes não técnicos nomeiam o
que sentiram (esperança/tranquilidade/alegria serena/curiosidade/cuidado ×
tristeza/monotonia/cansaço/distanciamento). "A Giulieta deve transmitir a
sensação de alguém que gosta da vida" — identidade oficial da voz. ⚠️ H2
continua aberto: o próximo áudio da Nanda já sai com a diretriz nova e a
velocidade natural.

**08/07 — 🌱 DECISÃO da fundadora: LIVING CONTEXT OFICIAL em 10 ÁREAS DA
VIDA (registro de arquitetura; sem código neste ciclo).** "Essa passa a ser a
arquitetura oficial do Living Context." O Living Context representa o ESTADO
ATUAL DA VIDA da pessoa, organizado em 10 áreas: 1.Tempo · 2.Agenda ·
3.Comunicação · 4.Saúde · 5.Mobilidade · 6.Casa · 7.Vida Financeira ·
8.Família · 9.Projetos de Vida · 10.Relationship Context. Completamente
MODULAR: funciona mesmo sem nenhum conector; cada área enriquece à medida que
Life Connectors forem autorizados. Princípio reforçado (textual): "a Giulieta
nunca usa contexto apenas porque ele existe — usa apenas quando melhora
concretamente a vida da pessoa." Pipeline oficial: **Living Context → Friction
Lens ("qual pequena fricção vale a pena reduzir agora?") → Mission Engine
("quem deve trabalhar para resolver isso?")** — a pessoa continua conversando
apenas com a Giulieta; toda a Base-X continua invisível. Registrado em
ARQUITETURA-LIVING-CONTEXT.md (fora do git, regra da fundadora); a engenharia
segue o roadmap LC-0→LC-4, alimentada pela fricção real do piloto — a
estrutura oficial não antecipa código.

**08/07 — 🎙️ VOICE ARCHITECT: DIAGNÓSTICO INAUGURAL + correções V0 mergeadas
(PR #21, main b2d6aa7, 62/62).** Veredito: "o conteúdo já é de família — é o
som que ainda é de máquina"; pelo portão triplo, HOJE a voz seria sentida como
excelente IA, não companhia — "mas a distância é menor do que parece". DUAS
DESCOBERTAS DE CÓDIGO, corrigidas na hora: (1) quem escolheu voz recebia áudio
sintetizado de texto escrito para o olho (diretriz seguia o canal de entrada;
agora segue "a resposta será falada"); (2) o check-in proativo chegava MUDO
até para quem escolheu voz — agora o "bom dia" fala (texto primeiro, sempre).
PRESCRIÇÕES EM ABERTO (decisão da fundadora): V0 restante — vocefy como
diretor de fôlego (frases de 7-12 palavras), telefone dígito a dígito, teste
cego de velocidade (0.92 uniforme vs 1.0 com fôlego — "calma é variação, não
lentidão"); V1 — migrar para gpt-4o-mini-tts com instrução de estilo ("fale
como alguém da família…"), a PRIMEIRA porta para prosódia emocional (exige
bateria de percepção antes de virar padrão); V2 — voz própria, prosódia por
emoção do turno, áudios curtos encadeados. OS 10 MANDAMENTOS DA VOZ
estabelecidos (carta de identidade sonora — "fôlego humano", "a pausa é
conteúdo", "calma é variação", "errar como gente", "a voz aproxima; a verdade
permanece"). Medição na semana: reciprocidade de voz (modality no banco),
"ouve na hora ou deixa pra depois?", e o pronome que ela usa ("a Giu falou" ×
"o negócio mandou áudio").

**08/07 — DECISÃO da fundadora: abre a EVOLUÇÃO DA VOZ.** Criada a 🎙️ VOICE
ARCHITECT (papel permanente — missão: não escolher TTS, mas construir a voz
que faça sentir "que bom que a Giu está aqui"; nunca atendente/robô/locutora —
alguém da família). Criado o PORTÃO TRIPLO (Voice + Life + Relationship
Architects, juntas, antes de todo merge importante: "excelente IA ou companhia
que tornou a vida melhor?" — o principal critério da Giulieta). Princípio novo
no cérebro (PR #20, mergeado, main 941eaef, 60/60): "a Giulieta nunca fala
apenas para responder — fala para melhorar AQUELE momento" ("como posso tornar
os próximos minutos da vida desta pessoa um pouco melhores?"). Diagnóstico
inaugural da Voice Architect EM ANDAMENTO (por que a voz atual transmite
tecnologia; prescrições V0/V1/V2; os 10 mandamentos da voz; medição na semana).
FRASE-NORTE registrada (fundadora): "A Giulieta não quer impressionar ninguém.
Ela quer cuidar tão bem das pessoas que, um dia, elas simplesmente não
consigam mais imaginar a vida sem ela ao lado." — harmonizada com o teste
definitivo da Life Architect: o 'não imaginar a vida sem ela' deve nascer de
VALOR REAL (o que pioraria se ela sumisse), jamais de apego fabricado; os
guarda-corpos anti-dependência continuam invioláveis.

**08/07 — X5 FECHADO (painel de presença, verificação-relâmpago pré-GO):
PASSA — o desabafo segue protegido; endurecimento de 1 linha aplicado e
mergeado (PR #19, main 89741df, 60/60).** Simulação do pior caso (Nine 22h30,
3 gatilhos de domínio dentro da emoção): duas primeiras respostas só presença;
UMA oferta, escolhida por ela; despedida em ponto final; zero missões nascidas
do desabafo. Ponto apertado: modo_noite manda ofertar e o catálogo de 21
domínios não lembrava a exceção — agora o cabeçalho do catálogo declara "EM
DESABAFO OU EMOÇÃO QUENTE, ESTE CATÁLOGO FICA MUDO". Confiança 80%→~92%.
**GO da fundadora agora depende só de: (a) H2 — ela mandar um áudio e
confirmar o ciclo de voz; (b) alarme de saldo OpenAI (Despacho).**

**08/07 — DESPACHO: RELATÓRIO OPERACIONAL v2 — A GIULIETA ESTÁ VIVA.** Deploy
automático ativo (main "carta" no ar); OpenAI resolvido — **CAUSA RAIZ: quota
429 (crédito)**; 14 mensagens reais trocadas com a Nanda: reconhecida pelo
nome sem perguntar, welcome entregue, onboarding completo, preferência de voz
registrada, memória gravando, segurança OK. **RESPOSTAS DO CODE às dúvidas
código×config do Despacho:** (1) Conector Google Calendar POR PESSOA está
100% NO MAIN (PR #18) — falta SÓ configuração (OAuth CLIENT_ID/SECRET +
GIU_BASE_URL, briefing §6); Google TASKS ainda NÃO existe (próxima capacidade
da fila, pós-aceitação da agenda). (2) LEMBRETES: totalmente funcionais no
main (tabela + loop + ferramenta, testados). (3) CORREÇÃO ao relatório:
"criação de compromissos depende do Google Calendar" está ERRADO — a Agenda
Viva interna agenda HOJE (propõe→confirma→executa + lembretes); o Google é o
espelho na agenda real, não pré-requisito. **O que ainda gateia o GO (regras
da fundadora, só ela pode dispensar):** (a) H2 — ciclo de voz confirmado
(voz é identidade = bloqueador declarado; e a Nanda ESCOLHEU voz — validar
áudio chegando); (b) X5 — reauditoria-relâmpago do Manus; (c) alarme de saldo
OpenAI (a causa raiz foi quota — sem alarme, recorre no meio da semana).
OAuth do Google NÃO bloqueia o piloto (capacidade de agenda entra em paralelo).

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
