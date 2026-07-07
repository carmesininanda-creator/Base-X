# 🎬 Demonstração — Conector Google Calendar por pessoa (PR #18)

> Regra da fundadora: todo conector novo vem acompanhado de demonstração em
> conversa real. Esta é a demonstração FIEL AO CÓDIGO da main `c66e5c5` —
> cada fala da Giu segue as diretrizes reais do cérebro; cada bastidor é uma
> chamada real de ferramenta/conector. Em produção, este é o roteiro de
> aceitação: o conector só é "concluído" quando a Nanda viver esta conversa
> de verdade, sem ajuda técnica.

**Legenda:** 🗣️ conversa (tudo que a pessoa vê) · ⚙️ bastidor (o que a Base-X
faz em silêncio — invisível para a família)

---

**TERÇA ANTERIOR, 9h15**

🗣️ **Nanda:** giu, marca a consulta da mamãe na terça às 15h

⚙️ *Base-X: Friction Lens → fricção prática real (domínio: saúde). Life Radar → pedido explícito = missão. Blueprint da Nanda → direto, sem rodeios, tirar da cabeça. `abrir_missao(objetivo="Consulta da mãe da Nanda — terça 15h", criterio_conclusao="consulta realizada", proximo_passo="agendar")` → `agendar(titulo="Consulta da mãe", data=..., hora="15:00")` → ação pendente #12 criada (propõe→confirma→executa).*

🗣️ **Giu:** Deixa comigo. Consulta da sua mãe, terça agora, dia 14, às 15h — fecho assim?

🗣️ **Nanda:** fecha

⚙️ *`confirmar_acao(12)` → executor: `google_calendar.is_configured(nanda)` = **False** (ela ainda não conectou a agenda) → cadeia cai para o interno: Agenda Viva. Evento salvo internamente.*

🗣️ **Giu:** Marcado — tá guardado comigo, e eu te lembro na véspera. Ah, e se você quiser, isso pode ir direto pra SUA agenda do celular também — eu consigo me conectar com ela, se você topar. Quer?

🗣️ **Nanda:** quero

⚙️ *`conectar_agenda()` → `oauth_state_new(nanda)` (estado de uso único, 15 min) → link de consentimento gerado. A Giu explica o que passa a ver — instrução D2.*

🗣️ **Giu:** Então é só abrir este link e autorizar — leva uns 20 segundos:
🗣️ https://accounts.google.com/o/oauth2/…
🗣️ Só pra você saber: com isso eu passo a ver e criar **só os eventos da sua agenda** — nada além, nem e-mail, nem contatos. A chave fica guardada aqui com a família, e some na hora se você disser "desconecta minha agenda".

*(Nanda toca no link, autoriza na tela do Google e vê:)*
> **"Prontinho! Sua agenda está conectada. Pode voltar pra conversa com a Giu. 💛"**

⚙️ *Callback: estado validado e CONSUMIDO (anti-replay) → refresh token guardado no perfil DA Nanda → daqui em diante, `_calendar_id_for(nanda)` = a agenda principal DELA.*

🗣️ **Nanda:** pronto

⚙️ *`google_calendar.create_event("Consulta da mãe", terça, "15:00", user_id=nanda)` → evento criado NA AGENDA DELA. `atualizar_missao(#12, nota="evento na agenda do celular", proximo_passo="lembrar na véspera", estado="em_andamento")`.*

🗣️ **Giu:** Conectou! E a consulta da sua mãe já tá lá na sua agenda, terça às 15h. Pode tirar da cabeça.

---

**SEGUNDA (véspera), 18h30**

⚙️ *Lembrete interno vence → entrega pelo WhatsApp (conector real do canal).*

🗣️ **Giu:** ✦ Lembrete: consulta da sua mãe amanhã às 15h. Precisa que eu te ajude a separar alguma coisa — exames, documentos?

🗣️ **Nanda:** ai, os exames! o de sangue tá na pasta azul, me lembra de pegar

