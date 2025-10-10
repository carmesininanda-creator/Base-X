# Arquitetura do Sistema de Paper Trading

## Visão Geral

O sistema de paper trading é projetado para executar estratégias quantitativas em tempo real, simulando operações no mercado sem utilizar capital real. O objetivo é validar a estratégia em condições reais de mercado antes de arriscar dinheiro.

## Componentes Principais

### 1. Módulo de Dados em Tempo Real (`src/live/`)

**Responsabilidade:** Coletar e processar dados de mercado em tempo real.

**Componentes:**
- `data_fetcher.py`: Conecta com APIs de dados (Yahoo Finance, B3, corretoras)
- `data_cache.py`: Cache local para otimizar requisições
- `data_validator.py`: Valida qualidade e integridade dos dados

**Funcionalidades:**
- Atualização periódica de preços (1-5 minutos)
- Histórico de preços intraday
- Indicadores técnicos em tempo real
- Detecção de anomalias nos dados

### 2. Motor de Sinais em Tempo Real (`src/live/`)

**Responsabilidade:** Gerar sinais de trading baseados na estratégia configurada.

**Componentes:**
- `signal_generator.py`: Aplica a lógica da estratégia aos dados atuais
- `rebalance_scheduler.py`: Agenda rebalanceamentos (diário, semanal, mensal)
- `signal_validator.py`: Valida sinais antes da execução

**Funcionalidades:**
- Cálculo de momentum em tempo real
- Ranking de ativos
- Geração de ordens de compra/venda
- Validação de sinais contra regras de risco

### 3. Simulador de Execução (`src/live/`)

**Responsabilidade:** Simular a execução de ordens no mercado.

**Componentes:**
- `order_simulator.py`: Simula preenchimento de ordens
- `slippage_model.py`: Modela derrapagem realista
- `cost_calculator.py`: Calcula custos de transação

**Funcionalidades:**
- Simulação de ordens a mercado e limitadas
- Modelagem de slippage baseada em liquidez
- Cálculo de custos (corretagem, emolumentos, impostos)
- Registro de todas as execuções

### 4. Gerenciador de Portfólio (`src/live/`)

**Responsabilidade:** Manter o estado atual do portfólio.

**Componentes:**
- `portfolio_manager.py`: Gerencia posições abertas e capital
- `position_tracker.py`: Rastreia cada posição individual
- `pnl_calculator.py`: Calcula P&L em tempo real

**Funcionalidades:**
- Registro de posições abertas
- Cálculo de P&L realizado e não realizado
- Valor total do portfólio
- Exposição por ativo e setor

### 5. Sistema de Persistência (`src/live/`)

**Responsabilidade:** Armazenar dados históricos e estado do sistema.

**Componentes:**
- `database.py`: Interface com SQLite/PostgreSQL
- `trade_logger.py`: Registra todas as operações
- `state_manager.py`: Salva e recupera estado do sistema

**Funcionalidades:**
- Banco de dados de trades
- Histórico de posições
- Snapshots diários do portfólio
- Logs de sistema

### 6. Gerenciador de Risco em Tempo Real (`src/live/`)

**Responsabilidade:** Monitorar e aplicar regras de risco.

**Componentes:**
- `risk_monitor.py`: Monitora métricas de risco continuamente
- `risk_enforcer.py`: Aplica limites e stop-losses
- `alert_manager.py`: Gera alertas de risco

**Funcionalidades:**
- Monitoramento de drawdown em tempo real
- Verificação de limites de posição
- Stop-loss automático
- Alertas por email/SMS

### 7. Dashboard de Monitoramento (`src/live/`)

**Responsabilidade:** Interface visual para acompanhamento.

**Componentes:**
- `live_dashboard.py`: Dashboard Streamlit em tempo real
- `performance_charts.py`: Gráficos de performance
- `position_viewer.py`: Visualização de posições

**Funcionalidades:**
- P&L do dia/semana/mês
- Posições abertas
- Histórico de trades
- Métricas de risco
- Gráficos interativos

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE PAPER TRADING                  │
└─────────────────────────────────────────────────────────────┘

1. COLETA DE DADOS
   ┌──────────────┐
   │ APIs Externas│
   │ (Yahoo, B3)  │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Data Fetcher │ ──► Cache Local
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Validação    │
   └──────┬───────┘
          │
          ▼

