# Guia Rápido do Dashboard - 5 Minutos

## 🎯 Objetivo
Executar seu primeiro backtest e entender os resultados em 5 minutos.

---

## 📋 Passo a Passo

### PASSO 1: Acesse o Dashboard
🔗 Abra o link no seu navegador

### PASSO 2: Configure (Barra Lateral)
```
✅ Deixe os valores padrão
✅ Ou ajuste conforme sua preferência:
   - Tickers: PETR4.SA, VALE3.SA, etc.
   - Período: Últimos 2 anos
   - Lookback: 63 dias
   - Top N: 3 ações
   - Bottom N: 3 ações
   - Capital: R$ 100.000
```

### PASSO 3: Execute
🚀 Clique no botão **"Executar Backtest"**
⏳ Aguarde 1-2 minutos

### PASSO 4: Analise os Resultados

#### 4.1 Olhe os 4 Cards no Topo

| Card | O que significa | Bom | Ruim |
|------|----------------|-----|------|
| **Retorno Total** | Quanto você ganhou/perdeu | > +15% | < 0% |
| **Sharpe Ratio** | Qualidade do retorno | > 1.5 | < 0.5 |
| **Max Drawdown** | Maior perda | > -15% | < -25% |
| **Trades** | Número de operações | 20-100 | < 5 ou > 200 |

#### 4.2 Veja o Gráfico de Equity
- ✅ **Subindo:** Estratégia lucrativa
- ⚠️ **Muito volátil:** Estratégia arriscada
- ❌ **Descendo:** Estratégia perdedora

#### 4.3 Analise o Drawdown
- ✅ **Raso e curto:** Recuperação rápida
- ❌ **Profundo e longo:** Difícil de aguentar psicologicamente

---

## 🎓 Interpretação Rápida

### Resultado EXCELENTE ⭐
```
Retorno Total:    > +20%
Sharpe Ratio:     > 2.0
Max Drawdown:     > -10%
```
**Significado:** Estratégia muito promissora!

### Resultado BOM ✅
```
Retorno Total:    +10% a +20%
Sharpe Ratio:     1.0 a 2.0
Max Drawdown:     -10% a -15%
```
**Significado:** Estratégia sólida, vale investigar mais.

### Resultado MÉDIO ⚠️
```
Retorno Total:    +5% a +10%
Sharpe Ratio:     0.5 a 1.0
Max Drawdown:     -15% a -20%
```
**Significado:** Estratégia precisa de ajustes.

### Resultado RUIM ❌
```
Retorno Total:    < +5% ou negativo
Sharpe Ratio:     < 0.5
Max Drawdown:     < -20%
```
**Significado:** Estratégia não funciona neste período/configuração.

---

## 🔧 Experimentos Rápidos

### Experimento 1: Período de Lookback
```
Teste 1: 30 dias  (momentum curto prazo)
Teste 2: 63 dias  (momentum médio prazo) ← padrão
Teste 3: 90 dias  (momentum longo prazo)
```
**Compare:** Qual período dá melhor Sharpe Ratio?

### Experimento 2: Número de Ativos
```
Teste 1: Top 2 / Bottom 2  (concentrado)
Teste 2: Top 3 / Bottom 3  (equilibrado) ← padrão
Teste 3: Top 5 / Bottom 5  (diversificado)
```
**Compare:** Mais concentração = mais retorno? Mais risco?

### Experimento 3: Long-Only vs Long-Short
```
Teste 1: Top 5 / Bottom 0  (só compra)
Teste 2: Top 5 / Bottom 5  (compra e vende) ← padrão
```
**Compare:** Short adiciona valor ou só risco?

---

## ⚡ Atalhos do Teclado

- **Ctrl + F:** Buscar na tabela de trades
- **Scroll:** Navegar pelos gráficos
- **Clique no gráfico:** Zoom e detalhes

---

## 📥 Exportar Resultados

1. Role até a tabela de trades
2. Clique em **"📥 Download CSV"**
3. Abra no Excel/Google Sheets
4. Analise as operações em detalhes

---

## 🆘 Problemas Comuns

### "Erro ao baixar dados"
**Solução:** Verifique se os tickers estão corretos (formato: `PETR4.SA`)

### "Backtest muito lento"
**Solução:** Reduza o número de tickers ou o período de análise

### "Poucos trades executados"
**Solução:** Aumente o Top N e Bottom N, ou reduza o período de lookback

---

## 🎯 Checklist de Sucesso

Após seu primeiro backtest, você deve conseguir responder:

- [ ] Qual foi o retorno total da estratégia?
- [ ] O Sharpe Ratio é maior que 1?
- [ ] Qual foi o pior momento (max drawdown)?
- [ ] Quantas operações foram executadas?
- [ ] A curva de equity é ascendente?
- [ ] Você aguentaria as perdas do drawdown?

Se respondeu **SIM** para a maioria, parabéns! Você entendeu o básico. 🎉

---

## 📚 Próximo Passo

Leia o **Guia Completo do Dashboard** (`dashboard_guide.md`) para entender cada funcionalidade em profundidade.

---

**Dica Final:** Não se apaixone pelo primeiro resultado bom! Teste em diferentes períodos e configurações para validar a robustez da estratégia. 🧪
