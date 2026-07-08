# ✅ Checklist de Lançamento — Giu Família v1.0

> **Decisão da fundadora (08/07/2026):** expansão genérica CONGELADA. A
> prioridade absoluta é **concluir a Base-X para a Família Fundadora** —
> Nanda, Ian, Pauline (Nine) e Rafael. Toda priorização responde:
> **"Isso deixa a Base-X da Família Fundadora mais completa?"**
> Sim → implementa. Não → roadmap.
>
> Este checklist define o que falta para a Giu Família estar **pronta para
> uso diário** pelos quatro. "Concluído" segue o critério dela: **quando a
> pessoa usar naturalmente, conversando, sem ajuda técnica** — por isso o
> checklist tem duas partes: o que fecha ANTES do uso diário (v1.0) e o que
> só a vida da família pode fechar (as semanas de laboratório vivo).

**Legenda:** ✅ pronto e testado · 🟡 pronto no código, falta viver/decidir ·
🔴 falta fazer · 👤 de quem depende

---

## 🚦 O CAMINHO CRÍTICO (os únicos itens entre hoje e o uso diário)

| # | Item | Estado | 👤 |
|---|------|--------|-----|
| CC1 | **Merge do PR #25** (Comunicação — pendências sem eco) | ✅ mergeado (delegado: "vamos concluir os itens restantes") | — |
| CC2 | **A PRESENÇA DA GIULIETA** (Sprint da Presença) — o ciclo técnico funciona (ela ouviu), mas a voz foi REPROVADA duas vezes ("parece um sistema lendo texto"). Nova regra dela: **a Giu Família NÃO lança com esta voz.** Caminho: Despacho provisiona chaves (ElevenLabs/Azure/Google) → bateria multi-provedor → o ouvido dela escolhe | 🔴 BLOQUEADOR do GO (sprint aberta) | Despacho + Nanda |
| CC3 | **Alarme de saldo OpenAI** no painel (recorrência do 429 no meio da semana é inaceitável) | 🔴 pendente | Despacho |
| CC4 | **Dívida M4**: check-in matinal sem a lei da oferta única | ✅ paga no PR #26 (bom dia sem coleção de culpas: vencidos ≤7 dias; recusadas nunca; ações antigas expiram) | — |
| CC5 | **SEMEAR A VIDA** (elevado pela fundadora: identidade + vida — pessoas, projetos, objetivos, rotina, preferências, contexto, fricções, INTERESSES, SONHOS, DESAFIOS, datas) | 🟡 mecanismo no PR #26 (com expurgo pela recusa — S1); fichas preenchidas prontas FORA do git aguardando revisão dela + aplicação do Despacho | Nanda revisa · Despacho aplica |
| CC6 | **GO da Primeira Semana** (o protocolo está pronto; os 4 entram no número) | 🔴 após CC1–CC4 | Nanda |

**Sem nenhum item além destes, a Giu Família entra em uso diário.** Todo o
resto abaixo ou já está pronto, ou é evolução que nasce DAS semanas de uso.

---

## As 10 dimensões da Giu (o pedido dela, seção a seção)

### 1. Relação
- ✅ Blueprints dos 4 por construção (garantia testada: nenhuma resposta sem
  passar pela camada) · welcomes aprovados · princípio do momento ·
  anti-dependência (a ponte, nunca o destino) · zero julgamento · direito ao
  silêncio · Portão do Cuidado de Quem Não Escolheu (a mãe protegida).
- 🟡 Falta apenas o que código não dá: **a relação acontecer** — as semanas
  reais. Marcos da relação e Relationship Health seguem CONGELADOS por
  decisão dela (interino: revisão semanal humana) — não bloqueiam v1.0.

### 2. Voz
- ✅ Energia Vital (a voz de quem gosta da vida) · velocidade natural 1.0 ·
  fôlego humano · telefone dígito a dígito · dose protegida · preferência
  voz/texto determinística · check-ins com voz para quem escolheu voz ·
  diretriz acompanha a resposta falada.
- 🔴 **CC2**: o ouvido da Nanda é o teste que falta (a voz mudou 3 vezes
  desde o último áudio dela).
- Pós-v1.0 (decisão dela): teste cego de velocidade; V1 gpt-4o-mini-tts com
  instrução de estilo (exige bateria de percepção).

### 3. Living Context
- ✅ Retrato "O MOMENTO DE AGORA" em todo turno · ⏰ Time (PT, estação,
  feriados, datas queridas com véspera, clima/sol por cidade autorizada) ·
  📅 Calendar (dia CHEIO → UMA prioridade; conflito por código; véspera;
  boa companhia sabe que horas são) · contrato com 12 garantias em teste
  (nunca levanta, silêncio, efêmero, confidencialidade, língua de vida,
  teto de tempo, oferta única, desacoplamento por AST).
- ✅ ✉️ Comunicação mergeada (pendências sem eco; CP-1 com recusa durável).
- Os demais domínios do retrato (Casa, Saúde…) nascem DAS fricções das
  semanas — ver "Domínios" abaixo.

### 4. Family Context
- ✅ Fatos de família/afeto · datas queridas (anotar_data/esquecer_data) ·
  recados entre membros SÓ com confirmação · confidencialidade absoluta
  TESTADA (nada atravessa membros — nem para a admin) · lei da mãe (mínimo
  necessário, sempre pela Nanda, Giu nunca a contata).
