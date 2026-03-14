# BazeX Care Bot - Telegram

Bot Telegram de monitoramento clinico para cuidadores, enfermeiros e supervisores. Tecnologia por tras da plataforma **Cuidar+**.

## Funcionalidades

- **Cadastro de pacientes** com ficha clinica completa (quarto, diagnostico, risco de queda, dieta, medicacao critica)
- **Checklist de cuidados** com 13 itens por turno (edicao em tempo real nos botoes)
- **Sinais vitais** (temperatura, saturacao, pressao, frequencia cardiaca, glicemia)
- **4 escalas clinicas** (dor, confusao mental, risco de queda, alimentacao)
- **10 tipos de intercorrencias** com alerta automatico
- **Motor de Risco Clinico 3 camadas**:
  - Camada 1: Score por regras clinicas (13 fatores de risco com pesos)
  - Camada 2: Tendencia individual (compara paciente com ele mesmo em 48h)
  - Camada 3: Protocolo automatico de acao (orienta o que fazer por nivel de risco)
- **Painel de supervisao** (/painel) com semaforo de risco e pacientes ordenados por criticidade
- **Protocolo Pos-Alta 72h** (/alta) com checklist de acompanhamento e lembretes automaticos
- **Passagem de plantao estruturada** ao encerrar turno
- **Trilha de auditoria** (quem registrou, quem foi alertado, quando)
- **4 roles**: Cuidador, Familia, Enfermeiro(a), Supervisor(a)
- **Cadeia de notificacao clinica**: Cuidador -> Enfermeira -> Supervisor -> Familia

## Comandos

| Comando | Descricao |
|---------|----------|
| `/start` | Iniciar bot e selecionar role |
| `/turno` | Iniciar turno com paciente |
| `/checklist` | Ver checklist de cuidados |
| `/sinais` | Registrar sinais vitais |
| `/escalas` | Registrar escalas clinicas |
| `/intercorrencia` | Registrar intercorrencia |
| `/observacao` | Adicionar observacao |
| `/painel` | Painel de supervisao (todos os pacientes) |
| `/risco` | Ver risco clinico do paciente ativo |
| `/timeline` | Linha do tempo clinica |
| `/alta` | Protocolo pos-alta 72h |
| `/plantao` | Selecionar paciente ativo |
| `/relatorio` | Gerar relatorio do turno |
| `/encerrar` | Encerrar turno |
| `/ajuda` | Lista de comandos |

## Configuracao

### Variaveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
BOT_TOKEN=seu_token_do_bot_telegram
```

Para obter o token, fale com o [@BotFather](https://t.me/BotFather) no Telegram.

### Instalacao Local

```bash
npm install
node index.js
```

## Deploy

### Railway (Recomendado)

1. Crie uma conta em [railway.app](https://railway.app)
2. Clique em "New Project" > "Deploy from GitHub repo"
3. Conecte o repositorio
4. Adicione a variavel de ambiente `BOT_TOKEN` nas Settings
5. Railway faz deploy automatico a cada push

**Plano Hobby ($5/mes)** roda 24/7 sem limite.

### Render

1. Crie uma conta em [render.com](https://render.com)
2. New > Background Worker > Connect GitHub repo
3. Runtime: Node
4. Build Command: `npm install`
5. Start Command: `node index.js`
6. Adicione `BOT_TOKEN` em Environment
7. Plano Starter ($7/mes) roda 24/7.

### VPS (DigitalOcean, AWS, etc.)

```bash
git clone https://github.com/seu-usuario/basexcare-bot.git
cd basexcare-bot
npm install
echo "BOT_TOKEN=seu_token" > .env

# Rodar com PM2 (recomendado para producao)
npm install -g pm2
pm2 start index.js --name basexcare-bot
pm2 save
pm2 startup
```

### Docker

```bash
docker build -t basexcare-bot .
docker run -d --name basexcare-bot -e BOT_TOKEN=seu_token -v $(pwd)/data.json:/app/data.json basexcare-bot
```

## Persistencia de Dados

Os dados sao salvos em `data.json`. Em ambientes de deploy:
- **Railway**: dados persistem entre deploys
- **Docker**: monte volume para `/app/data.json`
- **VPS**: dados persistem normalmente no disco

**Recomendacao para producao**: migrar para banco de dados (PostgreSQL/MongoDB).

## Stack

- **Node.js** 18+
- **Telegraf** 4.x (framework Telegram Bot)
- **node-cron** (lembretes automaticos)
- **Motor de Risco Clinico** proprietario (3 camadas)

## Bot

- **Nome:** BazeX Care
- **Username:** @BasexCareBot
- **Descricao:** Monitoramento clinico inteligente da Cuidar+

---

Desenvolvido como parte da plataforma **Cuidar+** | Tecnologia **BazeX Care**
