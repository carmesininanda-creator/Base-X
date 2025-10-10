"""
Motor de geração de sinais em tempo real para estratégias quantitativas.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """Classe para gerar sinais de trading em tempo real."""
    
    def __init__(
        self,
        strategy_name: str = "momentum",
        lookback_period: int = 63,
        top_n: int = 3,
        bottom_n: int = 3,
        min_data_points: int = 20
    ):
        """
        Inicializa o gerador de sinais.
        
        Args:
            strategy_name: Nome da estratégia
            lookback_period: Período de lookback em dias
            top_n: Número de ativos para comprar (long)
            bottom_n: Número de ativos para vender (short)
            min_data_points: Mínimo de pontos de dados necessários
        """
        self.strategy_name = strategy_name
        self.lookback_period = lookback_period
        self.top_n = top_n
        self.bottom_n = bottom_n
        self.min_data_points = min_data_points
        
        # Cache de dados históricos
        self.price_history = {}
        
        logger.info(f"SignalGenerator inicializado: {strategy_name}")
        logger.info(f"Lookback: {lookback_period} dias, Top: {top_n}, Bottom: {bottom_n}")
    
    def update_price_history(self, ticker: str, price: float, timestamp: datetime):
        """
        Atualiza o histórico de preços de um ticker.
        
        Args:
            ticker: Ticker do ativo
            price: Preço atual
            timestamp: Timestamp do preço
        """
        if ticker not in self.price_history:
            self.price_history[ticker] = []
        
        self.price_history[ticker].append({
            'timestamp': timestamp,
            'price': price
        })
        
        # Manter apenas dados necessários (lookback + buffer)
        max_points = self.lookback_period + 30
        if len(self.price_history[ticker]) > max_points:
            self.price_history[ticker] = self.price_history[ticker][-max_points:]
    
    def calculate_momentum(self, ticker: str) -> Optional[float]:
        """
        Calcula o momentum de um ticker.
        
        Args:
            ticker: Ticker do ativo
        
        Returns:
            Momentum (retorno percentual) ou None se dados insuficientes
        """
        if ticker not in self.price_history:
            logger.warning(f"Sem histórico para {ticker}")
            return None
        
        history = self.price_history[ticker]
        
        if len(history) < self.min_data_points:
            logger.warning(f"Dados insuficientes para {ticker}: {len(history)} pontos")
            return None
        
        # Pegar preço atual e preço de lookback dias atrás
        current_price = history[-1]['price']
        
        # Encontrar preço mais próximo de lookback dias atrás
        target_date = history[-1]['timestamp'] - timedelta(days=self.lookback_period)
        
        # Encontrar o preço mais próximo da data alvo
        lookback_price = None
        min_diff = float('inf')
        
        for entry in history:
            diff = abs((entry['timestamp'] - target_date).total_seconds())
            if diff < min_diff:
                min_diff = diff
                lookback_price = entry['price']
        
        if lookback_price is None or lookback_price == 0:
            logger.warning(f"Preço de lookback inválido para {ticker}")
            return None
        
        # Calcular retorno percentual
        momentum = ((current_price - lookback_price) / lookback_price) * 100
        
        logger.debug(f"{ticker}: Momentum = {momentum:.2f}%")
        
        return momentum
    
    def rank_assets(self, tickers: List[str]) -> List[Tuple[str, float]]:
        """
        Ranqueia ativos por momentum.
        
        Args:
            tickers: Lista de tickers
        
        Returns:
            Lista de tuplas (ticker, momentum) ordenada por momentum (maior para menor)
        """
        rankings = []
        
        for ticker in tickers:
            momentum = self.calculate_momentum(ticker)
            if momentum is not None:
                rankings.append((ticker, momentum))
        
        # Ordenar por momentum (maior para menor)
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Rankings calculados para {len(rankings)} ativos")
        for i, (ticker, momentum) in enumerate(rankings[:5], 1):
            logger.info(f"  {i}. {ticker}: {momentum:+.2f}%")
        
        return rankings
    
    def generate_signals(self, tickers: List[str]) -> Dict[str, str]:
        """
        Gera sinais de trading para todos os tickers.
        
        Args:
            tickers: Lista de tickers
        
        Returns:
            Dicionário {ticker: signal} onde signal é 'BUY', 'SELL' ou 'HOLD'
        """
        logger.info(f"Gerando sinais para {len(tickers)} ativos...")
        
        # Ranquear ativos
        rankings = self.rank_assets(tickers)
        
        if len(rankings) == 0:
            logger.warning("Nenhum ranking disponível, sem sinais gerados")
            return {}
        
        signals = {}
        
        # Top N: BUY (long)
        for i in range(min(self.top_n, len(rankings))):
            ticker = rankings[i][0]
            signals[ticker] = 'BUY'
            logger.info(f"✅ SINAL: {ticker} = BUY (momentum: {rankings[i][1]:+.2f}%)")
        
        # Bottom N: SELL (short)
        for i in range(max(0, len(rankings) - self.bottom_n), len(rankings)):
            ticker = rankings[i][0]
            signals[ticker] = 'SELL'
            logger.info(f"❌ SINAL: {ticker} = SELL (momentum: {rankings[i][1]:+.2f}%)")
        
        # Resto: HOLD
        for ticker, momentum in rankings:
            if ticker not in signals:
                signals[ticker] = 'HOLD'
        
        logger.info(f"Sinais gerados: {len([s for s in signals.values() if s == 'BUY'])} BUY, "
                   f"{len([s for s in signals.values() if s == 'SELL'])} SELL, "
                   f"{len([s for s in signals.values() if s == 'HOLD'])} HOLD")
        
        return signals
    
    def get_signal_details(self, tickers: List[str]) -> pd.DataFrame:
        """
        Retorna detalhes completos dos sinais em formato DataFrame.
        
        Args:
            tickers: Lista de tickers
        
        Returns:
            DataFrame com colunas: ticker, momentum, rank, signal
        """
        rankings = self.rank_assets(tickers)
        signals = self.generate_signals(tickers)
        
        data = []
        for rank, (ticker, momentum) in enumerate(rankings, 1):
            data.append({
                'ticker': ticker,
                'momentum': momentum,
                'rank': rank,
                'signal': signals.get(ticker, 'HOLD')
            })
        
        df = pd.DataFrame(data)
        return df
    
    def should_rebalance(self, last_rebalance: datetime, frequency: str = 'monthly') -> bool:
        """
        Verifica se deve fazer rebalanceamento.
        
        Args:
            last_rebalance: Data do último rebalanceamento
            frequency: Frequência ('daily', 'weekly', 'monthly')
        
        Returns:
            True se deve rebalancear, False caso contrário
        """
        now = datetime.now()
        
        if frequency == 'daily':
            # Rebalancear se for um novo dia
            return now.date() > last_rebalance.date()
        
        elif frequency == 'weekly':
            # Rebalancear toda segunda-feira
            if now.weekday() == 0:  # 0 = segunda
                days_since = (now - last_rebalance).days
                return days_since >= 7
            return False
        
        elif frequency == 'monthly':
            # Rebalancear no primeiro dia útil do mês
            if now.month != last_rebalance.month:
                # Verificar se é dia útil (seg-sex)
                if now.weekday() < 5:  # 0-4 = seg-sex
                    return True
            return False
        
        else:
            logger.error(f"Frequência inválida: {frequency}")
            return False
    
    def clear_history(self):
        """Limpa todo o histórico de preços."""
        self.price_history = {}
        logger.info("Histórico de preços limpo")
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do gerador de sinais.
        
        Returns:
            Dicionário com estatísticas
        """
        stats = {
            'strategy': self.strategy_name,
            'lookback_period': self.lookback_period,
            'top_n': self.top_n,
            'bottom_n': self.bottom_n,
            'tickers_tracked': len(self.price_history),
            'data_points': {
                ticker: len(history)
                for ticker, history in self.price_history.items()
            }
        }
        
        return stats


