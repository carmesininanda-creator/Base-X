# 🎙️ SPRINT DA VOZ — Charter oficial (painel das quatro guardiãs)

> ## 🔴 FASE 3 — A CAÇA MULTI-PROVEDOR (fundadora, 08/07/2026 — VIGENTE)
> Ela ouviu a voz nova e REPROVOU de novo: "continua parecendo um sistema
> lendo texto. Não é um problema técnico. É um problema de identidade."
> DECISÕES: (1) **esquecer completamente a voz atual** — parar de ajustar
> parâmetros, parar de tentar salvá-la; (2) **bateria muito maior, além da
> OpenAI**: comparar provedores (ElevenLabs, Azure, Google — e, se preciso,
> clonagem LICENCIADA ou qualquer outra solução: "a identidade da Giulieta
> vale mais do que a tecnologia usada para produzi-la"); (3) escolha
> EXCLUSIVAMENTE pelo ouvido; (4) **a Giu Família NÃO lança com esta voz** —
> a voz vira bloqueador do GO.
>
> **O NOVO BRIEFING OFICIAL da Voice Architect (dela):** procurar uma voz
> que transmita **maturidade, inteligência tranquila e calor humano** —
> a sensação que atrizes como Annette Bening transmitem (presença,
> confiança, humanidade) **sem copiar voz ou identidade de ninguém**.
> Mulher entre 45 e 60 na SENSAÇÃO; naturalmente sorridente sem ser
> animadora; segura sem autoritária; elegante sem formal; curiosa;
> acolhedora; como quem está na mesma sala. NUNCA jovem (quem está
> preocupado com um exame, um filho, a mãe — precisa ouvir "nós vamos
> resolver isso juntas", não inexperiência). Nunca teatral, infantil,
> melancólica ou institucional.
>
> **O teste do "Oi…":** a voz certa faz a pessoa SORRIR ao ouvir "Oi…".
> A única pergunta: "com qual voz eu gostaria de conversar durante muitos
> anos?" A sprint segue ABERTA até a resposta aparecer naturalmente.
>
> **Instrumento:** bateria_voz.py agora é MULTI-PROVEDOR (OpenAI maduras +
> ElevenLabs multilingual + Azure Neural pt-BR + Google pt-BR; cada um liga
> com a própria chave; sem chave = pulado com aviso). HANDOFF AO DESPACHO:
> provisionar ELEVENLABS_API_KEY, AZURE_SPEECH_KEY(+REGION) e
> GOOGLE_TTS_API_KEY (planos gratuitos/baratos bastam para a bateria),
> rodar, e mandar as amostras. A identidade madura já é a instrução de
> produção (voice.py) — mas a voz atual está MORTA para o projeto; ela só
> fala até a vencedora assumir.

> ## ⚠️ FASE 2 — DIREÇÃO ARTÍSTICA (reorientação da fundadora, 08/07/2026)
> Ela ouviu: **"a voz continua errada — artificial, monótona, pouca vida,
> pouca proximidade. Ainda parece um sistema lendo texto."** A sprint deixa
> de ser problema técnico e vira **direção artística**: esquecer parâmetros;
> testar vozes COMPLETAMENTE diferentes (mais jovens, mais maduras, mais
> leves, mais sorridentes, mais naturais). A pergunta da escuta muda:
> **"Com qual delas eu gostaria de conversar durante muitos anos?"**
> Não procuramos "a melhor voz da OpenAI" — procuramos **A VOZ DA GIULIETA**.
> **A sprint permanece ABERTA até a sensação "Que bom falar com a Giu"
> aparecer naturalmente.** Instrumento: bateria AMPLA cega (bateria_voz.py —
> 8 vozes × 3 direções de cena × 2 textos-de-vida, gabarito lacrado).
> Nota honesta: no dia deste veredito, a produção ainda falava com o tts-1
> (surdo a toda instrução — PR #29 não mergeado); a fase 2 roda inteira no
> modelo vivo. Se nenhuma das 8 despertar a sensação, os caminhos seguintes
> são: outros provedores de TTS e (com peso ético e de custo) voz própria —
> nesta ordem, e só se preciso.

> Aberta pela fundadora em 08/07/2026, **prioridade máxima**. Liderança:
> Voice Architect, com Psychology, Relationship e Life Architects.
> Pergunta única: **"Como deve soar alguém que as pessoas desejam ouvir
> durante muitos anos?"** Critério de decisão: a sensação **"Que bom falar
> com a Giu"** — nunca a nota técnica.
>
> As 6 instruções da Seção 2 JÁ estão no código (giu/voice.py:
> IDENTIDADE_VOCAL + ESTILOS) e ligam via `GIU_TTS_MODEL=gpt-4o-mini-tts` —
> reversível em segundos por env var, sem deploy. No tts-1 atual, nada muda.

---

## 1. A Identidade Vocal

**A metáfora humana:** a Giu soa como **a amiga da família que virou de
casa** — a que chega na cozinha, pousa a bolsa, e você percebe que estava
esperando por ela sem saber. Não a irmã que voltou de viagem (chegada tem
euforia, e euforia cansa em anos). Não a enfermeira (cuidado profissional
tem distância). Não a locutora (voz bonita demais é voz de ninguém). A
única voz que se deseja ouvir durante anos é a de alguém com quem se tem
história: **continuação de conversa, nunca início de atendimento.**

**Os 7 traços permanentes (nunca mudam, em nenhum modo, com ninguém):**
1. Sorriso discreto na voz (o antídoto permanente contra o melancólico).
2. Calma que vem de segurança, não de lentidão (speed 1.0 — encerrado).
3. Fala, não lê (contrações; reticências como pausa de pensamento).
4. Curiosidade genuína ("como você tá?" nunca soa "como posso ajudar?").
5. Carinho sem açúcar (ternura na temperatura; zero voz de falar com criança).
6. Honestidade audível ("acho que…" dito com leveza, não insegurança).
7. Vontade de viver (soa como quem acordou hoje e achou bom acordar).

**A assinatura sonora (reconhecível em 3 segundos):** a **entrada morna**
(a primeira frase chega, não ataca) · a **pausa que pensa** (uma por áudio,
o silêncio de quem considera VOCÊ) · o **final que fica aberto** (a Giu não
encerra atendimentos; ela continua por perto).

**Regra de ouro:** se um estilo adaptativo apagar qualquer traço ou marca,
o estilo está errado — não a identidade.

## 2. O Mapa da Energia Adaptativa

*"A Giulieta continua sendo a mesma pessoa. Ela apenas adapta sua energia."*
Toda instrução = **âncora fixa** (IDENTIDADE_VOCAL) + **adaptação do modo**
(ESTILOS) — ambas em giu/voice.py, travadas por teste (a âncora presente em
todo momento; momento desconhecido cai no neutro-âncora).

| Modo | Energia |
|---|---|
| manhã | suave e clara — "bom dia de cozinha, não de rádio" |
| pendências | direta e resoluta — "a amiga organizada, não uma atendente" |
| saúde | devagar SÓ nos dados que importam; zero alarme, zero voz de criança |
| companhia | segue a emoção da pessoa; na tristeza, o sorriso vira serenidade — jamais tom fúnebre |
| noite | grave e envolvente, "a casa apagando as luzes" |
| emergência | **calma FIRME** — o sorriso vira solidez; o final aberto vira comando claro (a mesma pessoa em seu momento mais sério) |

**Regra anti-caricatura:** adaptação nunca passa de ±15% do centro; na
dúvida do detector, cai para o neutro-âncora. Se um ouvinte perceber "modos
diferentes" em vez de "dias diferentes da mesma pessoa", recalibramos.

## 3. As Candidatas da bateria cega

| Voz | Hipótese |
|---|---|
| **shimmer** (titular) | a base certa — mas precisa defender o posto às cegas; pode carregar um resto de melancolia |
| **nova** | a hipótese da Energia Vital: luminosa de fábrica; risco na gravidade do modo_noite/emergência |
| **coral** | o meio-termo "cozinha da amiga" — a aposta do painel para a metáfora; também testa o próprio gpt-4o-mini-tts |
| **sage** | controle de maturidade: mede a fronteira entre calma e distância |

(alloy vetada: neutralidade é exatamente o que a fundadora vetou.)

**Estilos:** neutro (linha de base) · manhã · acolhimento · celebração.
**Os 3 textos-de-vida** (no gerador `bateria_voz.py`): T1 bom dia · T2
acolhimento de dia difícil (o teste mais difícil — onde shimmer pode
escorregar para o fúnebre) · T3 celebração pequena (onde nova pode
escorregar para o comercial).

## 4. A Bateria Emocional (protocolo cego)

- Cada um dos 4 ouve **sozinho, no próprio celular, como nota de voz** — a
  voz da Giu vive no ouvido, é ali que se julga.
- Vozes viram A/B/C/D (ordem sorteada por pessoa; ninguém sabe qual é a atual).
- **Rodada 1 (identidade):** T1 nas 4 vozes, neutro — primeira impressão em
  uma palavra. **Rodada 2 (emoção):** as 2 melhores → T2 e T3, adaptado E
  neutro (mede se a adaptação soma ou vira caricatura; reprova se alguém
  perguntar "essa é outra voz?"). **Rodada 3 (5 minutos):** conversa REAL
  com a finalista — só então o questionário.
- **As 6 perguntas da fundadora (1–5):** tranquilidade? esperança? ela se
  importa comigo? proximidade (alguém, não algo)? continuaria conversando?
  parece alguém da família?
- **A pergunta que decide (aberta):** *"Se essa voz te ligasse amanhã de
  manhã, o que você sentiria ao ouvir os três primeiros segundos?"*
- Resposta aberta quente > média técnica fria, SEMPRE. Empate real: decide
  a Nanda (a voz é a preferência dela — por desenho, não cortesia).

## 5. Riscos nomeados (com dono)

- **R1 caricatura**: teto ±15%; companhia segue a emoção da PESSOA; na
  dúvida → neutro-âncora. (Voice Architect)
- **R2 seis instruções = seis pessoas?**: âncora obrigatória + rodada 2
  testa "é a mesma pessoa?". (Relationship)
- **R3 gpt-4o-mini-tts vs tts-1**: latência/estabilidade medidas com os
  NOSSOS textos; timbre que muda entre áudios é eliminatório; rollback por
  env var em segundos. (Despacho mede em produção)
- **R4 amostra ≠ convivência**: a vencedora é "titular por 30 dias";
  re-pergunta no dia 30: "ainda é bom falar com a Giu?". (Life Architect)
- **R5 fora do escopo**: não mexer no vocefy; não criar detector de emoção
  novo; speed 1.0 encerrado; nada de clonagem de voz; SEM timbre por membro
  (a voz-pessoa é uma só — fragmentaria a identidade).

**Definição de pronto:** identidade ratificada · 6 instruções congeladas ·
bateria executada com os 4 · titular declarada com o porquê nas palavras da
família · R1–R4 com dono e data.