- 🟡 **CC5 (elevado)**: Semear a Vida — mecanismo no PR #26 com expurgo pela
  recusa; interesses/sonhos/desafios; autonomia como objetivo permanente no
  Blueprint dos filhos; fichas preenchidas fora do git aguardam a revisão dela.

### 5. Missões
- ✅ Ciclo completo vivido em teste: abrir → acompanhar → concluir →
  pergunta de VIDA (janela de 7 dias, independente da memória de contexto) ·
  desistir encerra com zero julgamento · missão parada = UM convite.
- 🟡 X4: medir na vida real (guiadas→missão) — material das semanas.

### 6. Memória
- ✅ Fatos com consentimento (recusa bloqueia TUDO: fatos, datas, cidade) ·
  esquecer_fato/esquecer_data/silenciar_pendencia (as mãos reais de apagar
  e calar) · apagamento total ("apagou, sumiu") · categoria limites
  inapagável (prova do consentimento) · confidencialidade familiar.
- Nada pendente para v1.0.

### 7. Blueprint
- ✅ Garantia arquitetural por construção + testes (Ian ≠ Pauline no mesmo
  turno; visitante sem blueprint não recebe camada) · hipótese NUNCA é
  rótulo — o que a pessoa mostra prevalece · identidade semeada no cadastro.
- Nada pendente para v1.0.

### 8. Conversation Spine
- ✅ Fio da conversa com TTL 24h, máx 10 itens, anotar_fio na hora ·
  simulação de conversa longa em teste · o "não" anotado no fio sustenta a
  oferta única dentro da conversa.
- Nada pendente para v1.0.

### 9. Friction Lens
- ✅ O olhar antes de toda resposta (5 passos) · exceção do desabafo (as 2
  primeiras respostas só presença; catálogo E pendências FICAM MUDOS) ·
  contexto nunca usado só porque existe · CP-1: a fricção tem memória
  (datas, pendências — com recusa DURÁVEL via silenciar_pendencia).
- Nada pendente para v1.0.

### 10. Mission Engine
- ✅ O motor: 7 campos, estados, histórico auditável, isolamento por pessoa,
  Life Radar (fricção real, nunca conversa→tarefa), Base-X invisível na
  conversa ("deixa comigo"), honestidade canônica quando falta capacidade.
- 🟡 O que só a vida fecha: as primeiras missões REAIS dos quatro.

---

## Os 12 Domínios para a Família (a lista dela) — o corte honesto da v1.0

O congelamento NÃO adia os domínios — ordena: **v1.0 = pisos internos
extraordinários + voz + go da semana**; os conectores externos entram como
ondas contínuas DEPOIS que o uso diário começar, puxados pelas fricções
reais (o ciclo permanente dela: cada semana gera aprendizados → fricções →
missões → capacidades).

| Domínio | Vive HOJE (piso interno) | Conector para a família (por ativação, pós-go) | 👤 destrava |
|---|---|---|---|
| ⏰ Tempo | ✅ Agenda Viva, lembretes, rotina, datas, dia cheio, conflito, véspera | Google Calendar ✅ construído — **falta só o OAuth** | Despacho (§6) |
| ✉️ Comunicação | ✅ pendências sem eco (mergeado) | Gmail (parecer rígido antes) | Despacho |
| 🏠 Casa | ✅ listas de mercado/farmácia como missão, manutenção guiada | Rappi · iFood · Alexa | parecer + ativação |
| 🚗 Mobilidade | ✅ trajeto mastigado guiado, consultas com deslocamento | Uber | parecer + ativação |
| 🩺 Saúde | ✅ consulta/exame como missão até o fim, medicamentos como lembrete | Vision (receitas/exames) · Oura · Garmin · Apple Health | parecer D-CV4 + ativação |
| 👨‍👩‍👧‍👦 Família | ✅ datas, recados, pontes, lei da mãe | agenda familiar (consentimento de todos) | decisão dela |
| 💰 Financeira | ✅ contas lembradas, decisão organizada | (nenhum priorizado — parecer mais rígido) | decisão dela |
| 🌿 Bem-estar | ✅ corpo pelo que a pessoa conta, modo noite, zero cobrança | wearables (dado sensível) | parecer + ativação |
| 📚 Aprendizado | ✅ passo que cabe no dia, constância sem cobrança | — (nativo interno) | — |
| 🎯 Goals | ✅ missões de longo prazo (ritmo escolhido pela pessoa) | — (nativo; marco de longo prazo qdo o 1º objetivo real nascer) | a vida |
| 👁️ Vision | 🔴 não existe (a Giu não enxerga) | **1º conector pós-go** (recomendação D-CV1-a): WhatsApp já entrega a foto; o modelo já compreende — falta o parecer (6 cláusulas) e o V-0 | Nanda (D-CV4) + Code |
| 📡 Multicanal | ✅ WhatsApp voz+texto (a porta da família) | identidade entre canais → depois Alexa/carro/TV/app | fricção real primeiro |

---

## O que este checklist NÃO inclui (de propósito)

Mercado, outros públicos, escala, funcionalidades "interessantes" — tudo
congelado por decisão dela. A Life Architect tem mandato para INTERROMPER
qualquer implementação que perca o foco: **a vida das pessoas é a
prioridade absoluta da Base-X.**
