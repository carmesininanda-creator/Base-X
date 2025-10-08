"""
Motor de backtesting para estratégias quantitativas.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """Motor de backtesting para estratégias quantitativas."""
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.0005,
        slippage: float = 0.0001
    ):
        """
        Inicializa o motor de backtesting.
        
        Args:
            initial_capital: Capital inicial em reais
            commission: Taxa de corretagem (percentual)
            slippage: Derrapagem estimada (percentual)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # Estado do backtest
        self.current_capital = initial_capital
        self.positions = {}  # {ticker: quantidade}
        self.portfolio_value = []
        self.trades = []
        self.equity_curve = pd.DataFrame()
        
        logger.info(f"BacktestEngine inicializado com capital: R$ {initial_capital:,.2f}")
    
    def calculate_position_value(self, prices: Dict[str, float]) -> float:
        """
        Calcula o valor total das posições abertas.
        
        Args:
            prices: Dicionário {ticker: preço}
        
        Returns:
            Valor total das posições
        """
        total_value = 0.0
        for ticker, quantity in self.positions.items():
            if ticker in prices:
                total_value += quantity * prices[ticker]
        return total_value
    
    def execute_trade(
        self,
        ticker: str,
        quantity: int,
        price: float,
        date: datetime
    ) -> Dict:
        """
        Executa uma ordem de compra ou venda.
        
        Args:
            ticker: Ticker do ativo
            quantity: Quantidade (positivo para compra, negativo para venda)
            price: Preço de execução
            date: Data da operação
        
        Returns:
            Dicionário com informações da operação
        """
        # Aplicar slippage
        if quantity > 0:  # Compra
            execution_price = price * (1 + self.slippage)
        else:  # Venda
            execution_price = price * (1 - self.slippage)
        
        # Calcular custo total
        trade_value = abs(quantity) * execution_price
        commission_cost = trade_value * self.commission
        total_cost = trade_value + commission_cost
        
        # Atualizar posição
        if ticker not in self.positions:
            self.positions[ticker] = 0
        self.positions[ticker] += quantity
        
        # Atualizar capital
        if quantity > 0:  # Compra
            self.current_capital -= total_cost
        else:  # Venda
            self.current_capital += trade_value - commission_cost
        
        # Registrar trade
        trade_record = {
            'date': date,
            'ticker': ticker,
            'quantity': quantity,
            'price': execution_price,
            'value': trade_value,
            'commission': commission_cost,
            'total_cost': total_cost
        }
        self.trades.append(trade_record)
        
        logger.debug(f"Trade executado: {ticker} {quantity} @ R$ {execution_price:.2f}")
        
        return trade_record
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Executa o backtest com base nos sinais de trading.
        
        Args:
            data: DataFrame com dados de mercado (MultiIndex: Date, Ticker)
            signals: DataFrame com sinais de trading (1: compra, -1: venda, 0: neutro)
        
        Returns:
            DataFrame com a curva de equity
        """
        logger.info("Iniciando backtest...")
        
        dates = signals.index.get_level_values('Date').unique().sort_values()
        equity_records = []
        
        for date in dates:
            # Obter sinais e preços do dia
            try:
                day_signals = signals.xs(date, level='Date')
                day_prices = data.xs(date, level='Date')['Close']
            except KeyError:
                continue
            
            # Executar trades baseados nos sinais
            for ticker in day_signals.index:
                signal = day_signals.loc[ticker, 'Signal']
                
                if signal != 0 and ticker in day_prices.index:
                    price = day_prices[ticker]
                    current_position = self.positions.get(ticker, 0)
                    
                    # Determinar quantidade a negociar
                    # (Simplificado: aloca capital igualmente entre posições)
                    if signal == 1 and current_position == 0:  # Compra
                        allocation = self.initial_capital * 0.1  # 10% do capital por posição
                        quantity = int(allocation / price)
                        if quantity > 0:
                            self.execute_trade(ticker, quantity, price, date)
                    
                    elif signal == -1 and current_position > 0:  # Venda
                        self.execute_trade(ticker, -current_position, price, date)
            
            # Calcular valor do portfólio
            prices_dict = day_prices.to_dict()
            position_value = self.calculate_position_value(prices_dict)
            total_value = self.current_capital + position_value
            
            equity_records.append({
                'Date': date,
                'Cash': self.current_capital,
                'Positions': position_value,
                'Total': total_value,
                'Returns': (total_value - self.initial_capital) / self.initial_capital
            })
        
        # Criar DataFrame com a curva de equity
        self.equity_curve = pd.DataFrame(equity_records).set_index('Date')
        
        logger.info(f"Backtest concluído. Total de trades: {len(self.trades)}")
        
        return self.equity_curve
    
    def calculate_metrics(self) -> Dict[str, float]:
        """
        Calcula métricas de performance do backtest.
        
        Returns:
            Dicionário com as métricas calculadas
        """
        if self.equity_curve.empty:
            logger.warning("Nenhum backtest foi executado ainda")
            return {}
        
        # Calcular retornos diários
        daily_returns = self.equity_curve['Total'].pct_change().dropna()
        
        # Retorno total
        total_return = (self.equity_curve['Total'].iloc[-1] - self.initial_capital) / self.initial_capital
        
        # Retorno anualizado
        num_days = len(self.equity_curve)
        num_years = num_days / 252  # 252 dias úteis por ano
        annualized_return = (1 + total_return) ** (1 / num_years) - 1 if num_years > 0 else 0
        
        # Volatilidade anualizada
        volatility = daily_returns.std() * np.sqrt(252)
        
        # Sharpe Ratio (assumindo taxa livre de risco = 0)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Maximum Drawdown
        cumulative = (1 + daily_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        metrics = {
            'Total Return': total_return,
            'Annualized Return': annualized_return,
            'Volatility': volatility,
            'Sharpe Ratio': sharpe_ratio,
            'Maximum Drawdown': max_drawdown,
            'Number of Trades': len(self.trades),
            'Final Capital': self.equity_curve['Total'].iloc[-1]
        }
        
        return metrics
    
    def get_trades_df(self) -> pd.DataFrame:
        """
        Retorna um DataFrame com todos os trades executados.
        
        Returns:
            DataFrame com os trades
        """
        return pd.DataFrame(self.trades)


def test_backtest_engine():
    """Função de teste para o BacktestEngine."""
    # Criar dados de teste
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    tickers = ['PETR4.SA', 'VALE3.SA']
    
    # Simular dados de preço
    data_list = []
    for date in dates:
        for ticker in tickers:
            data_list.append({
                'Date': date,
                'Ticker': ticker,
                'Close': 30 + np.random.randn() * 2
            })
    
    data = pd.DataFrame(data_list).set_index(['Date', 'Ticker'])
    
    # Criar sinais de teste (compra no início, venda no final)
    signals_list = []
    for i, date in enumerate(dates):
        for ticker in tickers:
            if i == 0:
                signal = 1  # Compra
            elif i == len(dates) - 1:
                signal = -1  # Venda
            else:
                signal = 0  # Neutro
            
            signals_list.append({
                'Date': date,
                'Ticker': ticker,
                'Signal': signal
            })
    
    signals = pd.DataFrame(signals_list).set_index(['Date', 'Ticker'])
    
    # Executar backtest
    engine = BacktestEngine(initial_capital=100000)
    equity_curve = engine.run_backtest(data, signals)
    
    print("\nCurva de Equity:")
    print(equity_curve.head())
    print("\nMétricas de Performance:")
    metrics = engine.calculate_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    test_backtest_engine()
