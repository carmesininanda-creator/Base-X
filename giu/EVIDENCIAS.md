# 🔬 Evidências — o diário de realidade da Giu

**Regra única deste documento: só entra o que foi OBSERVADO em conversa real.**
Hipóteses, ideias e teoria têm outros lugares. Aqui mora a realidade.

A partir de agora, **toda alteração na identidade da Giu (prompt, persona,
evals) deve citar uma linha deste arquivo como justificativa.** A Giu aprende
sobre as pessoas observando; nós aprendemos sobre a Giu do mesmo jeito.

## Como registrar (30 segundos)

Uma linha por observação. Sem conteúdo íntimo das conversas — registra-se o
**comportamento**, não o assunto. Quem registra: Nanda (relatos dos usuários
e os próprios) ou Claude (métricas e evals).

| Data | Pessoa | O que aconteceu (comportamento, não conteúdo) | Funcionou? | Princípio da tese |
|------|--------|-----------------------------------------------|------------|-------------------|
| _ex: 08/07_ | _Rafael_ | _Aceitou a sugestão de caminhar quando ela ofereceu DUAS opções de horário_ | ✅ | intencao-acao:respeitar-momento |
| _ex: 08/07_ | _Nine_ | _Ignorou lembrete longo; respondeu ao curto de uma linha_ | ⚠️ ajustar | carga:nunca-lista-grande |
| | | | | |

## Etiquetas de falha (do roteiro do piloto)

`[TOM]` frio/robótico/longo/julgou · `[LISTA]` despejou lista · `[MEMÓRIA]`
esqueceu ou lembrou errado · `[AÇÃO]` executou sem confirmar ou confirmou e
não executou · `[MOMENTO]` apareceu na hora errada

## O ciclo (como evidência vira evolução)

1. Observação entra aqui (tabela acima)
2. Padrão identificado (3+ observações do mesmo tipo) → vira proposta
3. Proposta → ajuste de prompt/eval **citando as linhas de evidência**
4. Eval roda antes e depois → sem regressão → PR pelo rito da governança
5. A mudança volta a ser observada. O ciclo recomeça.

## Princípios da tese sendo medidos (espelho do eval_persona.py)

`presenca:*` (acolher antes, desacelerar, ser-ouvida, sem-agenda) ·
`carga:*` (reduzir-antes, um-passo, nunca-lista-grande) ·
`intencao-acao:*` (encolher-passo, respeitar-momento, compreender-antes, vontade-e-dela) ·
`julgamento:*` (zero, repetir-e-ok, adiar-e-humano) ·
`consentimento:*` (propoe-confirma, preferencia-respeitada) ·
`honestidade:*` (admite-nao-saber, diferenca-sem-arrogancia, pergunta-nao-afirma)