2. GERAÇÃO DE SINAIS
   ┌──────────────┐
   │ Dados        │
   │ Validados    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Cálculo de   │
   │ Momentum     │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Ranking de   │
   │ Ativos       │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Geração de   │
   │ Sinais       │
   └──────┬───────┘
          │
          ▼

3. VALIDAÇÃO DE RISCO
   ┌──────────────┐
   │ Sinais       │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Verificação  │
   │ de Limites   │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Aprovação    │
   │ de Ordens    │
   └──────┬───────┘
          │
          ▼

4. EXECUÇÃO SIMULADA
   ┌──────────────┐
   │ Ordens       │
   │ Aprovadas    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Simulação de │
   │ Preenchimento│
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Cálculo de   │
   │ Custos       │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Atualização  │
   │ do Portfólio │
   └──────┬───────┘
          │
          ▼

5. PERSISTÊNCIA E MONITORAMENTO
   ┌──────────────┐
   │ Registro em  │
   │ Banco de     │
   │ Dados        │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Dashboard    │
   │ em Tempo     │
   │ Real         │
   └──────────────┘
```

## Tecnologias Utilizadas

| Componente | Tecnologia | Justificativa |
|------------|-----------|---------------|
| **Linguagem** | Python 3.11 | Ecossistema rico, bibliotecas financeiras |
| **Dados** | yfinance, pandas | Acesso fácil a dados de mercado |
| **Banco de Dados** | SQLite / PostgreSQL | SQLite para desenvolvimento, PostgreSQL para produção |
| **Dashboard** | Streamlit | Rápido desenvolvimento, interativo |
| **Agendamento** | APScheduler | Tarefas periódicas em Python |
| **Logs** | Python logging | Rastreamento de eventos |
| **Notificações** | SMTP (email) | Alertas de risco |

## Configuração do Sistema

O sistema será configurado através de um arquivo YAML:

```yaml
paper_trading:
  # Configurações gerais
  mode: "paper"  # paper ou live
  initial_capital: 100000.0
  
  # Dados em tempo real
  data:
    update_interval: 300  # segundos (5 minutos)
    source: "yahoo"
    cache_enabled: true
  
  # Estratégia
  strategy:
    name: "momentum"
    lookback_period: 63
    top_n: 3
    bottom_n: 3
    rebalance_frequency: "monthly"
    rebalance_day: 1  # primeiro dia útil do mês
  
  # Gestão de risco
  risk:
    max_drawdown: 0.15
    max_position_size: 0.10
    stop_loss: 0.05
    max_leverage: 2.0
  
  # Execução
  execution:
    slippage_model: "percentage"
    slippage_value: 0.0001
    commission: 0.0005
  
  # Persistência
  database:
    type: "sqlite"
    path: "data/paper_trading.db"
  
  # Monitoramento
  monitoring:
    dashboard_enabled: true
    dashboard_port: 8502
    alerts_enabled: true
    alert_email: "nanda@example.com"
```

## Segurança e Confiabilidade

### Tratamento de Erros
- Todas as operações críticas têm try-except
- Logs detalhados de erros
- Fallback para dados em cache em caso de falha de API

### Validações
- Validação de dados antes de processar
- Validação de sinais antes de executar
- Verificação de sanidade do portfólio

### Backup
- Snapshots diários do estado do sistema
- Backup automático do banco de dados
- Logs rotativos com retenção de 30 dias

## Próximos Passos de Desenvolvimento

1. ✅ **Fase 1:** Arquitetura e planejamento (CONCLUÍDO)
2. ⏳ **Fase 2:** Módulo de dados em tempo real
3. ⏳ **Fase 3:** Motor de sinais
4. ⏳ **Fase 4:** Simulador de execução
5. ⏳ **Fase 5:** Sistema de persistência
6. ⏳ **Fase 6:** Dashboard de monitoramento
7. ⏳ **Fase 7:** Testes e validação
8. ⏳ **Fase 8:** Documentação e entrega

## Estimativa de Tempo

- **Desenvolvimento:** 2-3 semanas
- **Testes:** 1 semana
- **Ajustes:** 1 semana
- **Total:** 4-5 semanas

## Métricas de Sucesso

O sistema será considerado bem-sucedido se:

- ✅ Executar sem erros por 30 dias consecutivos
- ✅ Gerar sinais consistentes com a estratégia
- ✅ Simular execuções de forma realista
- ✅ Fornecer visibilidade completa do portfólio
- ✅ Alertar sobre violações de risco
- ✅ Manter histórico completo de operações
