# 📚 Guia Completo do Sistema de Paper Trading

## 🎯 Visão Geral

Este sistema de paper trading permite que você teste estratégias quantitativas em tempo real **sem arriscar dinheiro real**. Todos os dados são reais, mas as operações são simuladas.

---

## 🚀 Como Usar

### 1. Iniciar o Sistema Principal

O sistema principal roda em background e executa as operações automaticamente:

```bash
cd ~/quant-fund-brazil
python3.11 src/live/paper_trading_system.py
```

**O que ele faz:**
- ✅ Coleta preços em tempo real a cada 5 minutos
- ✅ Calcula momentum dos ativos
- ✅ Gera sinais de compra/venda
- ✅ Executa ordens simuladas
- ✅ Rebalanceia mensalmente
- ✅ Salva tudo no banco de dados

**Para parar:** Pressione `Ctrl+C`

---

### 2. Abrir o Dashboard

Em outro terminal, inicie o dashboard de monitoramento:

```bash
cd ~/quant-fund-brazil
streamlit run src/live/dashboard/paper_trading_dashboard.py
```

**O dashboard mostra:**
- 💼 Valor do portfólio em tempo real
- 📈 Posições abertas
- 📋 Histórico de ordens
- 📊 Gráficos de performance
- 💰 P&L diário e total
- 📊 Estatísticas do sistema

**Acesso:** http://localhost:8501

---

## 📊 Componentes do Sistema

### 1. **Coleta de Dados em Tempo Real**
- Busca preços do Yahoo Finance
- Atualiza a cada 5 minutos
- Cache local para otimização
- Thread em background

### 2. **Motor de Sinais**
- Calcula momentum (retorno de 63 dias)
- Ranqueia ativos
- Gera sinais: BUY (top 3), SELL (bottom 3), HOLD (resto)

### 3. **Simulador de Execução**
- Simula preenchimento de ordens
- Aplica slippage realista (0.1%)
- Calcula corretagem (0.05%, mín R$ 3.33)
- Rastreia custos

### 4. **Banco de Dados**
- SQLite para persistência
- Armazena ordens, posições, snapshots
- Histórico completo
- Métricas de risco

### 5. **Dashboard Interativo**
- Streamlit para visualização
- Gráficos com Plotly
- Atualização em tempo real
- Controles do sistema

---

## ⚙️ Configuração

### Parâmetros Principais

Edite `src/live/paper_trading_system.py`:

```python
# Ativos para operar
TICKERS = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA',
    'ABEV3.SA', 'WEGE3.SA', 'RENT3.SA', 'GGBR4.SA'
]

# Capital inicial
initial_capital = 100000.0

# Período de lookback (dias)
lookback_period = 63

# Número de ativos para comprar/vender
top_n = 3
bottom_n = 3

# Frequência de rebalanceamento
rebalance_frequency = 'monthly'  # 'daily', 'weekly', 'monthly'

# Intervalo de atualização (segundos)
update_interval = 300  # 5 minutos
```

---

## 📈 Fluxo de Operação

### Dia Típico

**9:00 AM - Início do Mercado**
```
Sistema: Buscando preços de abertura...
Sistema: Atualizando histórico de preços...
```

**9:10 AM - Verificação de Rebalanceamento**
```
Sistema: Hoje é dia 1º do mês
Sistema: Iniciando rebalanceamento...
Sistema: Calculando momentum...
```

**9:15 AM - Geração de Sinais**
```
Sistema: VALE3.SA: +13.79% (TOP 1) → BUY
Sistema: BBDC4.SA: +10.12% (TOP 2) → BUY
Sistema: ITUB4.SA: +2.27% (TOP 3) → BUY
Sistema: ABEV3.SA: -4.26% (BOTTOM 3) → SELL
Sistema: PETR4.SA: -4.55% (BOTTOM 3) → SELL
```

**9:20 AM - Execução de Ordens**
```
Sistema: Comprando 173 ações de VALE3.SA
Sistema: Preço: R$ 65.13 (com slippage)
Sistema: Corretagem: R$ 3.33
Sistema: ✅ Ordem executada!
```

**14:35 PM - Atualização em Tempo Real**
```
Sistema: Atualizando preços...
Sistema: Atualizando posições...
Sistema: P&L do dia: +R$ 150,00
```

**18:00 PM - Fechamento**
```
Sistema: Mercado fechado
Sistema: Salvando snapshot diário...
Sistema: ✅ Snapshot salvo
```

---

## 💾 Estrutura do Banco de Dados

### Tabela: `orders`
```sql
- order_id: ID único da ordem
- ticker: Ticker do ativo
- side: BUY ou SELL
- quantity: Quantidade de ações
- price: Preço de referência
- filled_price: Preço de execução
- status: PENDING, FILLED, REJECTED, CANCELLED
- timestamp: Data/hora de criação
- filled_timestamp: Data/hora de execução
- commission: Corretagem paga
- slippage: Slippage aplicado
- total_cost: Custo total
```

### Tabela: `positions`
```sql
- ticker: Ticker do ativo
- quantity: Quantidade de ações
- avg_price: Preço médio de compra
- current_price: Preço atual
- unrealized_pnl: P&L não realizado
- timestamp: Última atualização
```

### Tabela: `daily_snapshots`
```sql
- date: Data do snapshot
- portfolio_value: Valor total do portfólio
- cash: Caixa disponível
- positions_value: Valor das posições
- daily_pnl: P&L do dia
- total_pnl: P&L total
- num_trades: Número de trades
- total_commission: Comissão total
```

---

## 🎯 Interpretação dos Resultados

### Métricas Principais

**Valor do Portfólio**
- Caixa + Valor das posições
- Deve crescer ao longo do tempo
- Comparar com capital inicial

