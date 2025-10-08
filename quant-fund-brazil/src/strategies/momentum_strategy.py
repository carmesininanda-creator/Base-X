"""
Estratégia de Momentum para o mercado brasileiro.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import logging
from .base_strategy import BaseStrategy

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MomentumStrategy(BaseStrategy):
    """
    Estratégia de Momentum baseada em retornos passados.
    
    A estratégia ranqueia os ativos pelo seu retorno no período de lookback
    e compra os top N ativos (maior retorno) e vende os bottom N ativos (menor retorno).
    """
    
    def __init__(
        self,
        lookback_period: int = 63,
        top_n: int = 5,
        bottom_n: int = 5,
        rebalance_frequency: str = "monthly"
    ):
        """
        Inicializa a estratégia de momentum.
        
        Args:
            lookback_period: Período de lookback em dias (padrão: 63 dias ≈ 3 meses)
            top_n: Número de ativos para comprar (maior momentum)
            bottom_n: Número de ativos para vender (menor momentum)
            rebalance_frequency: Frequência de rebalanceamento ('daily', 'weekly', 'monthly')
        """
        parameters = {
            'lookback_period': lookback_period,
            'top_n': top_n,
            'bottom_n': bottom_n,
            'rebalance_frequency': rebalance_frequency
        }
        super().__init__(name="Momentum Strategy", parameters=parameters)
        
        self.lookback_period = lookback_period
        self.top_n = top_n
        self.bottom_n = bottom_n
        self.rebalance_frequency = rebalance_frequency
    
    def calculate_momentum(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula o momentum (retorno) para cada ativo.
        
        Args:
            data: DataFrame com dados de mercado (MultiIndex: Date, Ticker)
        
        Returns:
            DataFrame com o momentum calculado
        """
        logger.info("Calculando momentum...")
        
        # Calcular retorno do período de lookback para cada ativo
        momentum = pd.DataFrame(index=data.index)
        
        # Agrupar por ticker e calcular retorno
        for ticker in data.index.get_level_values('Ticker').unique():
            ticker_data = data.xs(ticker, level='Ticker')
            
            # Calcular retorno do período
            returns = ticker_data['Close'].pct_change(periods=self.lookback_period)
            
            # Adicionar ao DataFrame de momentum
            for date in returns.index:
                momentum.loc[(date, ticker), 'Momentum'] = returns.loc[date]
        
        return momentum
    
    def rank_assets(self, momentum: pd.DataFrame, date: pd.Timestamp) -> pd.Series:
        """
        Ranqueia os ativos por momentum em uma data específica.
        
        Args:
            momentum: DataFrame com momentum calculado
            date: Data para ranqueamento
        
        Returns:
            Series com o ranking dos ativos
        """
        try:
            day_momentum = momentum.xs(date, level='Date')
            # Remover NaN e rankear
            day_momentum = day_momentum.dropna()
            ranked = day_momentum['Momentum'].rank(ascending=False)
            return ranked
        except KeyError:
            return pd.Series()
    
    def should_rebalance(self, date: pd.Timestamp, last_rebalance: pd.Timestamp = None) -> bool:
        """
        Determina se deve rebalancear a carteira na data especificada.
        
        Args:
            date: Data atual
            last_rebalance: Data do último rebalanceamento
        
        Returns:
            True se deve rebalancear, False caso contrário
        """
        if last_rebalance is None:
            return True
        
        if self.rebalance_frequency == "daily":
            return True
        elif self.rebalance_frequency == "weekly":
            return (date - last_rebalance).days >= 7
        elif self.rebalance_frequency == "monthly":
            return date.month != last_rebalance.month
        else:
            return False
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Gera sinais de trading baseados na estratégia de momentum.
        
        Args:
            data: DataFrame com dados de mercado (MultiIndex: Date, Ticker)
        
        Returns:
            DataFrame com sinais (1: compra, -1: venda, 0: neutro)
        """
        logger.info(f"Gerando sinais para estratégia de momentum...")
        
        # Validar dados
        if not self.validate_data(data):
            raise ValueError("Dados inválidos")
        
        # Calcular momentum
        momentum = self.calculate_momentum(data)
        
        # Inicializar DataFrame de sinais
        signals = pd.DataFrame(index=data.index, columns=['Signal'])
        signals['Signal'] = 0
        
        # Obter datas únicas
        dates = data.index.get_level_values('Date').unique().sort_values()
        
        # Pular as primeiras datas (período de lookback)
        dates = dates[self.lookback_period:]
        
        last_rebalance = None
        current_longs = set()
        current_shorts = set()
        
        for date in dates:
            # Verificar se deve rebalancear
            if self.should_rebalance(date, last_rebalance):
                # Rankear ativos
                ranked = self.rank_assets(momentum, date)
                
                if len(ranked) > 0:
                    # Identificar top e bottom ativos
                    new_longs = set(ranked.nsmallest(self.top_n).index)
                    new_shorts = set(ranked.nlargest(self.bottom_n).index)
                    
                    # Gerar sinais de saída para posições antigas
                    for ticker in current_longs:
                        if ticker not in new_longs:
                            signals.loc[(date, ticker), 'Signal'] = -1  # Vender
                    
                    for ticker in current_shorts:
                        if ticker not in new_shorts:
                            signals.loc[(date, ticker), 'Signal'] = 1  # Comprar para fechar short
                    
                    # Gerar sinais de entrada para novas posições
                    for ticker in new_longs:
                        if ticker not in current_longs:
                            signals.loc[(date, ticker), 'Signal'] = 1  # Comprar
                    
                    for ticker in new_shorts:
                        if ticker not in current_shorts:
                            signals.loc[(date, ticker), 'Signal'] = -1  # Vender (short)
                    
                    # Atualizar posições atuais
                    current_longs = new_longs
                    current_shorts = new_shorts
                    last_rebalance = date
                    
                    logger.debug(f"Rebalanceamento em {date}: {len(new_longs)} longs, {len(new_shorts)} shorts")
        
        logger.info(f"Sinais gerados. Total de sinais não-zero: {(signals['Signal'] != 0).sum()}")
        
        return signals


def test_momentum_strategy():
    """Função de teste para a MomentumStrategy."""
    # Criar dados de teste
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    tickers = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA']
    
    # Simular dados de preço com tendências diferentes
    data_list = []
    np.random.seed(42)
    
    for ticker in tickers:
        # Criar uma tendência diferente para cada ativo
        trend = np.random.randn() * 0.001
        prices = 30 * (1 + trend) ** np.arange(len(dates)) + np.random.randn(len(dates)) * 0.5
        
        for i, date in enumerate(dates):
            data_list.append({
                'Date': date,
                'Ticker': ticker,
                'Close': prices[i]
            })
    
    data = pd.DataFrame(data_list).set_index(['Date', 'Ticker'])
    
    # Criar estratégia
    strategy = MomentumStrategy(
        lookback_period=63,
        top_n=2,
        bottom_n=2,
        rebalance_frequency="monthly"
    )
    
    # Gerar sinais
    signals = strategy.generate_signals(data)
    
    print("\nPrimeiros sinais:")
    print(signals[signals['Signal'] != 0].head(20))
    
    print(f"\nTotal de sinais de compra: {(signals['Signal'] == 1).sum()}")
    print(f"Total de sinais de venda: {(signals['Signal'] == -1).sum()}")


if __name__ == "__main__":
    test_momentum_strategy()
