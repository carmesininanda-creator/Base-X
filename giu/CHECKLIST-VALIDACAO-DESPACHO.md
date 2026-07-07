# ✅ Checklist de Validação Operacional — Despacho (pós-merge, pré-Primeira Semana)

> Executar APÓS os merges do PR #9 e do PR #10, nesta ordem. Só liberar a
> família quando TUDO estiver verde. Objetivo maior: **proteger o primeiro
> contato** — a abertura personalizada de cada membro só dispara uma vez.

`BASE = https://base-x-production.up.railway.app`

---

## 0. Pré-deploy

- [ ] PR **#9** mergeado na `main` (bloqueadores).
- [ ] PR **#10** mergeado na `main` (voz + persona + primeiro encontro + posicionamento).
- [ ] `main` contém os commits: `38a906c` (voz/preferência), `9767a0d` (welcomes), `572e8e2` (posicionamento).

## 1. Redeploy no Railway

- [ ] Se o serviço tem auto-deploy da `main`: confirmar que o deploy novo subiu após o merge. Senão: redeploy manual no painel.
- [ ] **Logs de inicialização limpos**: sem `ERROR Configuração:` (o servidor ABORTA se `GIU_FAMILY_MODE=1` sem `GIU_API_TOKEN`). Warnings de canais não configurados são aceitáveis se esperados.
- [ ] **Nenhuma variável de ambiente NOVA é necessária.** Conferir as existentes:
  `OPENAI_API_KEY`, `GIU_API_TOKEN`, `GIU_FAMILY_MODE=1`, `WHATSAPP_TOKEN`,
  `WHATSAPP_PHONE_ID`, `WHATSAPP_VERIFY_TOKEN`, `META_APP_SECRET`.
  Voz: os padrões já valem (`GIU_VOICE_ENABLED=1`, `shimmer`, `0.92`).

## 2. Aplicação online

```bash
curl -s $BASE/
# Esperado: {"giu":"online", ..., "modo_familia": true, "canais": {"whatsapp": true, ...}}
```
- [ ] `modo_familia: true` e `canais.whatsapp: true`.

**Marcador de que o código novo está no ar** (rota criada no PR #9):
```bash
curl -s $BASE/openapi.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('delete' in d['paths']['/memories/{user_id}'])"
# Esperado: True  (se False → ainda é a versão antiga; redeploy não pegou)
```
- [ ] `True`.

## 3. Webhook do WhatsApp

```bash
curl -s "$BASE/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=<VERIFY_TOKEN>&hub.challenge=ping"
# Esperado: "ping"
```
- [ ] Handshake responde o challenge.
- [ ] No painel da Meta: webhook verificado, campo `messages` assinado.

## 4. Cadastro dos 4 membros (a ordem protege o primeiro contato)

**SEM o campo `welcome`** — a abertura do Blueprint entra sozinha pelo nome.
Nomes aceitos: `Nanda`, `Ian`, `Pauline` (ou `Nine`), `Rafael` (ou `Rafa`).

```bash
curl -s -X POST $BASE/family/members -H "Authorization: Bearer <GIU_API_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"<numero>", "name":"Ian", "emergency_contact":"<numero da Nanda>"}'
# Resposta traz "token": guardar AGORA — não é mostrado de novo.
```
- [ ] 4 membros cadastrados (Nanda como `"role":"admin"`).
- [ ] Os 4 tokens pessoais guardados com segurança (um por pessoa).
- [ ] `GET /family/members` (token de operadora) lista 4, **sem** campo de token.

⚠️ **Se algum membro já conversou com a versão antiga** (histórico > 0), a
abertura personalizada NÃO vai disparar para ele. Verificação e correção só a
pedido da própria pessoa: `DELETE $BASE/memories/<numero>` com o **token pessoal
dela** (apaga tudo e recomeça do zero, onboarding incluso).

## 5. E2E de fumaça — com um MEMBRO DE TESTE (nunca com a família)

Cadastrar um membro `"name":"Teste"` com o número do Despacho (nome fora do
piloto = sem abertura de Blueprint; não queima nada):

- [ ] **Portaria:** mandar "oi" de um número NÃO cadastrado → recebe recusa educada, e nada é salvo.
- [ ] **Texto:** membro Teste manda "oi" → Giu responde por texto (onboarding genérico: nome → pendência → consentimento).
- [ ] **Memória:** contar um fato ("gosto de café") → perguntar depois "o que você sabe sobre mim?" → o fato volta.
- [ ] **Voz (entrada):** mandar um áudio → Giu entende e responde **texto + áudio** (nota de voz).
- [ ] **Preferência:** dizer "me responde só por escrito" → mandar OUTRO áudio → resposta vem **só texto** (determinístico).
- [ ] **Voz degradada:** áudio incompreensível (ruído) → aviso gentil convidando a repetir por voz (nunca só "escreva").
- [ ] **Isolamento:** com o token do Teste, `GET /memories/<outro user_id>` → **403**. Com token de operadora → **403** também.
- [ ] **Limpeza:** `DELETE /memories/<numero do Teste>` (token pessoal) + `DELETE /family/members/<numero do Teste>` (operadora).

## 6. Comportamentos de identidade (verificados por código — evidência local)

Estes NÃO são testáveis por curl (vivem no prompt), e já estão cobertos pela
suíte E2E (42/42 na branch mergeada): onboarding personalizado por Blueprint,
"Ponte, não destino" em qualquer canal, Promessa 8 (nunca prometer função que
não existe), direito ao silêncio, pequenas lembranças. A validação HUMANA deles
é o próprio piloto (PROTOCOLO-PRIMEIRA-SEMANA.md).

## 7. Go / No-Go

- [ ] Tudo acima verde → avisar a Nanda: **pronta para a Primeira Semana**.
- [ ] Nanda envia o convite aos 4 (texto neutro no protocolo, §1).
- [ ] Até lá: **ninguém da família usa o número** — o primeiro contato é único.

## Riscos remanescentes conhecidos (não bloqueiam; registrados)

1. Check-ins proativos 2×/dia sem sinal de saturação (observar no piloto — sonda §3.6 do protocolo).
2. Read-back de ação sensível por voz é diretriz, não gate determinístico (P-VOZ-3, próxima leva).
3. STT+TTS caindo juntos → fallback só em texto naquele momento (outage correlacionado da OpenAI).
4. Oferta de preferência de voz dispara uma única vez (se o turno falhar, a pessoa ainda pode pedir em linguagem natural).