**P&L Não Realizado**
- Lucro/prejuízo das posições abertas
- Ainda não foi realizado (posições não fechadas)
- Pode variar bastante

**P&L do Dia**
- Lucro/prejuízo do dia atual
- Inclui variação de preços
- Pode ser positivo ou negativo

**Número de Trades**
- Total de operações executadas
- Mais trades = mais custos
- Estratégia de momentum tem poucos trades (mensal)

### O que é um Bom Resultado?

**Excelente:**
- Retorno > 30% ao ano
- Sharpe Ratio > 2.0
- Max Drawdown < -10%

**Bom:**
- Retorno > 20% ao ano
- Sharpe Ratio > 1.5
- Max Drawdown < -15%

**Aceitável:**
- Retorno > 15% ao ano
- Sharpe Ratio > 1.0
- Max Drawdown < -20%

**Ruim:**
- Retorno < 10% ao ano
- Sharpe Ratio < 0.5
- Max Drawdown > -25%

---

## 🛡️ Gestão de Risco

### Limites Implementados

**Tamanho de Posição:**
- Máximo 20% do capital por ativo
- Diversificação forçada

**Alavancagem:**
- Máximo 1.5x do capital
- Proteção contra overtrading

**Stop-Loss:**
- Automático em -5% por posição
- Proteção contra grandes perdas

**Drawdown:**
- Alerta em -15%
- Pausa automática em -20%

---

## 🐛 Solução de Problemas

### Sistema não inicia

**Erro:** `ModuleNotFoundError`
```bash
# Instalar dependências
pip3 install -r requirements.txt
```

**Erro:** `Database is locked`
```bash
# Fechar outros processos usando o banco
pkill -f paper_trading_system
```

### Dashboard não abre

**Erro:** `Port 8501 already in use`
```bash
# Matar processo na porta
pkill -f streamlit
# Ou usar outra porta
streamlit run src/live/dashboard/paper_trading_dashboard.py --server.port 8502
```

### Dados não atualizam

**Problema:** Yahoo Finance pode ter limites de requisições

**Solução:**
- Aumentar `update_interval` para 600 (10 minutos)
- Reduzir número de tickers
- Aguardar alguns minutos

---

## 📊 Análise de Performance

### Exportar Dados

```python
from src.live.database.trading_db import TradingDatabase

db = TradingDatabase("data/paper_trading.db")

# Exportar ordens
orders = db.get_orders(limit=1000)
import pandas as pd
df = pd.DataFrame(orders)
df.to_csv("orders.csv", index=False)

# Exportar snapshots
snapshots = db.get_daily_snapshots(days=365)
df = pd.DataFrame(snapshots)
df.to_csv("performance.csv", index=False)
```

### Calcular Métricas

```python
import numpy as np

# Carregar snapshots
snapshots = db.get_daily_snapshots(days=365)
df = pd.DataFrame(snapshots)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Calcular retornos diários
df['returns'] = df['portfolio_value'].pct_change()

# Sharpe Ratio
sharpe = df['returns'].mean() / df['returns'].std() * np.sqrt(252)
print(f"Sharpe Ratio: {sharpe:.2f}")

# Max Drawdown
cummax = df['portfolio_value'].cummax()
drawdown = (df['portfolio_value'] - cummax) / cummax
max_dd = drawdown.min()
print(f"Max Drawdown: {max_dd:.2%}")

# Retorno total
total_return = (df['portfolio_value'].iloc[-1] / df['portfolio_value'].iloc[0]) - 1
print(f"Retorno Total: {total_return:.2%}")
```

---

## 🎯 Próximos Passos

### Após 2-4 Semanas de Paper Trading

**1. Análise de Resultados**
- Revisar performance
- Identificar padrões
- Verificar se está dentro do esperado

**2. Ajustes de Parâmetros**
- Testar diferentes lookback periods
- Ajustar top_n e bottom_n
- Experimentar frequências de rebalanceamento

**3. Validação**
- Comparar com backtest
- Verificar consistência
- Identificar divergências

**4. Decisão**
- Se resultados forem bons: preparar para trading real
- Se resultados forem ruins: revisar estratégia
- Se resultados forem inconsistentes: continuar testando

### Preparação para Trading Real

**1. Escolher Corretora**
- Interactive Brokers (recomendado)
- Configurar API
- Testar conexão

**2. Adaptar Sistema**
- Substituir `PaperExecutor` por `IBExecutor`
- Testar com capital mínimo (R$ 5.000)
- Monitorar intensivamente

**3. Escala Gradual**
- Semana 1: R$ 5.000
- Semana 2-3: R$ 12.500
- Mês 2: R$ 25.000
- Mês 3: R$ 50.000

---

## 💙 Suporte

**Desenvolvido por:** Manus para Nanda

**Contato:** Qualquer dúvida, é só chamar!

**Lembre-se:** Este é um sistema de **simulação**. Nenhum dinheiro real está sendo usado. Use este período para aprender, testar e ganhar confiança antes de operar com capital real.

---

## 📝 Checklist de Validação

Antes de ir para trading real, certifique-se de que:

- [ ] Sistema rodou por pelo menos 2 semanas sem erros
- [ ] Performance está dentro do esperado (>15% anualizado)
- [ ] Sharpe Ratio > 1.0
- [ ] Max Drawdown < -20%
- [ ] Você entende como o sistema funciona
- [ ] Você sabe interpretar os sinais
- [ ] Você está confortável com a volatilidade
- [ ] Você tem capital que pode arriscar
- [ ] Você tem conta em corretora com API
- [ ] Você está preparada psicologicamente

**Todos os itens precisam estar ✅ antes de começar com dinheiro real!**

