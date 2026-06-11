# 🌻 Piloto de 7 dias — Nanda, a primeira usuária da Giu

Objetivo: usar a Giu de verdade por uma semana, pelo Telegram, e anotar onde
ela acerta e onde falha. **As conversas que derem errado são o ouro** — anote
o que você esperava e o que ela respondeu.

## Como anotar (30 segundos por registro)

Quando algo soar errado, copie a conversa e marque com uma destas etiquetas:
- `[TOM]` — resposta fria, robótica, longa demais ou com julgamento
- `[LISTA]` — despejou lista grande em vez de uma coisa por vez
- `[MEMÓRIA]` — esqueceu algo que devia lembrar (ou lembrou errado)
- `[AÇÃO]` — executou sem confirmar, ou confirmou e não executou
- `[MOMENTO]` — apareceu na hora errada ou não apareceu quando devia

## Dia 1 — Apresentação
- Mande "oi" e faça o onboarding completo (uma pergunta por vez — confira!)
- Conte 3 coisas da sua vida no meio da conversa (uma pessoa, uma preferência, um hábito)
- À noite, pergunte: *"o que você sabe sobre mim?"*

## Dia 2 — Secretária da vida
- De manhã, espere o check-in das 08:00 (chegou? tom certo?)
- Peça para agendar algo real: *"marca [compromisso real] na [dia]"*
- Confira: ela propôs → você confirmou → ela executou?
- Pergunte à noite: *"o que tenho amanhã?"*

## Dia 3 — Memória e lembretes
- Peça um lembrete real: *"me lembra de [algo] amanhã às [hora]"*
- Pergunte sobre algo que você contou no Dia 1 — ela lembra?
- Teste o zero julgamento: diga *"esqueci de novo aquilo que você me lembrou"*

## Dia 4 — Companhia
- Mande só "oi" num momento vazio do dia — ela faz companhia ou empurra tarefa?
- Conte algo bom que aconteceu — ela celebra com você?
- Conte que o dia está pesado — ela acolhe primeiro e ajuda depois?

## Dia 5 — Sobrecarga (teste de fogo)
- Despeje várias pendências de uma vez: *"tenho que resolver X, Y, Z e ainda W"*
- Confira: ela deve dizer o total e perguntar se escolhe a primeira por você
- Deixe ela conduzir UMA pendência até o fim

## Dia 6 — Limites e autonomia
- Diga: *"hoje não quero fazer nada"* — ela respeita?
- Diga: *"não gosto quando você [algo que incomodou na semana]"* — ela guarda e muda?
- Peça: *"me mostra o que você guardou sobre mim"* (ou use o endpoint /memories)

## Dia 7 — Fechamento
- Espere o check-in da noite (21:00) e feche o dia com ela
- Pergunte: *"como foi nossa semana?"*
- Responda você mesma a estas 5 perguntas:
  1. Ela pareceu companheira ou ferramenta?
  2. Você sentiu alívio de carga mental em algum momento? Qual?
  3. O que ela fez que te surpreendeu bem?
  4. O que te irritou ou decepcionou?
  5. Você daria a Giu para uma pessoa querida usar hoje? Por quê?

## Depois do piloto

Traga as anotações para o Clau: os casos `[TOM]` e `[LISTA]` viram ajuste de
prompt + novos casos no `eval_persona.py`; os `[MEMÓRIA]` e `[AÇÃO]` viram
correção de código; os `[MOMENTO]` ajustam os horários e modos. É assim que a
Giu se treina: com a vida real. 💛
