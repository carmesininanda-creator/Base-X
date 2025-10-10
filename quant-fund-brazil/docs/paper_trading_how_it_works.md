# Como Funciona o Paper Trading - Guia Completo

## 🎯 Visão Geral

O sistema de paper trading simula operações reais no mercado, mas **sem usar dinheiro real**. É como um videogame de trading: todas as regras são iguais ao mercado real, mas você não perde (nem ganha) dinheiro de verdade.

## 🚀 Iniciando o Sistema

### Passo 1: Configuração Inicial

Você vai configurar o sistema uma vez através de um arquivo de configuração:

```yaml
# config/paper_trading.yaml

capital_inicial: 100000  # R$ 100.000
tickers:
  - PETR4.SA
  - VALE3.SA
  - ITUB4.SA
  - BBDC4.SA
  - ABEV3.SA

estrategia:
  tipo: momentum
  lookback: 63  # 3 meses
  top_n: 3      # Comprar 3 melhores
  bottom_n: 3   # Vender 3 piores
  rebalancear: mensal  # Todo primeiro dia útil do mês

risco:
  max_drawdown: 15%
  max_posicao: 10%
  stop_loss: 5%
```

### Passo 2: Iniciar o Sistema

Você vai rodar um comando simples:

```bash
python -m src.live.main --mode paper
```

Ou clicar em um botão no dashboard:

```
┌──────────────────────────────────┐
│  🚀 Iniciar Paper Trading        │
└──────────────────────────────────┘
```

### O que acontece quando você inicia:

1. ✅ Sistema carrega as configurações
2. ✅ Conecta com as fontes de dados (Yahoo Finance)
3. ✅ Carrega o histórico de preços (últimos 3 meses)
4. ✅ Calcula o momentum inicial de todos os ativos
5. ✅ Cria o portfólio inicial (se for a primeira vez)
6. ✅ Inicia o monitoramento em tempo real

**Tempo:** 30 segundos a 1 minuto

---

## 📊 Funcionamento Diário

### Manhã (9:00 AM - Abertura do Mercado)

**O que o sistema faz automaticamente:**

1. **Coleta de Dados (9:00 - 9:05)**
   - Busca os preços de abertura de todos os ativos
   - Atualiza o cache local
   - Registra no banco de dados

2. **Atualização de Posições (9:05 - 9:10)**
   - Calcula o valor atual de cada posição
   - Atualiza o P&L (lucro/prejuízo)
   - Verifica alertas de risco

3. **Verificação de Rebalanceamento (9:10 - 9:15)**
   - Verifica se é dia de rebalanceamento (ex: primeiro dia útil do mês)
   - Se SIM: executa o processo de rebalanceamento (veja abaixo)
   - Se NÃO: continua monitorando

### Durante o Dia (9:00 - 18:00)

**A cada 5 minutos, o sistema:**

1. **Atualiza Preços**
   ```
   9:00 → Busca preços
   9:05 → Busca preços
   9:10 → Busca preços
   ...
   17:55 → Busca preços
   18:00 → Busca preços (fechamento)
   ```

2. **Recalcula Métricas**
   - Valor total do portfólio
   - P&L do dia
   - P&L total
   - Drawdown atual
   - Exposição por ativo

3. **Monitora Riscos**
   - Verifica se alguma posição ultrapassou o stop-loss
   - Verifica se o drawdown máximo foi atingido
   - Verifica se há concentração excessiva

4. **Atualiza Dashboard**
   - Gráficos em tempo real
   - Tabela de posições
   - Métricas de performance

### Tarde (18:00 - Fechamento do Mercado)

**O que o sistema faz:**

1. **Snapshot Diário (18:05)**
   - Salva o estado completo do portfólio
   - Registra todas as métricas do dia
   - Cria backup no banco de dados

2. **Relatório Diário (18:10)**
   - Gera resumo do dia
   - Calcula performance
   - Envia email (opcional)

---

## 🔄 Processo de Rebalanceamento

### Quando Acontece?

Por padrão, **no primeiro dia útil de cada mês** (configurável).

### Como Funciona?

#### Etapa 1: Cálculo de Momentum (9:10 - 9:15)

O sistema calcula o retorno de cada ativo nos últimos 63 dias:

```
PETR4.SA: +15.2% → Momentum alto
VALE3.SA: +12.8% → Momentum alto
ITUB4.SA: +8.5%  → Momentum médio
BBDC4.SA: +5.2%  → Momentum médio
ABEV3.SA: -2.1%  → Momentum baixo
```

#### Etapa 2: Ranking dos Ativos (9:15 - 9:16)

Ordena do melhor para o pior:

```
1. PETR4.SA: +15.2% ✅ TOP 3
2. VALE3.SA: +12.8% ✅ TOP 3
3. ITUB4.SA: +8.5%  ✅ TOP 3
4. BBDC4.SA: +5.2%
5. ABEV3.SA: -2.1%  ❌ BOTTOM 3
```

