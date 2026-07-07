# 📦 Briefing — Despacho (infraestrutura · deploy · operação)

> Modo Agente (fluxo único): leia o `DIARIO-EQUIPE.md` antes de agir e
> registre lá o resultado de cada item. Sua faixa: infraestrutura, deploy,
> integrações, operação, validação em produção.

## Missão imediata: colocar a Giulieta completa no ar e liberar o piloto

A `main` (`9933b97`) contém a Giulieta inteira: voz como preferência de
relacionamento, primeiro encontro por Blueprint, Blueprints no cérebro
(garantia arquitetural), identidade semeada, falha honesta nos 3 canais e o
Friction Lens. **46/46 testes E2E.** Sequência exata:

### 1. Causa raiz do incidente (H1 — PENDÊNCIA CRÍTICA)
O incidente (STT + TTS + cérebro mudos ao mesmo tempo) foi resolvido sem a
causa nomeada. Sem ela, pode voltar NO MEIO da Primeira Semana.
- Rode `python giu/diagnostico_openai.py` **no ambiente do Railway** (shell do
  serviço, ou `railway run`). Ele testa: formato da chave → biblioteca → rede
  → autenticação → cérebro → TTS → STT. Não expõe segredos.
- Cole a saída no `DIARIO-EQUIPE.md` (seção 3).
- Se a causa foi **billing/crédito da OpenAI**: configure alerta de saldo AGORA
  (painel OpenAI → Usage limits) — a família não pode encontrar a Giu muda.

### 2. Redeploy da `main`
- Auto-deploy ou manual no painel. Logs de subida limpos (sem `ERROR Configuração:`).
- **Marcador de versão** (prova que o código novo está no ar):
  ```bash
  curl -s $BASE/openapi.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('delete' in d['paths']['/memories/{user_id}'])"
  # True = main nova. False = redeploy não pegou.
  ```
- Nenhuma variável de ambiente NOVA é necessária.

### 3. Recadastro dos 4 membros (semeia identidade + Blueprints + boas-vindas)
Mesmo `POST /family/members` com token de operadora, **SEM o campo `welcome`**:
- Nomes aceitos: `Nanda` (role `admin`), `Ian`, `Pauline` (ou `Nine`), `Rafael` (ou `Rafa`).
- **O token pessoal de cada um NÃO muda** no recadastro — ignore o token que a
  resposta do re-POST exibe (o válido é o original).
- Efeito: a Giu nasce sabendo o apelido de cada um (não pergunta o nome), com
  o Blueprint no cérebro e a abertura personalizada pronta.

### 4. Validação (CHECKLIST-VALIDACAO-DESPACHO.md — completo)
Fumaça SEMPRE com membro `"Teste"` (nunca com a família; limpe depois).
Destaque para o **ciclo de voz (H2 — bloqueador do piloto, decisão da Nanda):**
1. Mandar áudio → ela entende e responde **áudio + texto**;
2. Dizer "me responde só por escrito" → mandar OUTRO áudio → resposta **só texto**;
3. Áudio incompreensível → convite gentil para repetir por voz (nunca só "escreva").

### 5. Reportar
Atualize o `DIARIO-EQUIPE.md`: H1 (causa raiz nomeada), H2 (ciclo de voz ✅/❌
com evidência), H4/H5 (deploy + validação). **Só a Nanda dá o go do piloto** —
seu papel termina em "tudo verde, evidências no diário".

## Regras da casa (não negociáveis)
- Ninguém da família usa o número até o go da Nanda (o primeiro contato é único).
- Logs jamais contêm conteúdo de conversa (só metadados) — se vir conteúdo em
  log, é bug: registre no diário e avise o Code imediatamente.
- Problema encontrado → diário primeiro, com o erro exato — o Code analisa se
  é código ou config antes de qualquer workaround.