def test_signal_generator():
    """Função de teste para o SignalGenerator."""
    import yfinance as yf
    
    # Criar gerador
    generator = SignalGenerator(
        lookback_period=63,
        top_n=3,
        bottom_n=3
    )
    
    # Tickers de teste
    tickers = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA']
    
    print("\n=== Carregando dados históricos ===")
    
    # Carregar dados históricos
    for ticker in tickers:
        print(f"Carregando {ticker}...")
        data = yf.download(ticker, period='6mo', progress=False)
        
        if not data.empty:
            for date, row in data.iterrows():
                generator.update_price_history(
                    ticker=ticker,
                    price=float(row['Close']),
                    timestamp=pd.Timestamp(date).to_pydatetime()
                )
    
    print("\n=== Calculando momentum ===")
    
    # Calcular momentum
    for ticker in tickers:
        momentum = generator.calculate_momentum(ticker)
        if momentum:
            print(f"{ticker}: {momentum:+.2f}%")
    
    print("\n=== Gerando sinais ===")
    
    # Gerar sinais
    signals = generator.generate_signals(tickers)
    
    print("\n=== Detalhes dos sinais ===")
    
    # Mostrar detalhes
    df = generator.get_signal_details(tickers)
    print(df.to_string(index=False))
    
    print("\n=== Estatísticas ===")
    
    # Mostrar estatísticas
    stats = generator.get_statistics()
    print(f"Estratégia: {stats['strategy']}")
    print(f"Lookback: {stats['lookback_period']} dias")
    print(f"Ativos rastreados: {stats['tickers_tracked']}")


if __name__ == "__main__":
    test_signal_generator()

