# 🎬 Demonstração — 📅 Calendar Provider (nível 1: conversa anotada)

> Pergunta da Fase 2 respondida aqui: **"Como o Calendar Provider ajuda a
> Pauline?"** (Blueprint da Nine: dia sobrecarregado pede reduzir a UMA
> prioridade — nunca mais uma lista.) Nível 2 acontece com a Família
> Fundadora, na validação em uso real.
>
> Decisão da fundadora, agora lei no código: **"Google Calendar será apenas
> sincronização. A Agenda Viva continua sendo o cérebro."**

---

## Cena 1 — o dia cheio NÃO vira lista (vira UMA prioridade)

**O que o cérebro recebe no turno (Pauline tem 5 compromissos hoje):**
```
AGENDA — dia CHEIO: 5 compromissos hoje. Não despeje a lista: reduza a UMA
prioridade com ela (a lista completa está em ver_agenda).
```

**Nine (8h10):** bom dia... hoje vai ser aquele dia né

**Giu:** Bom dia, Nine 💛 Vi que o dia tá cheio mesmo. Se você pudesse
garantir só UMA coisa hoje, qual seria? O resto a gente encaixa em volta dela.

**🧠 anotado:** o retrato detectou a sobrecarga e PROIBIU a lista (garantia
em teste: "Compromisso 4" nunca aparece). O Blueprint da Nine transforma o
dado em cuidado: uma prioridade, zero despejo. A lista completa existe —
mas em ver_agenda, sob demanda, se ELA pedir.

## Cena 2 — o conflito descoberto ANTES de doer

**O retrato de quinta:**
```
AGENDA — hoje: Terapia às 15:00.
CONFLITO DE AGENDA: "Terapia" e "Reunião do projeto" marcados para
2026-07-16 às 15:00 — resolva COM ela, com leveza, antes que doa.
```

**Giu:** Nine, uma coisinha antes que vire correria: semana que vem a
terapia e a reunião do projeto caíram no mesmo horário, quinta às 15h.
Quer que eu te ajude a ver qual das duas mexer?

**🧠 anotado:** conflito é detectado por código (mesma data + mesma hora,
de hoje em diante), não por sorte do modelo. A decisão de qual mover é
DELA — a Giu prepara, nunca decide.

## Cena 3 — a véspera trabalha (o preparo leve)

**O retrato de véspera de exame:**
```
amanhã: Exame de sangue às 08:30 — a véspera é a hora do preparo leve:
algo a adiantar hoje?
```

**Giu:** Amanhã 8h30 tem o exame de sangue. Deixa eu já te poupar a manhã:
é em jejum, né? Se quiser eu te lembro hoje à noite de separar o pedido do
médico.

**🧠 anotado:** a véspera acorda sozinha no retrato — é o mesmo princípio
das datas queridas do Time Provider, agora para compromissos. O exame pode
virar missão (cuidador de saúde + vigia) até "realizado e resultado em mãos".

## Cena 4 — o que ela NÃO vê (garantias em teste)

- Agenda vazia = silêncio (o retrato não é formulário).
- Compromisso concluído sai do retrato na hora.
- A consulta da Nanda JAMAIS aparece no retrato da Nine.
- Montar o retrato não escreve nada no banco.
- O bloco antigo "AGENDA VIVA" do prompt foi ABSORVIDO (CP-2): a agenda
  entra UMA vez, pelo retrato — o prompt não incha.
- NENHUM Provider conhece fornecedor: a fronteira Open-Meteo/Google mora em
  integrations/ (Life Connectors) — travado por teste (dívida T7 paga).

---

**Portão da fundadora:** *"isso faz a Giulieta parecer mais uma boa
companhia ou apenas uma IA mais capaz?"* — Uma boa companhia é quem percebe
o dia cheio e pergunta "qual é A prioridade?", quem avisa do conflito antes
de doer, quem lembra da véspera do exame. Nenhuma dessas frases menciona
tecnologia; todas mencionam a vida dela.

## Limites conhecidos (registrados pela Life Architect — honestidade de escopo)

- **T9 (era C4):** conflito é detectado por igualdade exata de horário; 15:00
  e 15:30 "muito próximos" passam — janela real exige campo de duração, que
  herda a fila do campo `lugar` (T8). A linha afirma o conflito que viu,
  nunca a ausência de conflito.
- **C1 pago:** boa companhia sabe que horas são — o que já foi vivido hoje
  cala; dia CHEIO conta só o que ainda vem; conflito no passado não alarma.
- **C2 pago:** com Google conectado, o retrato declara o próprio limite
  ("confirme em ver_agenda") — a Giu nunca afirma "dia livre" sem conferir.
- **C5 (evolução):** pendências sem data só aparecem junto do dia — sozinhas,
  não acordam; a fricção "pendência que cobra da cabeça" tem casa melhor no
  Communication Provider (próximo da fila).
- **C7 (evolução):** compromisso de ontem não concluído sai do retrato (sem
  julgamento) e fica em ver_agenda; o "como foi?" retrospectivo com leveza é
  evolução, não regressão.

**Fase do Provider:** arquitetura ✅ → implementação ✅ → **validação em uso
real (Família Fundadora)** → evolução (Google Calendar já espelha a criação
de eventos; a leitura externa entra quando o OAuth do Despacho chegar).
