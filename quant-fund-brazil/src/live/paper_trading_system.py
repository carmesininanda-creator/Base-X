"""
Sistema principal de paper trading que integra todos os módulos.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import signal
import sys

from data.realtime_data_fetcher import RealtimeDataFetcher
from signals.signal_generator import SignalGenerator
from execution.paper_executor import PaperExecutor, OrderSide
from database.trading_db import TradingDatabase
from risk.risk_manager import RiskManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PaperTradingSystem:
    """Sistema completo de paper trading."""
    
    def __init__(
        self,
        tickers: List[str],
        initial_capital: float = 100000.0,
        lookback_period: int = 63,
        top_n: int = 3,
        bottom_n: int = 3,
        rebalance_frequency: str = 'monthly',
        update_interval: int = 300  # 5 minutos
    ):
        """
        Inicializa o sistema de paper trading.
        
        Args:
            tickers: Lista de tickers para operar
            initial_capital: Capital inicial
            lookback_period: Período de lookback para momentum
            top_n: Número de ativos para comprar
            bottom_n: Número de ativos para vender
            rebalance_frequency: Frequência de rebalanceamento
            update_interval: Intervalo de atualização de dados (segundos)
        """
        self.tickers = tickers
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.rebalance_frequency = rebalance_frequency
        
        # Componentes do sistema
        self.data_fetcher = RealtimeDataFetcher(tickers, update_interval)
        self.signal_generator = SignalGenerator(
            lookback_period=lookback_period,
            top_n=top_n,
            bottom_n=bottom_n
        )
        self.executor = PaperExecutor()
        self.db = TradingDatabase("data/paper_trading.db")
        self.risk_manager = RiskManager(max_position_size=0.20)
        
        # Estado do sistema
        self.running = False
        self.last_rebalance = datetime.now() - timedelta(days=365)  # Forçar rebalanceamento inicial
        self.positions = {}  # {ticker: quantity}
        
        logger.info("PaperTradingSystem inicializado")
        logger.info(f"Tickers: {', '.join(tickers)}")
        logger.info(f"Capital inicial: R$ {initial_capital:,.2f}")
    
    def start(self):
        """Inicia o sistema."""
        logger.info("="*60)
        logger.info("INICIANDO SISTEMA DE PAPER TRADING")
        logger.info("="*60)
        
        self.running = True
        
        # Iniciar coleta de dados
        self.data_fetcher.start()
        logger.info("Coleta de dados iniciada")
        
        # Aguardar dados iniciais
        logger.info("Aguardando dados iniciais...")
        time.sleep(10)
        
        # Loop principal
        try:
            while self.running:
                self._main_loop()
                time.sleep(60)  # Verificar a cada minuto
        
        except KeyboardInterrupt:
            logger.info("Interrupção recebida, encerrando...")
        
        finally:
            self.stop()
    
    def stop(self):
        """Para o sistema."""
        logger.info("Parando sistema...")
        
        self.running = False
        self.data_fetcher.stop()
        self.db.close()
        
        logger.info("Sistema encerrado")
    
    def _main_loop(self):
        """Loop principal do sistema."""
        now = datetime.now()
        
        # Verificar se é horário de mercado (9:00 - 18:00, seg-sex)
        if not self._is_market_hours(now):
            logger.debug("Fora do horário de mercado")
            return
        
        # Atualizar preços no gerador de sinais
        self._update_signal_generator()
        
        # Verificar se deve rebalancear
        if self.signal_generator.should_rebalance(
            self.last_rebalance,
            self.rebalance_frequency
        ):
            logger.info("🔄 Iniciando rebalanceamento...")
            self._rebalance()
            self.last_rebalance = now
        
        # Atualizar posições com preços atuais
        self._update_positions()
        
        # Salvar snapshot diário (uma vez por dia)
        if self._should_save_snapshot():
            self._save_daily_snapshot()
    
    def _is_market_hours(self, dt: datetime) -> bool:
        """Verifica se está no horário de mercado."""
        # Segunda a sexta (0-4)
        if dt.weekday() > 4:
            return False
        
        # 9:00 - 18:00
        hour = dt.hour
        if hour < 9 or hour >= 18:
            return False
        
        return True
    
    def _update_signal_generator(self):
        """Atualiza o gerador de sinais com preços atuais."""
        prices = self.data_fetcher.get_latest_prices()
        
        for ticker, price in prices.items():
            if price:
                self.signal_generator.update_price_history(
                    ticker=ticker,
                    price=price,
                    timestamp=datetime.now()
                )
    
    def _rebalance(self):
        """Executa rebalanceamento do portfólio."""
        logger.info("Gerando sinais de trading...")
        
        # Gerar sinais
        signals = self.signal_generator.generate_signals(self.tickers)
        
        if not signals:
            logger.warning("Nenhum sinal gerado, pulando rebalanceamento")
            return
        
        # Obter preços atuais
        prices = self.data_fetcher.get_latest_prices()
        
        # Calcular tamanho das posições
        position_size = self.current_capital / (len([s for s in signals.values() if s in ['BUY', 'SELL']]))
        
        logger.info(f"Tamanho de posição: R$ {position_size:,.2f}")
        
        # Fechar posições antigas
        self._close_old_positions(signals, prices)
        
        # Abrir novas posições
        self._open_new_positions(signals, prices, position_size)
        
        logger.info("✅ Rebalanceamento concluído")
    
    def _close_old_positions(self, signals: Dict[str, str], prices: Dict[str, float]):
        """Fecha posições que não estão mais nos sinais."""
        for ticker, quantity in list(self.positions.items()):
            if quantity == 0:
                continue
            
            signal = signals.get(ticker, 'HOLD')
            
            # Se não deve mais ter posição, fechar
            if signal == 'HOLD':
                logger.info(f"Fechando posição: {ticker}")
                
                price = prices.get(ticker)
                if not price:
                    logger.warning(f"Sem preço para {ticker}, pulando")
                    continue
                
                # Criar ordem de fechamento
                side = OrderSide.SELL if quantity > 0 else OrderSide.BUY
                order = self.executor.submit_order(
                    ticker=ticker,
                    side=side,
                    quantity=abs(quantity),
                    price=price
                )
                
                # Executar ordem
                self.executor.execute_order(order)
                
                # Salvar no banco
                self._save_order(order)
                
                # Atualizar posição
                self.positions[ticker] = 0
                self.db.close_position(ticker)
    
    def _open_new_positions(self, signals: Dict[str, str], prices: Dict[str, float], position_size: float):
        """Abre novas posições baseadas nos sinais."""
        for ticker, signal in signals.items():
            if signal == 'HOLD':
                continue
            
            price = prices.get(ticker)
            if not price:
                logger.warning(f"Sem preço para {ticker}, pulando")
                continue
            
            # Calcular quantidade
            quantity = int(position_size / price)
            
            if quantity == 0:
                logger.warning(f"Quantidade zero para {ticker}, pulando")
                continue
            
            # Verificar risco
            if not self.risk_manager.check_position_size(quantity * price, self.current_capital):
                logger.warning(f"Posição em {ticker} excede limite de risco, reduzindo")
                max_size = self.current_capital * self.risk_manager.max_position_size
                quantity = int(max_size / price)
            
            # Criar ordem
            side = OrderSide.BUY if signal == 'BUY' else OrderSide.SELL
            
            logger.info(f"Abrindo posição: {ticker} {side.value} {quantity}")
            
            order = self.executor.submit_order(
                ticker=ticker,
                side=side,
                quantity=quantity,
                price=price
            )
            
            # Executar ordem
            self.executor.execute_order(order)
            
            # Salvar no banco
            self._save_order(order)
            
            # Atualizar posição
            current_qty = self.positions.get(ticker, 0)
            if side == OrderSide.BUY:
                self.positions[ticker] = current_qty + quantity
            else:
                self.positions[ticker] = current_qty - quantity
            
            # Salvar posição no banco
            self.db.update_position(
                ticker=ticker,
                quantity=self.positions[ticker],
                avg_price=order.filled_price,
                current_price=price
            )
    
    def _update_positions(self):
        """Atualiza posições com preços atuais."""
        prices = self.data_fetcher.get_latest_prices()
        
        for ticker, quantity in self.positions.items():
            if quantity == 0:
                continue
            
            price = prices.get(ticker)
            if price:
                # Buscar preço médio do banco
                positions = self.db.get_positions()
                pos = next((p for p in positions if p['ticker'] == ticker), None)
                
                if pos:
                    self.db.update_position(
                        ticker=ticker,
                        quantity=quantity,
                        avg_price=pos['avg_price'],
                        current_price=price
                    )
    
    def _save_order(self, order):
        """Salva ordem no banco de dados."""
        order_data = {
            'order_id': order.order_id,
            'ticker': order.ticker,
            'side': order.side.value,
            'quantity': order.quantity,
            'price': order.price,
            'filled_price': order.filled_price,
            'status': order.status.value,
            'timestamp': order.timestamp.isoformat(),
            'filled_timestamp': order.filled_timestamp.isoformat() if order.filled_timestamp else None,
            'commission': order.commission,
            'slippage': order.slippage,
            'total_cost': order.total_cost
        }
        
        self.db.save_order(order_data)
    
    def _should_save_snapshot(self) -> bool:
        """Verifica se deve salvar snapshot diário."""
        snapshots = self.db.get_daily_snapshots(days=1)
        
        if not snapshots:
            return True
        
        last_snapshot_date = snapshots[0]['date']
        today = datetime.now().date().isoformat()
        
        return last_snapshot_date != today
    
    def _save_daily_snapshot(self):
        """Salva snapshot diário do portfólio."""
        logger.info("Salvando snapshot diário...")
        
        # Calcular valor das posições
        prices = self.data_fetcher.get_latest_prices()
        positions_value = sum(
            self.positions.get(ticker, 0) * prices.get(ticker, 0)
            for ticker in self.tickers
        )
        
        # Calcular P&L
        total_pnl = positions_value + self.current_capital - self.initial_capital
        
        # Buscar snapshot anterior para P&L diário
        snapshots = self.db.get_daily_snapshots(days=1)
        prev_value = snapshots[0]['portfolio_value'] if snapshots else self.initial_capital
        daily_pnl = (positions_value + self.current_capital) - prev_value
        
        # Estatísticas de ordens
        stats = self.executor.get_statistics()
        
        snapshot = {
            'date': datetime.now().date().isoformat(),
            'portfolio_value': positions_value + self.current_capital,
            'cash': self.current_capital,
            'positions_value': positions_value,
            'daily_pnl': daily_pnl,
            'total_pnl': total_pnl,
            'num_trades': stats['filled_orders'],
            'total_commission': stats['total_commission']
        }
        
        self.db.save_daily_snapshot(snapshot)
        logger.info(f"✅ Snapshot salvo: Valor = R$ {snapshot['portfolio_value']:,.2f}")


def main():
    """Função principal."""
    # Configuração
    TICKERS = [
        'PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA',
        'ABEV3.SA', 'WEGE3.SA', 'RENT3.SA', 'GGBR4.SA'
    ]
    
    # Criar sistema
    system = PaperTradingSystem(
        tickers=TICKERS,
        initial_capital=100000.0,
        lookback_period=63,
        top_n=3,
        bottom_n=3,
        rebalance_frequency='monthly',
        update_interval=300
    )
    
    # Configurar handler de sinal para Ctrl+C
    def signal_handler(sig, frame):
        logger.info("\nEncerrando sistema...")
        system.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Iniciar sistema
    system.start()


if __name__ == "__main__":
    main()

