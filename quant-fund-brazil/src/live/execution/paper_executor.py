"""
Simulador de execução de ordens para paper trading.
Simula o comportamento real de execução de ordens com slippage e custos.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderSide(Enum):
    """Lado da ordem."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    """Status da ordem."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Order:
    """Classe representando uma ordem."""
    
    def __init__(
        self,
        ticker: str,
        side: OrderSide,
        quantity: int,
        price: float,
        order_id: Optional[str] = None
    ):
        self.order_id = order_id or str(uuid.uuid4())
        self.ticker = ticker
        self.side = side
        self.quantity = quantity
        self.price = price  # Preço de referência
        self.filled_price = None  # Preço de execução
        self.status = OrderStatus.PENDING
        self.timestamp = datetime.now()
        self.filled_timestamp = None
        self.commission = 0.0
        self.slippage = 0.0
        self.total_cost = 0.0
    
    def __repr__(self):
        return (f"Order(id={self.order_id[:8]}, {self.side.value} {self.quantity} "
                f"{self.ticker} @ R${self.price:.2f}, status={self.status.value})")


class PaperExecutor:
    """Simulador de execução de ordens para paper trading."""
    
    def __init__(
        self,
        commission_rate: float = 0.0005,  # 0.05%
        slippage_rate: float = 0.001,  # 0.1%
        min_commission: float = 3.33  # R$ 3.33 mínimo
    ):
        """
        Inicializa o executor de paper trading.
        
        Args:
            commission_rate: Taxa de corretagem (padrão: 0.05%)
            slippage_rate: Taxa de slippage (padrão: 0.1%)
            min_commission: Corretagem mínima por ordem
        """
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.min_commission = min_commission
        
        self.orders = {}  # {order_id: Order}
        self.filled_orders = []  # Lista de ordens executadas
        
        logger.info("PaperExecutor inicializado")
        logger.info(f"Corretagem: {commission_rate*100:.3f}%, Slippage: {slippage_rate*100:.2f}%")
    
    def calculate_slippage(self, price: float, side: OrderSide) -> float:
        """
        Calcula o slippage baseado no lado da ordem.
        
        Args:
            price: Preço de referência
            side: Lado da ordem (BUY/SELL)
        
        Returns:
            Preço com slippage aplicado
        """
        if side == OrderSide.BUY:
            # Compra: paga um pouco mais
            return price * (1 + self.slippage_rate)
        else:
            # Venda: recebe um pouco menos
            return price * (1 - self.slippage_rate)
    
    def calculate_commission(self, quantity: int, price: float) -> float:
        """
        Calcula a corretagem da ordem.
        
        Args:
            quantity: Quantidade de ações
            price: Preço por ação
        
        Returns:
            Valor da corretagem
        """
        total_value = quantity * price
        commission = total_value * self.commission_rate
        
        # Aplicar corretagem mínima
        return max(commission, self.min_commission)
    
    def submit_order(
        self,
        ticker: str,
        side: OrderSide,
        quantity: int,
        price: float
    ) -> Order:
        """
        Submete uma ordem para execução.
        
        Args:
            ticker: Ticker do ativo
            side: Lado da ordem (BUY/SELL)
            quantity: Quantidade de ações
            price: Preço de referência
        
        Returns:
            Objeto Order criado
        """
        order = Order(
            ticker=ticker,
            side=side,
            quantity=quantity,
            price=price
        )
        
        self.orders[order.order_id] = order
        
        logger.info(f"📝 Ordem submetida: {order}")
        
        return order
    
    def execute_order(self, order: Order) -> bool:
        """
        Executa uma ordem (simula preenchimento).
        
        Args:
            order: Ordem a ser executada
        
        Returns:
            True se executada com sucesso, False caso contrário
        """
        if order.status != OrderStatus.PENDING:
            logger.warning(f"Ordem {order.order_id} não está pendente")
            return False
        
        # Calcular preço com slippage
        filled_price = self.calculate_slippage(order.price, order.side)
        
        # Calcular corretagem
        commission = self.calculate_commission(order.quantity, filled_price)
        
        # Calcular custo total
        if order.side == OrderSide.BUY:
            total_cost = (order.quantity * filled_price) + commission
        else:
            total_cost = (order.quantity * filled_price) - commission
        
        # Atualizar ordem
        order.filled_price = filled_price
        order.commission = commission
        order.slippage = abs(filled_price - order.price)
        order.total_cost = total_cost
        order.status = OrderStatus.FILLED
        order.filled_timestamp = datetime.now()
        
        # Adicionar à lista de ordens executadas
        self.filled_orders.append(order)
        
        logger.info(f"✅ Ordem executada: {order.ticker} {order.side.value}")
        logger.info(f"   Quantidade: {order.quantity}")
        logger.info(f"   Preço ref: R$ {order.price:.2f}")
        logger.info(f"   Preço exec: R$ {filled_price:.2f}")
        logger.info(f"   Slippage: R$ {order.slippage:.2f}")
        logger.info(f"   Corretagem: R$ {commission:.2f}")
        logger.info(f"   Custo total: R$ {total_cost:.2f}")
        
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancela uma ordem pendente.
        
        Args:
            order_id: ID da ordem
        
        Returns:
            True se cancelada, False caso contrário
        """
        if order_id not in self.orders:
            logger.warning(f"Ordem {order_id} não encontrada")
            return False
        
        order = self.orders[order_id]
        
        if order.status != OrderStatus.PENDING:
            logger.warning(f"Ordem {order_id} não pode ser cancelada (status: {order.status})")
            return False
        
        order.status = OrderStatus.CANCELLED
        logger.info(f"❌ Ordem cancelada: {order_id}")
        
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Retorna uma ordem pelo ID.
        
        Args:
            order_id: ID da ordem
        
        Returns:
            Objeto Order ou None
        """
        return self.orders.get(order_id)
    
    def get_pending_orders(self) -> List[Order]:
        """
        Retorna todas as ordens pendentes.
        
        Returns:
            Lista de ordens pendentes
        """
        return [order for order in self.orders.values() 
                if order.status == OrderStatus.PENDING]
    
    def get_filled_orders(self, ticker: Optional[str] = None) -> List[Order]:
        """
        Retorna ordens executadas.
        
        Args:
            ticker: Filtrar por ticker (opcional)
        
        Returns:
            Lista de ordens executadas
        """
        if ticker:
            return [order for order in self.filled_orders if order.ticker == ticker]
        return self.filled_orders
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas de execução.
        
        Returns:
            Dicionário com estatísticas
        """
        total_orders = len(self.orders)
        filled_orders = len(self.filled_orders)
        pending_orders = len(self.get_pending_orders())
        
        total_commission = sum(order.commission for order in self.filled_orders)
        total_slippage = sum(order.slippage * order.quantity for order in self.filled_orders)
        
        stats = {
            'total_orders': total_orders,
            'filled_orders': filled_orders,
            'pending_orders': pending_orders,
            'total_commission': total_commission,
            'total_slippage': total_slippage,
            'avg_commission': total_commission / filled_orders if filled_orders > 0 else 0,
            'avg_slippage': total_slippage / filled_orders if filled_orders > 0 else 0
        }
        
        return stats
    
    def reset(self):
        """Reseta o executor (limpa todas as ordens)."""
        self.orders = {}
        self.filled_orders = []
        logger.info("Executor resetado")


def test_paper_executor():
    """Função de teste para o PaperExecutor."""
    
    # Criar executor
    executor = PaperExecutor()
    
    print("\n=== Teste de Execução de Ordens ===\n")
    
    # Submeter ordem de compra
    print("1. Submetendo ordem de COMPRA...")
    buy_order = executor.submit_order(
        ticker="PETR4.SA",
        side=OrderSide.BUY,
        quantity=100,
        price=38.50
    )
    print(f"   Ordem criada: {buy_order.order_id[:8]}")
    
    # Executar ordem
    print("\n2. Executando ordem de COMPRA...")
    executor.execute_order(buy_order)
    
    # Submeter ordem de venda
    print("\n3. Submetendo ordem de VENDA...")
    sell_order = executor.submit_order(
        ticker="VALE3.SA",
        side=OrderSide.SELL,
        quantity=50,
        price=65.20
    )
    print(f"   Ordem criada: {sell_order.order_id[:8]}")
    
    # Executar ordem
    print("\n4. Executando ordem de VENDA...")
    executor.execute_order(sell_order)
    
    # Estatísticas
    print("\n5. Estatísticas de Execução:")
    stats = executor.get_statistics()
    print(f"   Total de ordens: {stats['total_orders']}")
    print(f"   Ordens executadas: {stats['filled_orders']}")
    print(f"   Ordens pendentes: {stats['pending_orders']}")
    print(f"   Corretagem total: R$ {stats['total_commission']:.2f}")
    print(f"   Slippage total: R$ {stats['total_slippage']:.2f}")
    print(f"   Corretagem média: R$ {stats['avg_commission']:.2f}")
    
    # Listar ordens executadas
    print("\n6. Ordens Executadas:")
    for order in executor.get_filled_orders():
        print(f"   {order.ticker}: {order.side.value} {order.quantity} @ R$ {order.filled_price:.2f}")
        print(f"      Corretagem: R$ {order.commission:.2f}, Custo: R$ {order.total_cost:.2f}")


if __name__ == "__main__":
    test_paper_executor()

