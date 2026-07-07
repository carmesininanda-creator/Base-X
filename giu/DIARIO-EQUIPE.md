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

**Código (`main` = `9933b97`):** Giulieta completa — voz como preferência de
relacionamento, persona lapidada, primeiro encontro por Blueprint,
posicionamento ("devolve a pessoa para quem ela ama"), Promessa 8, Blueprints
como garantia arquitetural no cérebro, identidade semeada, falha honesta nos
3 canais e **Friction Lens**. **46/46 testes E2E, validados em checkout limpo
da main.**

**PRs:** #9, #10, #11 e #12 mergeados. Fila de PRs: vazia.

**Produção (WhatsApp +55 11 92078-5067):** funcionando após incidente
(fronteira OpenAI). ⚠️ PENDENTE de confirmação formal (ver problemas abertos).

**Piloto Primeira Semana:** protocolo pronto (PROTOCOLO-PRIMEIRA-SEMANA.md).
NÃO iniciado — bloqueado pelos itens abertos abaixo. Participantes: Nanda,
Ian, Nine, Rafael (todos maiores de idade). Ninguém da família usa o número
até o go da Nanda.

**Alicerces em fila de aprovação (filosofia consolidada, zero engenharia):**
Vida ao Lado (conectores) · Living Context (o momento + fricção) · Missões
(condução única). Roadmap de capacidades registrado na PERSONA.md (item 5).

## 2. Handoffs abertos (quem deve o quê a quem)

| # | De → Para | O quê | Status |
|---|-----------|-------|--------|
| H1 | Despacho → Code | **Causa raiz do incidente OpenAI** (uma linha: chave? billing? rede?) — para registro e prevenção de recorrência (se billing: alarme de saldo antes do piloto) | ⏳ aberto |
| H2 | Despacho → equipe | **Ciclo completo de voz confirmado em produção**: áudio → entende → responde áudio+texto → "me responde só por escrito" → áudio → só texto | ⏳ aberto (bloqueador do piloto, decisão da Nanda) |
| H3 | ~~Nanda → Code~~ | PR #12 mergeado pelo Code em 07/07, sob delegação noturna da fundadora ("faz tudo para mim") — especificação era dela, verbatim; 46/46 testes | ✅ fechado |
| H4 | Despacho | **Redeploy da main `9933b97`** + **recadastro dos 4 membros** (mesmo POST, sem campo `welcome`; token não muda — ignorar o token exibido no re-POST) — semeia identidades e Blueprints. Roteiro completo: BRIEFING-DESPACHO.md | ⏳ aberto |
| H5 | Despacho | Checklist de validação (CHECKLIST-VALIDACAO-DESPACHO.md) — fumaça com membro "Teste", nunca com a família | ⏳ aberto |
| H6 | Manus | Validação de experiência do piloto — roteiro completo: BRIEFING-MANUS.md (protocolo, 9 dimensões, pulso, atritos a caçar) | ⏳ aberto |
| H7 | Nanda | **GO do piloto** — só ela dá, após H1–H5 verdes no diário | ⏳ aberto |

## 3. Registro corrido (descobertas · decisões · problemas)

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
