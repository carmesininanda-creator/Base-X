# Guia Completo do Dashboard Interativo

Este guia detalha todas as funcionalidades interativas do dashboard do fundo quantitativo, explicando como usar cada recurso e interpretar os resultados.

## Visão Geral da Interface

O dashboard está dividido em duas áreas principais:

1. **Barra Lateral Esquerda:** Configurações e controles
2. **Área Principal:** Resultados, gráficos e análises

---

## 📊 Barra Lateral: Configurações

### 1. Universo de Ativos

**O que é:** Lista de ações brasileiras que serão analisadas pela estratégia.

**Como usar:**
- Você verá uma caixa de texto com vários tickers (códigos de ações)
- Cada ticker deve estar em uma linha separada
- Formato correto: `PETR4.SA` (código da ação + `.SA` para B3)

**Exemplos de tickers populares:**
- `PETR4.SA` - Petrobras PN
- `VALE3.SA` - Vale ON
- `ITUB4.SA` - Itaú Unibanco PN
- `BBDC4.SA` - Bradesco PN
- `ABEV3.SA` - Ambev ON
- `B3SA3.SA` - B3 ON
- `WEGE3.SA` - WEG ON
- `RENT3.SA` - Localiza ON
- `GGBR4.SA` - Gerdau PN
- `SUZB3.SA` - Suzano ON

**Dica:** Quanto mais ativos você incluir, mais oportunidades a estratégia terá para selecionar os melhores, mas o processamento será mais demorado.

---

### 2. Período de Análise

**O que é:** O intervalo de tempo que será usado para o backtest histórico.

**Campos:**
- **Data Inicial:** Início do período de análise
- **Data Final:** Fim do período de análise (geralmente hoje)

**Como escolher:**
- **Período curto (6 meses - 1 ano):** Testa a estratégia em condições recentes de mercado
- **Período médio (2-3 anos):** Balanceia dados recentes com diferentes condições de mercado
- **Período longo (5+ anos):** Testa a robustez da estratégia em diversos ciclos econômicos

**Recomendação:** Comece com 2 anos (padrão) para ter uma boa amostra sem processar dados demais.

---

### 3. Estratégia de Momentum - Parâmetros

#### 3.1 Período de Lookback (20-126 dias)

**O que é:** Quantos dias no passado a estratégia olha para calcular o momentum (força) de cada ação.

**Como funciona:**
- A estratégia calcula o retorno de cada ação nos últimos X dias
- Ações com maior retorno = maior momentum = candidatas à compra
- Ações com menor retorno = menor momentum = candidatas à venda

**Valores sugeridos:**
- **20 dias (≈ 1 mês):** Momentum de curto prazo, mais volátil
- **63 dias (≈ 3 meses):** Momentum de médio prazo, equilibrado (padrão)
- **126 dias (≈ 6 meses):** Momentum de longo prazo, mais estável

**Dica:** O valor padrão de 63 dias é baseado em pesquisas acadêmicas que mostram bons resultados com momentum de 3 meses.

#### 3.2 Top N - Comprar (1-10)

**O que é:** Quantas ações com **maior momentum** (melhor desempenho) serão compradas.

**Como funciona:**
- A estratégia ranqueia todas as ações do universo
- Compra as N ações que mais subiram no período de lookback

**Exemplo com Top N = 3:**
- Se PETR4 subiu 15%, VALE3 subiu 12% e ITUB4 subiu 10%
- A estratégia comprará essas 3 ações

**Recomendação:** 
- **3-5 ações:** Boa diversificação sem diluir demais os resultados
- **1-2 ações:** Mais concentrado, maior risco e retorno potencial
- **7-10 ações:** Muito diversificado, resultados mais próximos do mercado

#### 3.3 Bottom N - Vender (1-10)

**O que é:** Quantas ações com **menor momentum** (pior desempenho) serão vendidas (operação short).

**Como funciona:**
- A estratégia identifica as N ações que mais caíram
- Vende essas ações "a descoberto" (apostando na continuação da queda)

**Importante:** Operações short são mais arriscadas e nem sempre permitidas para todos os investidores.

**Recomendação:** Mantenha o mesmo valor do Top N para uma estratégia equilibrada (long-short neutro).

---

### 4. Capital Inicial

**O que é:** Quanto dinheiro você começaria com no backtest.

**Valores:**
- Mínimo: R$ 10.000
- Máximo: R$ 10.000.000
- Padrão: R$ 100.000

**Como afeta os resultados:**
- O capital inicial **não afeta os retornos percentuais**
- Afeta apenas os valores absolutos (R$) de lucro/prejuízo
- Útil para simular cenários realistas do seu capital disponível