#### Etapa 3: Geração de Sinais (9:16 - 9:17)

**Comprar (Long):**
- PETR4.SA
- VALE3.SA
- ITUB4.SA

**Vender (Short):**
- ABEV3.SA

**Não fazer nada:**
- BBDC4.SA

#### Etapa 4: Cálculo de Tamanho de Posição (9:17 - 9:18)

Com R$ 100.000 de capital:

**Long (50% do capital):**
- PETR4.SA: R$ 16.666 (1/3 de 50%)
- VALE3.SA: R$ 16.666
- ITUB4.SA: R$ 16.666

**Short (50% do capital):**
- ABEV3.SA: R$ 16.666 (1/3 de 50%)

**Caixa:**
- R$ 33.334 (restante)

#### Etapa 5: Ajuste de Posições Existentes (9:18 - 9:20)

O sistema compara o portfólio atual com o desejado:

**Posições Atuais:**
```
PETR4.SA: R$ 10.000 → Precisa comprar R$ 6.666
VALE3.SA: R$ 0      → Precisa comprar R$ 16.666
ITUB4.SA: R$ 20.000 → Precisa vender R$ 3.334
BBDC4.SA: R$ 15.000 → Precisa vender R$ 15.000 (zerar)
ABEV3.SA: R$ 0      → Precisa vender R$ 16.666 (short)
```

#### Etapa 6: Geração de Ordens (9:20 - 9:21)

O sistema cria ordens de mercado:

```
ORDEM 1: COMPRAR PETR4.SA - R$ 6.666
ORDEM 2: COMPRAR VALE3.SA - R$ 16.666
ORDEM 3: VENDER ITUB4.SA - R$ 3.334
ORDEM 4: VENDER BBDC4.SA - R$ 15.000
ORDEM 5: VENDER ABEV3.SA - R$ 16.666 (short)
```

#### Etapa 7: Simulação de Execução (9:21 - 9:25)

Para cada ordem, o sistema simula a execução:

**Exemplo: ORDEM 1 - COMPRAR PETR4.SA - R$ 6.666**

1. **Preço de Mercado:** R$ 38.50
2. **Slippage (0.01%):** R$ 38.50 × 1.0001 = R$ 38.504
3. **Quantidade:** R$ 6.666 ÷ R$ 38.504 = 173 ações
4. **Valor Total:** 173 × R$ 38.504 = R$ 6.661,19
5. **Corretagem (0.05%):** R$ 6.661,19 × 0.0005 = R$ 3,33
6. **Custo Total:** R$ 6.661,19 + R$ 3,33 = R$ 6.664,52

**Registro:**
```
Data: 2025-11-01 09:23:15
Ticker: PETR4.SA
Tipo: COMPRA
Quantidade: 173 ações
Preço: R$ 38.504
Valor: R$ 6.661,19
Corretagem: R$ 3,33
Total: R$ 6.664,52
```

#### Etapa 8: Atualização do Portfólio (9:25 - 9:26)

O sistema atualiza todas as posições:

**Portfólio Atualizado:**
```
┌──────────────┬────────────┬──────────────┬──────────────┐
│ Ticker       │ Quantidade │ Preço Médio  │ Valor Atual  │
├──────────────┼────────────┼──────────────┼──────────────┤
│ PETR4.SA     │ 433        │ R$ 38.50     │ R$ 16.670,50 │
│ VALE3.SA     │ 255        │ R$ 65.20     │ R$ 16.626,00 │
│ ITUB4.SA     │ 550        │ R$ 30.30     │ R$ 16.665,00 │
│ ABEV3.SA     │ -1250      │ R$ 13.33     │ -R$ 16.662,50│
├──────────────┼────────────┼──────────────┼──────────────┤
│ TOTAL        │            │              │ R$ 33.299,00 │
│ CAIXA        │            │              │ R$ 66.701,00 │
│ PATRIMÔNIO   │            │              │ R$ 100.000,00│
└──────────────┴────────────┴──────────────┴──────────────┘
```

#### Etapa 9: Notificação (9:26)

O sistema envia um resumo:

```
📧 Email: Rebalanceamento Concluído

Olá Nanda,

O rebalanceamento mensal foi executado com sucesso!

Operações Realizadas:
✅ 5 ordens executadas
💰 Custos totais: R$ 83,30

Novo Portfólio:
• PETR4.SA: R$ 16.670,50 (16.7%)
• VALE3.SA: R$ 16.626,00 (16.6%)
• ITUB4.SA: R$ 16.665,00 (16.7%)
• ABEV3.SA: -R$ 16.662,50 (-16.7%) [SHORT]
• Caixa: R$ 66.701,00 (66.7%)

Performance Atual:
• Retorno Total: +2.5%
• Sharpe Ratio: 1.8
• Max Drawdown: -3.2%

Dashboard: http://localhost:8502
```

