# 🎬 Demonstração — ⏰ Time Provider (nível 1: conversa anotada)

> Regra da demonstração (decisão da fundadora): todo cuidado novo entrega
> (1) a conversa completa anotada e (2) a aceitação real vivida. Este
> documento é o nível 1 — simulação fiel ao código. O nível 2 acontece com a
> **Família Fundadora**, na fase de validação em uso real.
>
> Pergunta da Fase 2 respondida aqui: **"Como o Time Provider ajuda a Nanda?"**

---

## Cena 1 — a data querida entra pela conversa (não por formulário)

**Nanda (quarta, 20h41):** amanhã nem me fala... tenho que resolver mil
coisas e sexta é aniversário da minha mãe, nem comprei nada

**🧠 anotado:** o retrato deu o AGORA (quarta-feira, inverno); a Friction
Lens viu DUAS fricções — a sobrecarga de amanhã (emocional/prática) e o
presente da mãe (relacional, com prazo). O Blueprint da Nanda manda: "o que
posso adiantar?", nunca mais uma cobrança. Nos bastidores: `anotar_data
("Aniversário da mãe dela", "MM-DD de sexta")` — invisível na conversa.

**Giu:** Sexta é da sua mãe, anotei aqui comigo 💛 Quer que eu te lembre
amanhã cedo de resolver o presente — ou prefere que eu já monte 2 ideias
simples pra você só escolher?

**🧠 anotado:** UMA oferta, 2 opções, decisão dela. A data agora vive no
perfil — quinta (véspera) e sexta (dia) o retrato "acorda" sozinho, sem
depender da janela de contexto.

## Cena 2 — a véspera acorda no retrato (quinta, 8h02, check-in normal)

**O que o cérebro recebe no turno, sem ninguém pedir:**
```
O MOMENTO DE AGORA (o retrato do momento — ...):
AGORA: quinta-feira, 10/07/2026 08:02 (fuso America/Sao_Paulo) — inverno
DATAS QUERIDAS (ela pediu para lembrar) — amanhã: Aniversário da mãe dela
— toque com carinho e no momento certo, nunca como notificação.
```

**Giu:** Bom dia, Nanda 💛 Antes do dia te engolir: amanhã é o dia da sua
mãe. Se quiser, deixo o lembrete do presente pra hora do almoço, que é
quando você respira.

**🧠 anotado:** a VÉSPERA é o cuidado real — no dia já é tarde para
presente. O tom vai junto com o dado (o retrato instrui "nunca como
notificação"). Se ela disser "já resolvi", o assunto MORRE — a lei da
oferta única (CP-1) vale para datas também.

## Cena 3 — a cidade é dela (opt-in explícito, e "esquece" é lei)

**Nanda:** que frio absurdo hoje em São Paulo, acordei congelando

**Giu:** Congelando é pouco... se você topar, eu passo a acompanhar o tempo
aí de São Paulo — daí consigo te avisar quando vier friagem assim. Só a
cidade, nada de localização — e você me pede pra esquecer quando quiser.

**Nanda:** pode sim

**🧠 anotado:** `definir_cidade("São Paulo")` — geocodifica uma vez, guarda
{nome, lat, lon} no perfil DELA. A partir daqui o retrato ganha a linha:
`Lá fora em São Paulo: 11°C, céu limpo (máx 18° / mín 9°); o sol se põe às
17h32.` Se ela disser "esquece minha cidade" → `city_clear` imediato e
determinístico. Se o serviço de clima cair ou demorar mais de 2,5s, a linha
simplesmente não aparece — a Nanda nunca vê um erro.

## Cena 4 — o que ela NÃO vê (as garantias em teste)

- O retrato do Ian não sabe que sexta é o dia da mãe da Nanda
  (confidencialidade — teste `nada_atravessa_membros`).
- Nenhum turno espera o clima: teto de 2,5s, cache de 30min, falha muda
  (testes `degrada_em_silencio`, `teto_por_snapshot`).
- Nenhuma palavra de sistema chega à conversa: "Open-Meteo", "API",
  "provider" são proibidos por teste (`lingua_de_vida`).
- O prompt não cresceu: o retrato SUBSTITUIU o antigo AGORA — um único
  `AGORA:` no prompt, orçamento global medido em teste (CP-2).

---

**Fase do Provider:** arquitetura ✅ → implementação ✅ → **validação em uso
real (aguarda a Família Fundadora)** → evolução. A pergunta de encerramento
("a vida ficou objetivamente melhor?") pertence à Life Architect, na fase 3.