---

### 5. Botão "🚀 Executar Backtest"

**O que faz:** Inicia o processamento completo:
1. Baixa os dados históricos das ações
2. Calcula o momentum de cada ação
3. Gera sinais de compra e venda
4. Simula todas as operações
5. Calcula métricas de performance
6. Gera os gráficos

**Tempo de processamento:** 1-3 minutos (depende do número de ativos e período)

---

## 📈 Área Principal: Resultados

### 1. Métricas de Performance (Cards no Topo)

Após executar o backtest, você verá 4 cards principais:

#### Card 1: Retorno Total
**O que mostra:** Ganho ou perda percentual total do período.

**Exemplo:** `+25.50%` significa que o capital cresceu 25,50%

**Como interpretar:**
- ✅ **Positivo (verde):** A estratégia gerou lucro
- ❌ **Negativo (vermelho):** A estratégia gerou prejuízo
- Compare com o CDI ou Ibovespa no mesmo período

#### Card 2: Sharpe Ratio
**O que mostra:** Retorno ajustado ao risco.

**Como interpretar:**
- **< 0:** Estratégia perdeu dinheiro
- **0 a 1:** Retorno baixo para o risco assumido
- **1 a 2:** Bom retorno ajustado ao risco ✅
- **> 2:** Excelente retorno ajustado ao risco ⭐

**Importante:** Sharpe Ratio é mais importante que o retorno total! Uma estratégia com 20% de retorno e Sharpe 2.0 é melhor que uma com 30% de retorno e Sharpe 0.5.

#### Card 3: Max Drawdown
**O que mostra:** A maior perda de pico a vale durante o período.

**Exemplo:** `-12.30%` significa que em algum momento você perdeu 12,30% do valor máximo alcançado.

**Como interpretar:**
- **-5% a -10%:** Drawdown baixo, estratégia estável ✅
- **-10% a -20%:** Drawdown moderado, aceitável
- **> -20%:** Drawdown alto, estratégia arriscada ⚠️

**Importante:** Este é o "pior momento" que você teria passado. Pergunte-se: "Eu aguentaria ver meu capital cair X%?"

#### Card 4: Número de Trades
**O que mostra:** Quantas operações (compras + vendas) foram executadas.

**Como interpretar:**
- **Poucos trades (< 20):** Estratégia de longo prazo, menos custos
- **Muitos trades (> 100):** Estratégia ativa, mais custos de corretagem

---

### 2. Gráfico: Curva de Equity

**O que mostra:** A evolução do valor do seu portfólio ao longo do tempo.

**Elementos do gráfico:**
- **Linha azul:** Valor total do portfólio (capital + posições)
- **Linha vermelha tracejada:** Capital inicial (referência)
- **Eixo X:** Datas
- **Eixo Y:** Valor em reais

**Como usar:**
- **Passe o mouse:** Veja o valor exato em cada data
- **Zoom:** Clique e arraste para dar zoom em um período
- **Pan:** Arraste o gráfico para navegar

**O que procurar:**
- ✅ **Tendência ascendente:** Estratégia lucrativa
- ⚠️ **Muita volatilidade:** Estratégia arriscada
- ❌ **Tendência descendente:** Estratégia perdedora

---

### 3. Gráfico: Drawdown

**O que mostra:** As perdas percentuais em relação ao pico anterior.

**Como interpretar:**
- **Área vermelha:** Períodos de perda
- **Linha em zero:** Portfólio em novo pico histórico
- **Profundidade:** Quanto você perdeu
- **Duração:** Quanto tempo levou para recuperar

**O que procurar:**
- ✅ **Drawdowns curtos e rasos:** Recuperação rápida
- ⚠️ **Drawdowns longos:** Demora para recuperar o capital
- ❌ **Drawdown profundo no final:** Estratégia pode estar se deteriorando

---

### 4. Relatório de Risco (3 Colunas)

#### Coluna 1: Métricas de Perda
**VaR (Value at Risk):**
- O que mostra: "Em um dia ruim, posso perder até R$ X com 95% de confiança"
- Exemplo: `R$ 2.500` = em 95% dos dias, você não perderá mais que R$ 2.500

**Volatilidade Anual:**
- O que mostra: Quanto o portfólio "balança" em um ano
- Exemplo: `15%` = oscilação típica de 15% ao ano
- Quanto menor, mais estável

#### Coluna 2: Métricas de Exposição
**Alavancagem:**
- O que mostra: Quanto você está exposto em relação ao capital
- Exemplo: `1.5x` = você tem R$ 150 de exposição para cada R$ 100 de capital
- **1.0x:** Sem alavancagem (ideal para iniciantes)
- **> 2.0x:** Alta alavancagem (risco elevado)

