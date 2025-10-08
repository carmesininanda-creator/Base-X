"""
Dashboard de monitoramento para o fundo quantitativo.

Para executar:
    streamlit run dashboard.py
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

from data.market_data import MarketDataProvider
from strategies.momentum_strategy import MomentumStrategy
from backtesting.backtest_engine import BacktestEngine
from risk.risk_manager import RiskManager


# Configurar página
st.set_page_config(
    page_title="Fundo Quantitativo - Dashboard",
    page_icon="📊",
    layout="wide"
)

# Título
st.title("📊 Dashboard do Fundo Quantitativo")
st.markdown("---")


# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações")

# Seleção de tickers
st.sidebar.subheader("Universo de Ativos")
default_tickers = [
    'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA',
    'ABEV3.SA', 'B3SA3.SA', 'WEGE3.SA', 'RENT3.SA'
]
tickers_input = st.sidebar.text_area(
    "Tickers (um por linha)",
    value="\n".join(default_tickers),
    height=150
)
tickers = [t.strip() for t in tickers_input.split('\n') if t.strip()]

# Período
st.sidebar.subheader("Período")
end_date = st.sidebar.date_input("Data Final", datetime.now())
start_date = st.sidebar.date_input(
    "Data Inicial",
    datetime.now() - timedelta(days=730)
)

# Parâmetros da estratégia
st.sidebar.subheader("Estratégia de Momentum")
lookback_period = st.sidebar.slider("Período de Lookback (dias)", 20, 126, 63)
top_n = st.sidebar.slider("Top N (Comprar)", 1, 10, 3)
bottom_n = st.sidebar.slider("Bottom N (Vender)", 1, 10, 3)

# Capital inicial
st.sidebar.subheader("Backtest")
initial_capital = st.sidebar.number_input(
    "Capital Inicial (R$)",
    min_value=10000,
    max_value=10000000,
    value=100000,
    step=10000
)

# Botão para executar
run_button = st.sidebar.button("🚀 Executar Backtest", type="primary")


# Função para executar backtest
@st.cache_data
def run_backtest_cached(tickers, start_date, end_date, lookback_period, top_n, bottom_n, initial_capital):
    """Executa o backtest com cache."""
    
    # Baixar dados
    provider = MarketDataProvider(source="yahoo")
    data = provider.get_historical_data(
        tickers=tickers,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    # Criar estratégia
    strategy = MomentumStrategy(
        lookback_period=lookback_period,
        top_n=top_n,
        bottom_n=bottom_n,
        rebalance_frequency="monthly"
    )
    
    # Gerar sinais
    signals = strategy.generate_signals(data)
    
    # Executar backtest
    engine = BacktestEngine(
        initial_capital=initial_capital,
        commission=0.0005,
        slippage=0.0001
    )
    
    equity_curve = engine.run_backtest(data, signals)
    metrics = engine.calculate_metrics()
    trades_df = engine.get_trades_df()
    
    # Calcular risco
    risk_manager = RiskManager()
    
    # Simular posições finais para o relatório de risco
    final_positions = {}
    final_prices = {}
    
    if not trades_df.empty:
        for ticker in tickers:
            ticker_trades = trades_df[trades_df['ticker'] == ticker]
            if not ticker_trades.empty:
                total_qty = ticker_trades['quantity'].sum()
                if total_qty != 0:
                    final_positions[ticker] = total_qty
                    final_prices[ticker] = ticker_trades.iloc[-1]['price']
    
    risk_report = risk_manager.generate_risk_report(
        equity_curve=equity_curve['Total'],
        portfolio_value=equity_curve['Total'].iloc[-1],
        positions=final_positions,
        prices=final_prices
    )
    
    return equity_curve, metrics, trades_df, risk_report


# Executar backtest
if run_button:
    with st.spinner("Executando backtest... Isso pode levar alguns minutos."):
        try:
            equity_curve, metrics, trades_df, risk_report = run_backtest_cached(
                tickers, start_date, end_date, lookback_period, top_n, bottom_n, initial_capital
            )
            
            st.success("✅ Backtest concluído com sucesso!")
            
            # Seção 1: Métricas Principais
            st.header("📈 Métricas de Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Retorno Total",
                    f"{metrics['Total Return']:.2%}",
                    delta=f"{metrics['Total Return']:.2%}"
                )
            
            with col2:
                st.metric(
                    "Sharpe Ratio",
                    f"{metrics['Sharpe Ratio']:.2f}"
                )
            
            with col3:
                st.metric(
                    "Max Drawdown",
                    f"{metrics['Maximum Drawdown']:.2%}",
                    delta=f"{metrics['Maximum Drawdown']:.2%}",
                    delta_color="inverse"
                )
            
            with col4:
                st.metric(
                    "Número de Trades",
                    f"{metrics['Number of Trades']}"
                )
            
            st.markdown("---")
            
            # Seção 2: Gráfico de Equity
            st.header("💰 Curva de Equity")
            
            fig_equity = go.Figure()
            
            fig_equity.add_trace(go.Scatter(
                x=equity_curve.index,
                y=equity_curve['Total'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig_equity.add_hline(
                y=initial_capital,
                line_dash="dash",
                line_color="red",
                annotation_text="Capital Inicial"
            )
            
            fig_equity.update_layout(
                xaxis_title="Data",
                yaxis_title="Valor do Portfólio (R$)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_equity, use_container_width=True)
            
            st.markdown("---")
            
            # Seção 3: Drawdown
            st.header("📉 Drawdown")
            
            returns = equity_curve['Total'].pct_change()
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            
            fig_dd = go.Figure()
            
            fig_dd.add_trace(go.Scatter(
                x=drawdown.index,
                y=drawdown * 100,
                mode='lines',
                name='Drawdown',
                fill='tozeroy',
                line=dict(color='red', width=1)
            ))
            
            fig_dd.update_layout(
                xaxis_title="Data",
                yaxis_title="Drawdown (%)",
                hovermode='x unified',
                height=300
            )
            
            st.plotly_chart(fig_dd, use_container_width=True)
            
            st.markdown("---")
            
            # Seção 4: Relatório de Risco
            st.header("🛡️ Relatório de Risco")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("VaR (95%, 1 dia)", f"R$ {risk_report['VaR (95%, 1 day)']:,.2f}")
                st.metric("Volatilidade Anual", f"{risk_report['Volatility (Annual)']:.2%}")
            
            with col2:
                st.metric("Alavancagem", f"{risk_report['Leverage']:.2f}x")
                st.metric("Número de Posições", f"{risk_report['Number of Positions']}")
            
            with col3:
                st.metric("Maior Posição", f"{risk_report['Largest Position']:.2%}")
                if risk_report['Largest Position Ticker']:
                    st.info(f"Ticker: {risk_report['Largest Position Ticker']}")
            
            st.markdown("---")
            
            # Seção 5: Histórico de Trades
            st.header("📋 Histórico de Trades")
            
            if not trades_df.empty:
                st.dataframe(
                    trades_df.style.format({
                        'price': 'R$ {:.2f}',
                        'value': 'R$ {:.2f}',
                        'commission': 'R$ {:.2f}',
                        'total_cost': 'R$ {:.2f}'
                    }),
                    use_container_width=True,
                    height=400
                )
                
                # Botão para download
                csv = trades_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="trades.csv",
                    mime="text/csv"
                )
            else:
                st.info("Nenhum trade foi executado.")
            
        except Exception as e:
            st.error(f"❌ Erro ao executar backtest: {str(e)}")
            st.exception(e)

else:
    st.info("👈 Configure os parâmetros na barra lateral e clique em 'Executar Backtest' para começar.")
    
    # Mostrar informações sobre o projeto
    st.header("ℹ️ Sobre o Projeto")
    
    st.markdown("""
    Este dashboard permite executar backtests de estratégias quantitativas no mercado brasileiro.
    
    **Características:**
    - ✅ Estratégia de Momentum configurável
    - ✅ Análise de performance e risco
    - ✅ Visualizações interativas
    - ✅ Exportação de resultados
    
    **Como usar:**
    1. Configure os tickers na barra lateral
    2. Defina o período de análise
    3. Ajuste os parâmetros da estratégia
    4. Clique em "Executar Backtest"
    """)
