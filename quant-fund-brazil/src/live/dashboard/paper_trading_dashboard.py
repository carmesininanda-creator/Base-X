"""
Dashboard de monitoramento em tempo real para paper trading.
Interface Streamlit para visualizar e controlar o sistema.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.live.database.trading_db import TradingDatabase
from src.live.signals.signal_generator import SignalGenerator
from src.live.data.realtime_data_fetcher import RealtimeDataFetcher
from src.live.execution.paper_executor import PaperExecutor, OrderSide

# Configuração da página
st.set_page_config(
    page_title="Paper Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .big-metric {
        font-size: 2rem;
        font-weight: bold;
    }
    .positive {
        color: #00ff00;
    }
    .negative {
        color: #ff0000;
    }
    .neutral {
        color: #ffaa00;
    }
</style>
""", unsafe_allow_html=True)


class PaperTradingDashboard:
    """Dashboard para paper trading."""
    
    def __init__(self):
        """Inicializa o dashboard."""
        self.db = TradingDatabase("data/paper_trading.db")
        
        # Inicializar session state
        if 'system_running' not in st.session_state:
            st.session_state.system_running = False
        if 'last_update' not in st.session_state:
            st.session_state.last_update = None
    
    def render_header(self):
        """Renderiza o cabeçalho do dashboard."""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.title("📊 Paper Trading Dashboard")
            st.caption("Sistema de Trading Quantitativo - Simulação")
        
        with col2:
            status = "🟢 ATIVO" if st.session_state.system_running else "🔴 PARADO"
            st.metric("Status do Sistema", status)
        
        with col3:
            if st.session_state.last_update:
                st.metric("Última Atualização", 
                         st.session_state.last_update.strftime("%H:%M:%S"))
    
    def render_portfolio_overview(self):
        """Renderiza visão geral do portfólio."""
        st.header("💼 Visão Geral do Portfólio")
        
        # Buscar dados
        positions = self.db.get_positions()
        snapshots = self.db.get_daily_snapshots(days=1)
        
        # Calcular métricas
        total_value = sum(pos['quantity'] * pos['current_price'] 
                         for pos in positions if pos['current_price'])
        total_pnl = sum(pos['unrealized_pnl'] for pos in positions)
        
        # Valores padrão se não houver snapshot
        portfolio_value = snapshots[0]['portfolio_value'] if snapshots else 100000
        daily_pnl = snapshots[0]['daily_pnl'] if snapshots else 0
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Valor do Portfólio",
                f"R$ {portfolio_value:,.2f}",
                delta=f"{(portfolio_value/100000 - 1)*100:+.2f}%"
            )
        
        with col2:
            pnl_color = "normal" if total_pnl >= 0 else "inverse"
            st.metric(
                "P&L Não Realizado",
                f"R$ {total_pnl:,.2f}",
                delta=f"{(total_pnl/portfolio_value)*100:+.2f}%",
                delta_color=pnl_color
            )
        
        with col3:
            st.metric(
                "P&L do Dia",
                f"R$ {daily_pnl:,.2f}",
                delta=f"{(daily_pnl/portfolio_value)*100:+.2f}%"
            )
        
        with col4:
            st.metric(
                "Posições Abertas",
                len([p for p in positions if p['quantity'] != 0])
            )
    
    def render_positions(self):
        """Renderiza tabela de posições."""
        st.header("📈 Posições Atuais")
        
        positions = self.db.get_positions()
        
        if not positions:
            st.info("Nenhuma posição aberta no momento.")
            return
        
        # Criar DataFrame
        df = pd.DataFrame(positions)
        df = df[df['quantity'] != 0]  # Apenas posições abertas
        
        if df.empty:
            st.info("Nenhuma posição aberta no momento.")
            return
        
        # Formatar valores
        df['avg_price'] = df['avg_price'].apply(lambda x: f"R$ {x:.2f}")
        df['current_price'] = df['current_price'].apply(lambda x: f"R$ {x:.2f}" if x else "N/A")
        df['unrealized_pnl'] = df['unrealized_pnl'].apply(lambda x: f"R$ {x:+,.2f}")
        
        # Renomear colunas
        df = df.rename(columns={
            'ticker': 'Ticker',
            'quantity': 'Quantidade',
            'avg_price': 'Preço Médio',
            'current_price': 'Preço Atual',
            'unrealized_pnl': 'P&L Não Realizado'
        })
        
        # Exibir tabela
        st.dataframe(
            df[['Ticker', 'Quantidade', 'Preço Médio', 'Preço Atual', 'P&L Não Realizado']],
            use_container_width=True,
            hide_index=True
        )
    
    def render_recent_orders(self):
        """Renderiza ordens recentes."""
        st.header("📋 Ordens Recentes")
        
        orders = self.db.get_orders(limit=10)
        
        if not orders:
            st.info("Nenhuma ordem registrada ainda.")
            return
        
        # Criar DataFrame
        df = pd.DataFrame(orders)
        
        # Formatar valores
        df['price'] = df['price'].apply(lambda x: f"R$ {x:.2f}")
        df['filled_price'] = df['filled_price'].apply(lambda x: f"R$ {x:.2f}" if x else "N/A")
        df['commission'] = df['commission'].apply(lambda x: f"R$ {x:.2f}")
        df['total_cost'] = df['total_cost'].apply(lambda x: f"R$ {x:,.2f}")
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%d/%m %H:%M')
        
        # Renomear colunas
        df = df.rename(columns={
            'timestamp': 'Data/Hora',
            'ticker': 'Ticker',
            'side': 'Lado',
            'quantity': 'Qtd',
            'price': 'Preço Ref',
            'filled_price': 'Preço Exec',
            'status': 'Status',
            'commission': 'Corretagem',
            'total_cost': 'Custo Total'
        })
        
        # Exibir tabela
        st.dataframe(
            df[['Data/Hora', 'Ticker', 'Lado', 'Qtd', 'Preço Ref', 'Preço Exec', 'Status', 'Corretagem', 'Custo Total']],
            use_container_width=True,
            hide_index=True
        )
    
    def render_performance_chart(self):
        """Renderiza gráfico de performance."""
        st.header("📊 Performance Histórica")
        
        snapshots = self.db.get_daily_snapshots(days=30)
        
        if not snapshots:
            st.info("Dados insuficientes para gráfico. Execute o sistema por alguns dias.")
            return
        
        # Criar DataFrame
        df = pd.DataFrame(snapshots)
        df = df.sort_values('date')
        df['date'] = pd.to_datetime(df['date'])
        
        # Criar gráfico
        fig = go.Figure()
        
        # Linha de valor do portfólio
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['portfolio_value'],
            mode='lines+markers',
            name='Valor do Portfólio',
            line=dict(color='#00ff00', width=2),
            marker=dict(size=6)
        ))
        
        # Linha de referência (capital inicial)
        fig.add_hline(
            y=100000,
            line_dash="dash",
            line_color="gray",
            annotation_text="Capital Inicial"
        )
        
        # Layout
        fig.update_layout(
            title="Evolução do Portfólio",
            xaxis_title="Data",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_pnl_chart(self):
        """Renderiza gráfico de P&L diário."""
        st.header("💰 P&L Diário")
        
        snapshots = self.db.get_daily_snapshots(days=30)
        
        if not snapshots:
            st.info("Dados insuficientes para gráfico.")
            return
        
        # Criar DataFrame
        df = pd.DataFrame(snapshots)
        df = df.sort_values('date')
        df['date'] = pd.to_datetime(df['date'])
        
        # Criar gráfico de barras
        fig = px.bar(
            df,
            x='date',
            y='daily_pnl',
            title="P&L Diário",
            labels={'date': 'Data', 'daily_pnl': 'P&L (R$)'},
            color='daily_pnl',
            color_continuous_scale=['red', 'yellow', 'green']
        )
        
        fig.update_layout(height=300)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_statistics(self):
        """Renderiza estatísticas do sistema."""
        st.header("📊 Estatísticas do Sistema")
        
        stats = self.db.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Ordens", stats['total_orders'])
        
        with col2:
            st.metric("Ordens Executadas", stats['filled_orders'])
        
        with col3:
            st.metric("Comissão Total", f"R$ {stats['total_commission']:.2f}")
        
        with col4:
            st.metric("Dias de Operação", stats['total_snapshots'])
    
    def render_controls(self):
        """Renderiza controles do sistema."""
        st.sidebar.header("⚙️ Controles do Sistema")
        
        # Botão de iniciar/parar
        if st.session_state.system_running:
            if st.sidebar.button("⏸️ Pausar Sistema", type="primary", use_container_width=True):
                st.session_state.system_running = False
                st.sidebar.success("Sistema pausado!")
                st.rerun()
        else:
            if st.sidebar.button("▶️ Iniciar Sistema", type="primary", use_container_width=True):
                st.session_state.system_running = True
                st.sidebar.success("Sistema iniciado!")
                st.rerun()
        
        st.sidebar.divider()
        
        # Botão de atualizar
        if st.sidebar.button("🔄 Atualizar Dados", use_container_width=True):
            st.session_state.last_update = datetime.now()
            st.rerun()
        
        st.sidebar.divider()
        
        # Configurações
        st.sidebar.subheader("📝 Configurações")
        
        lookback = st.sidebar.slider("Período de Lookback (dias)", 20, 126, 63)
        top_n = st.sidebar.slider("Top N (comprar)", 1, 10, 3)
        bottom_n = st.sidebar.slider("Bottom N (vender)", 1, 10, 3)
        
        st.sidebar.divider()
        
        # Informações
        st.sidebar.subheader("ℹ️ Informações")
        st.sidebar.info("""
        **Modo:** Paper Trading (Simulação)
        
        **Nenhum dinheiro real está sendo usado.**
        
        Este é um ambiente de teste seguro para validar a estratégia antes de operar com capital real.
        """)
    
    def run(self):
        """Executa o dashboard."""
        # Cabeçalho
        self.render_header()
        
        st.divider()
        
        # Controles na sidebar
        self.render_controls()
        
        # Conteúdo principal
        self.render_portfolio_overview()
        
        st.divider()
        
        # Duas colunas
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_positions()
        
        with col2:
            self.render_recent_orders()
        
        st.divider()
        
        # Gráficos
        self.render_performance_chart()
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_pnl_chart()
        
        with col2:
            self.render_statistics()
        
        # Footer
        st.divider()
        st.caption("📊 Paper Trading Dashboard | Desenvolvido por Manus para Nanda 💙")


def main():
    """Função principal."""
    dashboard = PaperTradingDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()