⚙️ *`atualizar_missao(#12, nota="levar exame de sangue — pasta azul", proximo_passo="lembrar da pasta azul amanhã cedo")` → `criar_lembrete("pegar a pasta azul com o exame", amanhã 13h)` → confirmado.*

🗣️ **Giu:** Anotado — amanhã às 13h eu te lembro da pasta azul. Boa noite pra vocês 💛

---

**TERÇA, 13h00** — 🗣️ **Giu:** ✦ Lembrete: a pasta azul com o exame de sangue — pra consulta das 15h.

🗣️ **Nanda:** peguei! saindo daqui a pouco

🗣️ **Giu:** Boa consulta pra ela. Tô aqui.

---

**TERÇA, 19h40**

⚙️ *Missão #12 segue viva no prompt de todo turno (sobrevive a qualquer conversa no meio). A Nanda manda mensagem sobre outro assunto; ao final, o Vigia puxa o fio com naturalidade.*

🗣️ **Nanda:** giu, anota que quinta tem reunião da escola

🗣️ **Giu:** Anoto sim — quinta, reunião da escola. Quer horário? … E me conta: como foi a consulta da sua mãe hoje?

🗣️ **Nanda:** foi bem! a médica ajustou o remédio dela, já saímos com a receita

⚙️ *`concluir_missao(#12, resultado="consulta realizada; medicação ajustada; receita em mãos")` — critério de conclusão ATINGIDO (realizada, não só marcada). Missão sai das vivas → entra em "aguardando a pergunta de VIDA" (por até 7 dias).*

🗣️ **Giu:** Que bom que correu bem 💛 Receita em mãos e remédio ajustado — cuidado completo. Se quiser, eu guardo o horário novo do remédio dela pra te lembrar.

---

**QUINTA, 21h10** *(dois dias depois, num momento leve)*

⚙️ *Seção "concluídas aguardando a pergunta de vida" no prompt → a Giu verifica com naturalidade, nunca como pesquisa de satisfação.*

🗣️ **Giu:** Nanda… aquela semana da consulta da sua mãe — sinto que foi uma coisa a menos na sua cabeça. Foi mesmo, ou eu que acho?

🗣️ **Nanda:** foi demais. nem pensei nisso a semana toda, só apareci lá

⚙️ *`atualizar_missao(#12, nota="VIDA: 'nem pensei nisso a semana toda, só apareci lá' — carga saiu de verdade")` → o ciclo COMPLETO fechou: fala → missão → conexão autorizada → evento real → lembretes → consulta acontecida → vida medida. Material da Life Architect.*

🗣️ **Giu:** Então valeu a pena. É pra isso que eu tô aqui.

---

## O que esta conversa demonstra (checklist da regra)

| Exigência da fundadora | Onde aparece |
|---|---|
| Conversa natural, sem comando/menu | todos os turnos |
| Pedir autorização (opt-in, nunca imposto) | "se você topar… Quer?" + link |
| Dizer o que passa a ver (D2) | "só os eventos da sua agenda — nada além" |
| Conectar | callback "Prontinho!" |
| Criar o evento NA agenda dela (D1: nunca na global) | ⚙️ `user_id=nanda` → agenda principal DELA |
| Acompanhar (Vigia, missão viva além da janela) | véspera, pasta azul, 13h |
| Perguntar como foi DEPOIS | "como foi a consulta da sua mãe hoje?" |
| Medir a vida ("VIDA:") | quinta, 21h10 |
| Base-X invisível (nunca "módulo", "conector", "missão") | em nenhum turno a máquina aparece |
| Saída ensinada na entrada | "some na hora se você disser 'desconecta minha agenda'" |

**Aceitação real (o critério continua sendo o da fundadora):** esta mesma
conversa, vivida por ela no WhatsApp, sem ajuda técnica — após o Despacho
provisionar o OAuth (BRIEFING §6).
