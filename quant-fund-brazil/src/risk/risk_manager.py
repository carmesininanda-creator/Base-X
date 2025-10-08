"""
Módulo de gestão de risco para o fundo quantitativo.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskManager:
    """Classe para gestão de risco do portfólio."""
    
    def __init__(
        self,
        max_drawdown: float = 0.15,
        max_leverage: float = 2.0,
        max_position_size: float = 0.10,
        stop_loss: float = 0.05,
        var_confidence: float = 0.95
    ):
        """
        Inicializa o gerenciador de risco.
        
        Args:
            max_drawdown: Máximo drawdown aceitável (percentual)
            max_leverage: Alavancagem máxima permitida
            max_position_size: Tamanho máximo de posição por ativo (percentual do PL)
            stop_loss: Stop-loss por posição (percentual)
            var_confidence: Nível de confiança para o VaR
        """
        self.max_drawdown = max_drawdown
        self.max_leverage = max_leverage
        self.max_position_size = max_position_size
        self.stop_loss = stop_loss
        self.var_confidence = var_confidence
        
        logger.info("RiskManager inicializado")
        logger.info(f"  Max Drawdown: {max_drawdown:.1%}")
        logger.info(f"  Max Leverage: {max_leverage:.1f}x")
        logger.info(f"  Max Position Size: {max_position_size:.1%}")
    
    def calculate_drawdown(self, equity_curve: pd.Series) -> Tuple[float, pd.Series]:
        """
        Calcula o drawdown da curva de equity.
        
        Args:
            equity_curve: Series com os valores do portfólio ao longo do tempo
        
        Returns:
            Tupla com (max_drawdown, drawdown_series)
        """
        cumulative = equity_curve
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        
        return max_dd, drawdown
    
    def check_drawdown_limit(self, equity_curve: pd.Series) -> bool:
        """
        Verifica se o drawdown está dentro do limite aceitável.
        
        Args:
            equity_curve: Series com os valores do portfólio
        
        Returns:
            True se está dentro do limite, False caso contrário
        """
        max_dd, _ = self.calculate_drawdown(equity_curve)
        
        if abs(max_dd) > self.max_drawdown:
            logger.warning(f"Drawdown excedeu o limite: {max_dd:.2%} > {self.max_drawdown:.2%}")
            return False
        
        return True
    
    def calculate_position_sizes(
        self,
        portfolio_value: float,
        positions: Dict[str, int],
        prices: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calcula o tamanho de cada posição como percentual do portfólio.
        
        Args:
            portfolio_value: Valor total do portfólio
            positions: Dicionário {ticker: quantidade}
            prices: Dicionário {ticker: preço}
        
        Returns:
            Dicionário {ticker: percentual_do_portfolio}
        """
        position_sizes = {}
        
        for ticker, quantity in positions.items():
            if ticker in prices:
                position_value = quantity * prices[ticker]
                position_sizes[ticker] = position_value / portfolio_value
        
        return position_sizes
    
    def check_position_limits(
        self,
        portfolio_value: float,
        positions: Dict[str, int],
        prices: Dict[str, float]
    ) -> Tuple[bool, List[str]]:
        """
        Verifica se alguma posição excede o limite máximo.
        
        Args:
            portfolio_value: Valor total do portfólio
            positions: Dicionário {ticker: quantidade}
            prices: Dicionário {ticker: preço}
        
        Returns:
            Tupla com (todas_ok, lista_de_violações)
        """
        position_sizes = self.calculate_position_sizes(portfolio_value, positions, prices)
        violations = []
        
        for ticker, size in position_sizes.items():
            if abs(size) > self.max_position_size:
                violations.append(ticker)
                logger.warning(
                    f"Posição em {ticker} excede o limite: "
                    f"{size:.2%} > {self.max_position_size:.2%}"
                )
        
        return len(violations) == 0, violations
    
    def calculate_leverage(
        self,
        portfolio_value: float,
        positions: Dict[str, int],
        prices: Dict[str, float]
    ) -> float:
        """
        Calcula a alavancagem atual do portfólio.
        
        Args:
            portfolio_value: Valor total do portfólio
            positions: Dicionário {ticker: quantidade}
            prices: Dicionário {ticker: preço}
        
        Returns:
            Alavancagem (exposição total / valor do portfólio)
        """
        total_exposure = 0.0
        
        for ticker, quantity in positions.items():
            if ticker in prices:
                total_exposure += abs(quantity * prices[ticker])
        
        leverage = total_exposure / portfolio_value if portfolio_value > 0 else 0
        
        return leverage
    
    def check_leverage_limit(
        self,
        portfolio_value: float,
        positions: Dict[str, int],
        prices: Dict[str, float]
    ) -> bool:
        """
        Verifica se a alavancagem está dentro do limite.
        
        Args:
            portfolio_value: Valor total do portfólio
            positions: Dicionário {ticker: quantidade}
            prices: Dicionário {ticker: preço}
        
        Returns:
            True se está dentro do limite, False caso contrário
        """
        leverage = self.calculate_leverage(portfolio_value, positions, prices)
        
        if leverage > self.max_leverage:
            logger.warning(f"Alavancagem excedeu o limite: {leverage:.2f}x > {self.max_leverage:.2f}x")
            return False
        
        return True
    
    def calculate_var(
        self,
        returns: pd.Series,
        portfolio_value: float,
        time_horizon: int = 1
    ) -> float:
        """
        Calcula o Value at Risk (VaR) do portfólio.
        
        Args:
            returns: Series com os retornos históricos
            portfolio_value: Valor atual do portfólio
            time_horizon: Horizonte de tempo em dias
        
        Returns:
            VaR em reais
        """
        if len(returns) < 2:
            return 0.0
        
        # Calcular o quantil correspondente ao nível de confiança
        var_percentile = 1 - self.var_confidence
        var_return = returns.quantile(var_percentile)
        
        # Ajustar para o horizonte de tempo
        var_return_adjusted = var_return * np.sqrt(time_horizon)
        
        # Converter para valor em reais
        var_value = abs(var_return_adjusted * portfolio_value)
        
        return var_value
    
    def calculate_portfolio_volatility(self, returns: pd.Series) -> float:
        """
        Calcula a volatilidade anualizada do portfólio.
        
        Args:
            returns: Series com os retornos diários
        
        Returns:
            Volatilidade anualizada
        """
        if len(returns) < 2:
            return 0.0
        
        daily_vol = returns.std()
        annual_vol = daily_vol * np.sqrt(252)  # 252 dias úteis
        
        return annual_vol
    
    def generate_risk_report(
        self,
        equity_curve: pd.Series,
        portfolio_value: float,
        positions: Dict[str, int],
        prices: Dict[str, float]
    ) -> Dict:
        """
        Gera um relatório completo de risco.
        
        Args:
            equity_curve: Series com os valores do portfólio ao longo do tempo
            portfolio_value: Valor atual do portfólio
            positions: Dicionário {ticker: quantidade}
            prices: Dicionário {ticker: preço}
        
        Returns:
            Dicionário com métricas de risco
        """
        # Calcular retornos
        returns = equity_curve.pct_change().dropna()
        
        # Calcular métricas
        max_dd, _ = self.calculate_drawdown(equity_curve)
        leverage = self.calculate_leverage(portfolio_value, positions, prices)
        position_sizes = self.calculate_position_sizes(portfolio_value, positions, prices)
        var = self.calculate_var(returns, portfolio_value)
        volatility = self.calculate_portfolio_volatility(returns)
        
        # Identificar maior posição
        max_position = max(position_sizes.values()) if position_sizes else 0
        max_position_ticker = max(position_sizes, key=position_sizes.get) if position_sizes else None
        
        report = {
            'Portfolio Value': portfolio_value,
            'Number of Positions': len(positions),
            'Leverage': leverage,
            'Max Drawdown': max_dd,
            'VaR (95%, 1 day)': var,
            'Volatility (Annual)': volatility,
            'Largest Position': max_position,
            'Largest Position Ticker': max_position_ticker,
            'Position Sizes': position_sizes
        }
        
        return report


