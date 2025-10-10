"""
Sistema de persistência de dados para paper trading.
Usa SQLite para armazenar histórico de ordens, posições e performance.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingDatabase:
    """Classe para gerenciar o banco de dados de trading."""
    
    def __init__(self, db_path: str = "data/trading.db"):
        """
        Inicializa o banco de dados.
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        # Criar diretório se não existir
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.conn = None
        
        self._connect()
        self._create_tables()
        
        logger.info(f"TradingDatabase inicializado: {db_path}")
    
    def _connect(self):
        """Conecta ao banco de dados."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Retornar resultados como dicionários
        logger.debug(f"Conectado ao banco: {self.db_path}")
    
    def _create_tables(self):
        """Cria as tabelas necessárias."""
        cursor = self.conn.cursor()
        
        # Tabela de ordens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                ticker TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                filled_price REAL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                filled_timestamp TEXT,
                commission REAL DEFAULT 0,
                slippage REAL DEFAULT 0,
                total_cost REAL DEFAULT 0
            )
        """)
        
        # Tabela de posições
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL DEFAULT 0,
                timestamp TEXT NOT NULL,
                UNIQUE(ticker)
            )
        """)
        
        # Tabela de snapshots diários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                portfolio_value REAL NOT NULL,
                cash REAL NOT NULL,
                positions_value REAL NOT NULL,
                daily_pnl REAL DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                num_trades INTEGER DEFAULT 0,
                total_commission REAL DEFAULT 0,
                metadata TEXT
            )
        """)
        
        # Tabela de métricas de risco
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                var_95 REAL,
                volatility REAL,
                max_drawdown REAL,
                sharpe_ratio REAL,
                max_position_size REAL,
                leverage REAL,
                metadata TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("Tabelas criadas/verificadas")
    
    def save_order(self, order_data: Dict):
        """
        Salva uma ordem no banco de dados.
        
        Args:
            order_data: Dicionário com dados da ordem
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO orders (
                order_id, ticker, side, quantity, price, filled_price,
                status, timestamp, filled_timestamp, commission, slippage, total_cost
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data['order_id'],
            order_data['ticker'],
            order_data['side'],
            order_data['quantity'],
            order_data['price'],
            order_data.get('filled_price'),
            order_data['status'],
            order_data['timestamp'],
            order_data.get('filled_timestamp'),
            order_data.get('commission', 0),
            order_data.get('slippage', 0),
            order_data.get('total_cost', 0)
        ))
        
        self.conn.commit()
        logger.debug(f"Ordem salva: {order_data['order_id']}")
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """
        Recupera uma ordem pelo ID.
        
        Args:
            order_id: ID da ordem
        
        Returns:
            Dicionário com dados da ordem ou None
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_orders(
        self,
        ticker: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Recupera ordens com filtros opcionais.
        
        Args:
            ticker: Filtrar por ticker
            status: Filtrar por status
            limit: Limite de resultados
        
        Returns:
            Lista de dicionários com dados das ordens
        """
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def update_position(self, ticker: str, quantity: int, avg_price: float, current_price: float = None):
        """
        Atualiza uma posição no portfólio.
        
        Args:
            ticker: Ticker do ativo
            quantity: Quantidade de ações
            avg_price: Preço médio de compra
            current_price: Preço atual (opcional)
        """
        cursor = self.conn.cursor()
        
        unrealized_pnl = 0
        if current_price:
            unrealized_pnl = (current_price - avg_price) * quantity
        
        cursor.execute("""
            INSERT OR REPLACE INTO positions (
                ticker, quantity, avg_price, current_price, unrealized_pnl, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            quantity,
            avg_price,
            current_price,
            unrealized_pnl,
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        logger.debug(f"Posição atualizada: {ticker}")
    
    def get_positions(self) -> List[Dict]:
        """
        Recupera todas as posições atuais.
        
        Returns:
            Lista de dicionários com dados das posições
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE quantity != 0 ORDER BY ticker")
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def close_position(self, ticker: str):
        """
        Fecha uma posição (zera quantidade).
        
        Args:
            ticker: Ticker do ativo
        """
        cursor = self.conn.cursor()
        cursor.execute("UPDATE positions SET quantity = 0 WHERE ticker = ?", (ticker,))
        self.conn.commit()
        logger.info(f"Posição fechada: {ticker}")
    
    def save_daily_snapshot(self, snapshot_data: Dict):
        """
        Salva um snapshot diário do portfólio.
        
        Args:
            snapshot_data: Dicionário com dados do snapshot
        """
        cursor = self.conn.cursor()
        
        metadata = json.dumps(snapshot_data.get('metadata', {}))
        
        cursor.execute("""
            INSERT OR REPLACE INTO daily_snapshots (
                date, portfolio_value, cash, positions_value,
                daily_pnl, total_pnl, num_trades, total_commission, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_data['date'],
            snapshot_data['portfolio_value'],
            snapshot_data['cash'],
            snapshot_data['positions_value'],
            snapshot_data.get('daily_pnl', 0),
            snapshot_data.get('total_pnl', 0),
            snapshot_data.get('num_trades', 0),
            snapshot_data.get('total_commission', 0),
            metadata
        ))
        
        self.conn.commit()
        logger.info(f"Snapshot diário salvo: {snapshot_data['date']}")
    
    def get_daily_snapshots(self, days: int = 30) -> List[Dict]:
        """
        Recupera snapshots diários.
        
        Args:
            days: Número de dias para recuperar
        
        Returns:
            Lista de dicionários com dados dos snapshots
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM daily_snapshots
            ORDER BY date DESC
            LIMIT ?
        """, (days,))
        rows = cursor.fetchall()
        
        snapshots = []
        for row in rows:
            snapshot = dict(row)
            if snapshot.get('metadata'):
                snapshot['metadata'] = json.loads(snapshot['metadata'])
            snapshots.append(snapshot)
        
        return snapshots
    
    def save_risk_metrics(self, metrics_data: Dict):
        """
        Salva métricas de risco.
        
        Args:
            metrics_data: Dicionário com métricas de risco
        """
        cursor = self.conn.cursor()
        
        metadata = json.dumps(metrics_data.get('metadata', {}))
        
        cursor.execute("""
            INSERT INTO risk_metrics (
                timestamp, var_95, volatility, max_drawdown,
                sharpe_ratio, max_position_size, leverage, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            metrics_data.get('var_95'),
            metrics_data.get('volatility'),
            metrics_data.get('max_drawdown'),
            metrics_data.get('sharpe_ratio'),
            metrics_data.get('max_position_size'),
            metrics_data.get('leverage'),
            metadata
        ))
        
        self.conn.commit()
        logger.debug("Métricas de risco salvas")
    
    def get_latest_risk_metrics(self) -> Optional[Dict]:
        """
        Recupera as métricas de risco mais recentes.
        
        Returns:
            Dicionário com métricas ou None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM risk_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if row:
            metrics = dict(row)
            if metrics.get('metadata'):
                metrics['metadata'] = json.loads(metrics['metadata'])
            return metrics
        return None
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas gerais do banco de dados.
        
        Returns:
            Dicionário com estatísticas
        """
        cursor = self.conn.cursor()
        
        # Total de ordens
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        total_orders = cursor.fetchone()['count']
        
        # Ordens executadas
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'FILLED'")
        filled_orders = cursor.fetchone()['count']
        
        # Posições abertas
        cursor.execute("SELECT COUNT(*) as count FROM positions WHERE quantity != 0")
        open_positions = cursor.fetchone()['count']
        
        # Total de comissões
        cursor.execute("SELECT SUM(commission) as total FROM orders WHERE status = 'FILLED'")
        total_commission = cursor.fetchone()['total'] or 0
        
        # Snapshots salvos
        cursor.execute("SELECT COUNT(*) as count FROM daily_snapshots")
        total_snapshots = cursor.fetchone()['count']
        
        return {
            'total_orders': total_orders,
            'filled_orders': filled_orders,
            'open_positions': open_positions,
            'total_commission': total_commission,
            'total_snapshots': total_snapshots
        }
    
    def clear_all_data(self):
        """Limpa todos os dados do banco (CUIDADO!)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM positions")
        cursor.execute("DELETE FROM daily_snapshots")
        cursor.execute("DELETE FROM risk_metrics")
        self.conn.commit()
        logger.warning("Todos os dados foram limpos!")
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()
            logger.info("Conexão com banco fechada")


def test_trading_database():
    """Função de teste para o TradingDatabase."""
    import os
    
    # Usar banco de teste
    test_db = "data/test_trading.db"
    
    # Remover banco de teste se existir
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Criar banco
    db = TradingDatabase(test_db)
    
    print("\n=== Teste do Banco de Dados ===\n")
    
    # 1. Salvar ordem
    print("1. Salvando ordem...")
    order_data = {
        'order_id': 'test-001',
        'ticker': 'PETR4.SA',
        'side': 'BUY',
        'quantity': 100,
        'price': 38.50,
        'filled_price': 38.54,
        'status': 'FILLED',
        'timestamp': datetime.now().isoformat(),
        'filled_timestamp': datetime.now().isoformat(),
        'commission': 3.33,
        'slippage': 0.04,
        'total_cost': 3857.18
    }
    db.save_order(order_data)
    print("   ✅ Ordem salva")
    
    # 2. Recuperar ordem
    print("\n2. Recuperando ordem...")
    order = db.get_order('test-001')
    print(f"   Ticker: {order['ticker']}")
    print(f"   Quantidade: {order['quantity']}")
    print(f"   Preço: R$ {order['filled_price']:.2f}")
    
    # 3. Atualizar posição
    print("\n3. Atualizando posição...")
    db.update_position('PETR4.SA', 100, 38.54, 39.00)
    print("   ✅ Posição atualizada")
    
    # 4. Listar posições
    print("\n4. Listando posições...")
    positions = db.get_positions()
    for pos in positions:
        print(f"   {pos['ticker']}: {pos['quantity']} ações @ R$ {pos['avg_price']:.2f}")
        print(f"      P&L não realizado: R$ {pos['unrealized_pnl']:.2f}")
    
    # 5. Salvar snapshot
    print("\n5. Salvando snapshot diário...")
    snapshot = {
        'date': datetime.now().date().isoformat(),
        'portfolio_value': 103900.00,
        'cash': 100000.00,
        'positions_value': 3900.00,
        'daily_pnl': 46.00,
        'total_pnl': 46.00,
        'num_trades': 1,
        'total_commission': 3.33
    }
    db.save_daily_snapshot(snapshot)
    print("   ✅ Snapshot salvo")
    
    # 6. Estatísticas
    print("\n6. Estatísticas do banco:")
    stats = db.get_statistics()
    print(f"   Total de ordens: {stats['total_orders']}")
    print(f"   Ordens executadas: {stats['filled_orders']}")
    print(f"   Posições abertas: {stats['open_positions']}")
    print(f"   Comissão total: R$ {stats['total_commission']:.2f}")
    print(f"   Snapshots salvos: {stats['total_snapshots']}")
    
    # Fechar banco
    db.close()
    
    print("\n✅ Teste concluído!")


if __name__ == "__main__":
    test_trading_database()

