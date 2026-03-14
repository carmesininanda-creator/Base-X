# Deploy BazeX Care Bot no Railway — Guia Completo

Este guia detalha o processo passo a passo para hospedar o bot Telegram BazeX Care no Railway, garantindo operacao 24/7 com persistencia de dados.

## Pre-requisitos

Antes de comecar, certifique-se de ter:

| Item | Descricao |
|------|-----------|
| Conta GitHub | Para hospedar o codigo do bot |
| Conta Railway | Cadastro gratuito em [railway.app](https://railway.app) |
| Token do Bot | Obtido via [@BotFather](https://t.me/BotFather) no Telegram |
| Cartao de credito | Railway exige para o plano Hobby ($5/mes) |

## Passo 1 — Criar repositorio no GitHub

O Railway faz deploy a partir de um repositorio GitHub. Suba o codigo do bot para um repositorio privado.

```bash
# Na pasta do bot
cd basexcare-bot

# Inicializar git (se ainda nao tem)
git init
git add .
git commit -m "BazeX Care Bot v2 — Motor de Risco Clinico"

# Criar repositorio no GitHub (privado)
gh repo create basexcare-bot --private --source=. --push
```

**Arquivos que devem estar no repositorio:**

| Arquivo | Funcao |
|---------|--------|
| `index.js` | Codigo principal do bot (3400+ linhas) |
| `package.json` | Dependencias (telegraf, node-cron, dotenv) |
| `Dockerfile` | Configuracao Docker para o Railway |
| `data.json` | Banco de dados inicial (pode ser `{}`) |
| `.env.example` | Exemplo de variaveis de ambiente |
| `README.md` | Documentacao do bot |

**Importante:** Nunca suba o arquivo `.env` com o token real para o GitHub. Use `.gitignore`:

```bash
echo ".env" >> .gitignore
echo "node_modules/" >> .gitignore
```

## Passo 2 — Criar projeto no Railway

1. Acesse [railway.app](https://railway.app) e faca login com sua conta GitHub.

2. Clique em **"New Project"** no dashboard.

3. Selecione **"Deploy from GitHub repo"**.

4. Autorize o Railway a acessar seus repositorios (se ainda nao fez).

5. Selecione o repositorio **basexcare-bot**.

6. O Railway detectara automaticamente o `Dockerfile` e iniciara o build.

## Passo 3 — Configurar variaveis de ambiente

Antes do bot funcionar, voce precisa configurar o token do Telegram.

1. No projeto Railway, clique no servico do bot.

2. Va na aba **"Variables"**.

3. Adicione a seguinte variavel:

| Variavel | Valor |
|----------|-------|
| `BOT_TOKEN` | `8633651730:AAHnjRPM4gs6Q2XcXoTgjlSqLM-ceu3eYQQ` |

4. Clique em **"Add"** e o Railway fara redeploy automaticamente.

## Passo 4 — Verificar o deploy

Apos o deploy, verifique se o bot esta rodando:

1. Na aba **"Deployments"**, o status deve ser **"Active"** (verde).

2. Clique em **"View Logs"** para ver os logs do bot. Voce deve ver:

```
🚀 Iniciando BazeX Care Bot...
📊 Dados: X pacientes, Y cuidadores, Z familias
✅ BazeX Care Bot ativo! @BasexCareBot — aguardando mensagens...
```

3. Abra o Telegram e envie `/start` para `@BasexCareBot`. O bot deve responder.

## Passo 5 — Configurar persistencia de dados

O Railway usa um sistema de arquivos efemero por padrao. Para persistir o `data.json` entre deploys, voce tem duas opcoes:

### Opcao A: Volume persistente (Recomendado)

1. No servico do bot, va em **"Settings"** > **"Volumes"**.

2. Clique em **"Add Volume"**.

3. Configure:

| Campo | Valor |
|-------|-------|
| Mount Path | `/app/data` |
| Size | 1 GB (suficiente para milhares de pacientes) |

4. Atualize o codigo para usar o volume. No `index.js`, altere a linha do `DB_PATH`:

```javascript
const DB_PATH = process.env.DATA_PATH || path.join(__dirname, "data.json");
```

5. Adicione a variavel de ambiente:

| Variavel | Valor |
|----------|-------|
| `DATA_PATH` | `/app/data/data.json` |

### Opcao B: Backup periodico (Alternativa simples)

Se preferir nao usar volumes, o bot ja salva dados no `data.json` local. Os dados persistem entre restarts, mas sao perdidos em redeploys. Para mitigar:

- Faca backup do `data.json` periodicamente.
- Considere migrar para PostgreSQL no futuro (Railway oferece banco gratis no plano Hobby).

## Passo 6 — Configurar dominio customizado (Opcional)

Se quiser expor uma API HTTP (para o app movel acessar os dados do bot):

1. Va em **"Settings"** > **"Networking"**.

2. Clique em **"Generate Domain"** para obter um dominio `.railway.app`.

3. Ou adicione um dominio customizado (ex: `api.cuidarplus.com.br`).

## Custos

| Plano | Preco | Recursos |
|-------|-------|----------|
| **Hobby** | $5/mes | 8 GB RAM, 8 vCPU, 100 GB disco, execucao 24/7 |
| **Pro** | $20/mes | Recursos maiores, SLA, suporte prioritario |

O plano **Hobby ($5/mes)** e mais que suficiente para o bot BazeX Care em producao.

## Monitoramento

### Logs em tempo real

No dashboard do Railway, clique no servico e va em **"Logs"** para ver os logs em tempo real do bot.

### Alertas de saude

O `Dockerfile` inclui um `HEALTHCHECK` que verifica se o processo Node.js esta rodando. O Railway reinicia automaticamente se o health check falhar.

### Metricas

Na aba **"Metrics"**, voce pode ver:
- Uso de CPU
- Uso de memoria
- Uso de disco
- Trafego de rede

## Atualizacoes

Para atualizar o bot:

```bash
# Faca as alteracoes no codigo
git add .
git commit -m "Descricao da alteracao"
git push
```

O Railway faz **deploy automatico** a cada push no branch principal. O bot reinicia com zero downtime.

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| Bot nao responde | Verifique os logs. Confirme que `BOT_TOKEN` esta correto nas variaveis. |
| Deploy falha | Verifique se `package.json` e `Dockerfile` estao no repositorio. |
| Dados perdidos | Configure um volume persistente (Passo 5, Opcao A). |
| Bot duplicado | Certifique-se de que nao ha outra instancia rodando (sandbox, VPS, etc.). Pare a instancia local antes de fazer deploy. |
| Erro 409 Conflict | Significa que duas instancias do bot estao rodando. Pare a instancia local. |

## Proximos passos

Apos o deploy bem-sucedido:

1. **Pare o bot local** (sandbox) para evitar conflito de instancias.
2. **Teste todos os comandos** no Telegram.
3. **Configure backups** do `data.json` (ou migre para PostgreSQL).
4. **Monitore os logs** nos primeiros dias para garantir estabilidade.

---

**Cuidar+** | Tecnologia **BazeX Care** | Deploy Railway