**Número de Posições:**
- Quantas ações diferentes você tem no portfólio

#### Coluna 3: Concentração
**Maior Posição:**
- Percentual do portfólio na ação mais concentrada
- Exemplo: `12%` = 12% do capital em uma única ação
- Ideal: < 10% para boa diversificação

**Ticker da Maior Posição:**
- Qual ação está mais concentrada

---

### 5. Histórico de Trades (Tabela)

**O que mostra:** Todas as operações executadas, linha por linha.

**Colunas:**
- **date:** Data da operação
- **ticker:** Código da ação
- **quantity:** Quantidade (positivo = compra, negativo = venda)
- **price:** Preço de execução (R$)
- **value:** Valor total da operação (R$)
- **commission:** Custo de corretagem (R$)
- **total_cost:** Custo total incluindo taxas (R$)

**Recursos interativos:**
- **Ordenar:** Clique no cabeçalho de qualquer coluna
- **Buscar:** Use Ctrl+F no navegador
- **Scroll:** Role para ver todas as operações

**Botão "📥 Download CSV":**
- Baixa a tabela completa em formato CSV
- Abra no Excel, Google Sheets ou Python para análises adicionais

---

## 🎯 Fluxo de Uso Recomendado

### Para Iniciantes:

1. **Primeira execução:** Use os valores padrão e clique em "Executar Backtest"
2. **Analise os resultados:** Foque no Sharpe Ratio e Max Drawdown
3. **Experimente:** Mude o período de lookback (30, 60, 90 dias) e compare
4. **Varie o universo:** Adicione ou remova ações e veja o impacto
5. **Documente:** Anote quais configurações deram melhores resultados

### Para Avançados:

1. **Teste múltiplos períodos:** Execute backtests em diferentes janelas de tempo
2. **Análise de sensibilidade:** Varie sistematicamente cada parâmetro
3. **Compare estratégias:** Long-only (Bottom N = 0) vs Long-Short
4. **Otimização:** Encontre a combinação ideal de parâmetros
5. **Walk-forward:** Teste em um período e valide em outro

---

## ⚠️ Avisos Importantes

### 1. Overfitting
**Problema:** Ajustar demais os parâmetros para o período testado.

**Como evitar:**
- Não teste dezenas de combinações e escolha a melhor
- Use períodos diferentes para validação
- Prefira estratégias simples

### 2. Custos de Transação
**Importante:** O backtest já inclui:
- Corretagem: 0,05% por operação
- Slippage: 0,01% (diferença entre preço esperado e executado)

**Atenção:** Não inclui:
- Imposto de renda (15% sobre ganhos)
- Emolumentos da B3
- Taxa de custódia

### 3. Dados Históricos
**Limitação:** Usa dados do Yahoo Finance, que podem ter:
- Pequenas imprecisões
- Falta de ajuste para proventos em alguns casos
- Dados faltantes em datas específicas

### 4. Operações Short
**Atenção:** A estratégia inclui vendas a descoberto (short), que:
- Nem sempre são permitidas para pessoas físicas
- Exigem margem e garantias
- Têm custos adicionais (aluguel de ações)

**Alternativa:** Configure Bottom N = 0 para estratégia long-only (apenas compras).

---

## 💡 Dicas de Interpretação

### Resultado Bom:
- ✅ Sharpe Ratio > 1.5
- ✅ Max Drawdown < -15%
- ✅ Curva de equity ascendente e suave
- ✅ Retorno superior ao CDI ou Ibovespa

### Resultado Ruim:
- ❌ Sharpe Ratio < 0.5
- ❌ Max Drawdown > -25%
- ❌ Curva de equity muito volátil
- ❌ Muitos trades com pouco retorno

### Sinais de Alerta:
- ⚠️ Drawdown longo no final do período
- ⚠️ Volatilidade muito alta
- ⚠️ Pouquíssimos trades (< 5)
- ⚠️ Todos os ganhos concentrados em um curto período

---

## 🚀 Próximos Passos

Após dominar o dashboard:

1. **Estude a documentação:** Leia os 6 documentos na pasta `docs/`
2. **Modifique o código:** Crie suas próprias estratégias
3. **Paper trading:** Teste em tempo real sem dinheiro real
4. **Aprenda mais:** Estude finanças quantitativas e gestão de risco

---

**Lembre-se:** Este é um projeto educacional. Resultados passados não garantem resultados futuros. Sempre consulte um profissional antes de investir dinheiro real.
