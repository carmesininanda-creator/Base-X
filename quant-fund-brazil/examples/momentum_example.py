"""
Exemplo completo de uso da estratégia de momentum.

Este script demonstra como:
1. Baixar dados de mercado
2. Criar e configurar a estratégia de momentum
3. Executar um backtest
4. Analisar os resultados
"""

import sys
from pathlib import Path

# Adicionar o diretório src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from data.market_data import MarketDataProvider
from strategies.momentum_strategy import MomentumStrategy
from backtesting.backtest_engine import BacktestEngine


def run_momentum_backtest():
    """Executa um backtest completo da estratégia de momentum."""
    
    print("=" * 80)
    print("BACKTEST DA ESTRATÉGIA DE MOMENTUM")
    print("=" * 80)
    
    # 1. Configurar parâmetros
    print("\n1. Configurando parâmetros...")
    
    tickers = [
        'PETR4.SA',  # Petrobras
        'VALE3.SA',  # Vale
        'ITUB4.SA',  # Itaú
        'BBDC4.SA',  # Bradesco
        'ABEV3.SA',  # Ambev
        'B3SA3.SA',  # B3
        'WEGE3.SA',  # WEG
        'RENT3.SA',  # Localiza
        'GGBR4.SA',  # Gerdau
        'SUZB3.SA'   # Suzano
    ]
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')  # 2 anos
    
    print(f"   Tickers: {len(tickers)} ativos")
    print(f"   Período: {start_date} até {end_date}")
    
    # 2. Baixar dados de mercado
    print("\n2. Baixando dados de mercado...")
    
    provider = MarketDataProvider(source="yahoo")
    data = provider.get_historical_data(
        tickers=tickers,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"   Dados baixados: {len(data)} registros")
    
    # 3. Criar e configurar a estratégia
    print("\n3. Configurando estratégia de momentum...")
    
    strategy = MomentumStrategy(
        lookback_period=63,  # 3 meses
        top_n=3,  # Comprar top 3 ativos
        bottom_n=3,  # Vender bottom 3 ativos
        rebalance_frequency="monthly"
    )
    
    print(f"   Estratégia: {strategy}")
    
    # 4. Gerar sinais de trading
    print("\n4. Gerando sinais de trading...")
    
    signals = strategy.generate_signals(data)
    
    num_signals = (signals['Signal'] != 0).sum()
    print(f"   Sinais gerados: {num_signals}")
    print(f"   Sinais de compra: {(signals['Signal'] == 1).sum()}")
    print(f"   Sinais de venda: {(signals['Signal'] == -1).sum()}")
    
    # 5. Executar backtest
    print("\n5. Executando backtest...")
    
    engine = BacktestEngine(
        initial_capital=100000.0,  # R$ 100.000
        commission=0.0005,  # 0.05%
        slippage=0.0001  # 0.01%
    )
    
    equity_curve = engine.run_backtest(data, signals)
    
    print(f"   Backtest concluído")
    print(f"   Total de trades: {len(engine.trades)}")
    
    # 6. Calcular e exibir métricas
    print("\n6. Métricas de Performance:")
    print("-" * 80)
    
    metrics = engine.calculate_metrics()
    
    for key, value in metrics.items():
        if isinstance(value, float):
            if 'Return' in key or 'Drawdown' in key:
                print(f"   {key:.<50} {value:>10.2%}")
            elif 'Ratio' in key:
                print(f"   {key:.<50} {value:>10.2f}")
            elif 'Capital' in key:
                print(f"   {key:.<50} R$ {value:>10,.2f}")
            else:
                print(f"   {key:.<50} {value:>10.4f}")
        else:
            print(f"   {key:.<50} {value:>10}")
    
    # 7. Visualizar resultados
    print("\n7. Gerando gráficos...")
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Gráfico 1: Curva de Equity
    axes[0].plot(equity_curve.index, equity_curve['Total'], label='Portfolio Value', linewidth=2)
    axes[0].axhline(y=engine.initial_capital, color='r', linestyle='--', label='Initial Capital')
    axes[0].set_title('Curva de Equity - Estratégia de Momentum', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Data')
    axes[0].set_ylabel('Valor do Portfólio (R$)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Gráfico 2: Retornos
    daily_returns = equity_curve['Total'].pct_change()
    axes[1].plot(daily_returns.index, daily_returns * 100, label='Daily Returns', linewidth=1, alpha=0.7)
    axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[1].set_title('Retornos Diários', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Data')
    axes[1].set_ylabel('Retorno (%)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar gráfico
    output_path = project_root / "examples" / "momentum_backtest_results.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   Gráfico salvo em: {output_path}")
    
    # 8. Salvar resultados
    print("\n8. Salvando resultados...")
    
    # Salvar curva de equity
    equity_path = project_root / "examples" / "equity_curve.csv"
    equity_curve.to_csv(equity_path)
    print(f"   Curva de equity salva em: {equity_path}")
    
    # Salvar trades
    trades_path = project_root / "examples" / "trades.csv"
    trades_df = engine.get_trades_df()
    trades_df.to_csv(trades_path, index=False)
    print(f"   Trades salvos em: {trades_path}")
    
    print("\n" + "=" * 80)
    print("BACKTEST CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    
    return equity_curve, metrics


if __name__ == "__main__":
    equity_curve, metrics = run_momentum_backtest()