---

## 📱 Dashboard em Tempo Real

### O que você vê no dashboard:

#### Seção 1: Resumo Geral

```
┌─────────────────────────────────────────────────────┐
│  💼 PORTFÓLIO                                       │
├─────────────────────────────────────────────────────┤
│  Capital Inicial:     R$ 100.000,00                 │
│  Valor Atual:         R$ 102.500,00  (+2.5%)        │
│  P&L Total:           R$ 2.500,00                   │
│  P&L Hoje:            R$ 150,00      (+0.15%)       │
└─────────────────────────────────────────────────────┘
```

#### Seção 2: Posições Abertas

```
┌──────────────┬────────────┬──────────────┬──────────────┬──────────┐
│ Ticker       │ Qtd        │ Preço Médio  │ Preço Atual  │ P&L      │
├──────────────┼────────────┼──────────────┼──────────────┼──────────┤
│ PETR4.SA     │ 433        │ R$ 38.50     │ R$ 39.20     │ +R$ 303  │
│ VALE3.SA     │ 255        │ R$ 65.20     │ R$ 66.10     │ +R$ 230  │
│ ITUB4.SA     │ 550        │ R$ 30.30     │ R$ 30.50     │ +R$ 110  │
│ ABEV3.SA     │ -1250 (S)  │ R$ 13.33     │ R$ 13.20     │ +R$ 163  │
└──────────────┴────────────┴──────────────┴──────────────┴──────────┘

(S) = Short (posição vendida)
```

#### Seção 3: Gráfico de Equity

```
R$ 103k ┤                                              ╭─
        │                                         ╭────╯
R$ 102k ┤                                    ╭────╯
        │                               ╭────╯
R$ 101k ┤                          ╭────╯
        │                     ╭────╯
R$ 100k ┼─────────────────────╯
        │
R$ 99k  ┤
        └─────────────────────────────────────────────────
         Nov 1   Nov 8   Nov 15  Nov 22  Nov 29  Dez 6
```

#### Seção 4: Métricas de Risco

```
┌─────────────────────────────────────────────────────┐
│  🛡️ RISCO                                           │
├─────────────────────────────────────────────────────┤
│  Max Drawdown:        -3.2%  ✅ (limite: -15%)      │
│  Volatilidade:        12.5%                         │
│  VaR (95%):           -R$ 1.250                     │
│  Maior Posição:       16.7%  ✅ (limite: 20%)       │
│  Alavancagem:         0.33x  ✅ (limite: 2.0x)      │
└─────────────────────────────────────────────────────┘
```

#### Seção 5: Próximos Eventos

```
┌─────────────────────────────────────────────────────┐
│  📅 AGENDA                                          │
├─────────────────────────────────────────────────────┤
│  Próximo Rebalanceamento:  01/12/2025 (23 dias)    │
│  Última Atualização:       08/11/2025 14:35         │
│  Próxima Atualização:      08/11/2025 14:40         │
└─────────────────────────────────────────────────────┘
```

---

## 🚨 Sistema de Alertas

### Quando você recebe alertas:

#### Alerta 1: Drawdown Alto

```
⚠️ ALERTA DE RISCO

Drawdown atual: -12.5%
Limite configurado: -15%

Você está próximo do limite de drawdown.
Considere reduzir exposição ou revisar a estratégia.

Dashboard: http://localhost:8502
```

#### Alerta 2: Stop-Loss Atingido

```
🛑 STOP-LOSS ACIONADO

Posição: PETR4.SA
Perda: -5.2%
Limite: -5.0%

A posição foi automaticamente fechada para limitar perdas.

Detalhes no dashboard: http://localhost:8502
```

#### Alerta 3: Erro de Dados

```
❌ ERRO NO SISTEMA

Não foi possível atualizar preços de:
- ABEV3.SA
- B3SA3.SA

Usando último preço conhecido.
Verifique a conexão com a internet.
```

---

## 📊 Relatórios

### Relatório Diário (Todo dia às 18:10)

```
📈 RELATÓRIO DIÁRIO - 08/11/2025

Performance:
• P&L do Dia: +R$ 150,00 (+0.15%)
• P&L Acumulado: +R$ 2.500,00 (+2.50%)
• Melhor Ativo: PETR4.SA (+1.8%)
• Pior Ativo: ITUB4.SA (-0.3%)

Operações:
• Nenhuma operação hoje

Risco:
• Drawdown: -3.2%
• Volatilidade: 12.5%
• VaR: -R$ 1.250

Próximo Rebalanceamento: 01/12/2025
```

### Relatório Mensal (Todo dia 1º às 18:10)