def test_risk_manager():
    """Função de teste para o RiskManager."""
    # Criar dados de teste
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    
    # Simular curva de equity
    np.random.seed(42)
    returns = np.random.randn(len(dates)) * 0.01
    equity = pd.Series(100000 * (1 + returns).cumprod(), index=dates)
    
    # Criar posições de teste
    positions = {
        'PETR4.SA': 1000,
        'VALE3.SA': 800,
        'ITUB4.SA': 1500
    }
    
    prices = {
        'PETR4.SA': 30.0,
        'VALE3.SA': 65.0,
        'ITUB4.SA': 25.0
    }
    
    # Criar gerenciador de risco
    risk_manager = RiskManager()
    
    # Gerar relatório de risco
    report = risk_manager.generate_risk_report(
        equity_curve=equity,
        portfolio_value=equity.iloc[-1],
        positions=positions,
        prices=prices
    )
    
    print("\nRelatório de Risco:")
    print("-" * 60)
    for key, value in report.items():
        if key == 'Position Sizes':
            print(f"\n{key}:")
            for ticker, size in value.items():
                print(f"  {ticker}: {size:.2%}")
        elif isinstance(value, float):
            if 'Drawdown' in key or 'Volatility' in key or 'Position' in key:
                print(f"{key:.<40} {value:>10.2%}")
            elif 'Value' in key or 'VaR' in key:
                print(f"{key:.<40} R$ {value:>10,.2f}")
            else:
                print(f"{key:.<40} {value:>10.2f}")
        else:
            print(f"{key:.<40} {value}")


if __name__ == "__main__":
    test_risk_manager()