```
📊 RELATÓRIO MENSAL - NOVEMBRO 2025

Performance:
• Retorno do Mês: +3.2%
• Retorno Acumulado: +8.5%
• Sharpe Ratio: 1.8
• Max Drawdown: -5.1%

Operações:
• Total de Trades: 8
• Trades Lucrativos: 6 (75%)
• Trades Perdedores: 2 (25%)
• Custos Totais: R$ 166,60

Melhores Ativos:
1. PETR4.SA: +12.5%
2. VALE3.SA: +8.3%
3. ITUB4.SA: +5.2%

Comparação com Benchmark:
• Ibovespa: +2.1%
• CDI: +0.9%
• Sua Estratégia: +3.2% ✅

Próximo Rebalanceamento: 01/12/2025
```

---

## 🔧 Manutenção e Controle

### Comandos Disponíveis

```bash
# Iniciar paper trading
python -m src.live.main --mode paper

# Parar paper trading
python -m src.live.main --stop

# Ver status
python -m src.live.main --status

# Forçar rebalanceamento
python -m src.live.main --rebalance

# Exportar histórico
python -m src.live.main --export trades.csv
```

### Painel de Controle no Dashboard

```
┌─────────────────────────────────────────────────────┐
│  ⚙️ CONTROLES                                       │
├─────────────────────────────────────────────────────┤
│  [ ⏸️ Pausar Sistema ]                              │
│  [ ▶️ Retomar Sistema ]                             │
│  [ 🔄 Forçar Rebalanceamento ]                      │
│  [ 📥 Exportar Dados ]                              │
│  [ ⚙️ Editar Configurações ]                        │
└─────────────────────────────────────────────────────┘
```

---

## 💡 Cenários de Uso

### Cenário 1: Tudo Correndo Bem

**Você:**
- Abre o dashboard uma vez por dia (5 minutos)
- Verifica o P&L e as posições
- Lê o email de relatório diário

**Sistema:**
- Roda 100% automaticamente
- Atualiza preços a cada 5 minutos
- Rebalanceia no dia agendado
- Envia alertas se necessário

**Resultado:** Você acompanha sem precisar fazer nada.

### Cenário 2: Drawdown Alto

**Sistema detecta:**
- Drawdown de -13% (próximo do limite de -15%)

**Sistema faz:**
- Envia alerta por email
- Destaca no dashboard em vermelho
- Sugere ações (reduzir exposição, pausar)

**Você decide:**
- Pausar o sistema temporariamente
- Ou ajustar os limites de risco
- Ou deixar continuar e monitorar

### Cenário 3: Erro de Dados

**Sistema detecta:**
- Falha ao buscar preços de 2 ativos

**Sistema faz:**
- Usa último preço conhecido
- Registra o erro no log
- Envia alerta

**Você faz:**
- Verifica a conexão
- Se persistir, contata suporte
- Sistema continua funcionando com dados em cache

---

## 🎯 Resumo: O que você precisa fazer

### Diariamente (5 minutos):
- ✅ Abrir o dashboard
- ✅ Verificar P&L e posições
- ✅ Ler alertas (se houver)

### Semanalmente (10 minutos):
- ✅ Revisar performance da semana
- ✅ Verificar se há padrões
- ✅ Ajustar configurações se necessário

### Mensalmente (30 minutos):
- ✅ Analisar relatório mensal
- ✅ Comparar com benchmark
- ✅ Decidir se continua ou ajusta estratégia

### O sistema faz TUDO automaticamente:
- ✅ Coleta de dados
- ✅ Cálculo de sinais
- ✅ Execução de ordens
- ✅ Gestão de risco
- ✅ Relatórios
- ✅ Alertas

---

## 🚀 Vantagens do Paper Trading

1. **Zero Risco Financeiro:** Você não perde dinheiro real
2. **Validação Real:** Testa em condições reais de mercado
3. **Aprendizado:** Entende como a estratégia se comporta
4. **Confiança:** Ganha confiança antes de arriscar capital
5. **Ajustes:** Pode ajustar parâmetros sem consequências
6. **Histórico:** Constrói um histórico de performance real

---

## ⏭️ Transição para Trading Real

Depois de 3-6 meses de paper trading bem-sucedido:

1. **Análise de Resultados**
   - Sharpe Ratio consistentemente > 1.5
   - Drawdown máximo aceitável
   - Performance superior ao benchmark

2. **Preparação**
   - Abrir conta em corretora com API
   - Configurar chaves de acesso
   - Testar conexão

3. **Início Gradual**
   - Começar com 10-20% do capital
   - Monitorar de perto por 1 mês
   - Aumentar gradualmente se tudo correr bem

4. **Operação Normal**
   - Sistema idêntico ao paper trading
   - Mas com ordens reais
   - Dinheiro real em jogo

---

**Pronto! Esse é o funcionamento completo do sistema de paper trading.** 🎉
