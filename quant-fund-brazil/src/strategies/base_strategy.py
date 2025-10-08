"""
Classe base para estratégias de investimento.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """Classe abstrata base para todas as estratégias."""
    
    def __init__(self, name: str, parameters: Dict[str, Any] = None):
        """
        Inicializa a estratégia.
        
        Args:
            name: Nome da estratégia
            parameters: Dicionário com parâmetros da estratégia
        """
        self.name = name
        self.parameters = parameters or {}
        logger.info(f"Estratégia '{name}' inicializada com parâmetros: {self.parameters}")
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Gera sinais de trading baseados nos dados de mercado.
        
        Args:
            data: DataFrame com dados de mercado (MultiIndex: Date, Ticker)
        
        Returns:
            DataFrame com sinais (1: compra, -1: venda, 0: neutro)
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Valida se os dados estão no formato correto.
        
        Args:
            data: DataFrame com dados de mercado
        
        Returns:
            True se os dados são válidos, False caso contrário
        """
        if not isinstance(data.index, pd.MultiIndex):
            logger.error("Dados devem ter MultiIndex (Date, Ticker)")
            return False
        
        if 'Close' not in data.columns:
            logger.error("Dados devem conter coluna 'Close'")
            return False
        
        return True
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """
        Obtém um parâmetro da estratégia.
        
        Args:
            key: Chave do parâmetro
            default: Valor padrão se o parâmetro não existir
        
        Returns:
            Valor do parâmetro
        """
        return self.parameters.get(key, default)
    
    def set_parameter(self, key: str, value: Any):
        """
        Define um parâmetro da estratégia.
        
        Args:
            key: Chave do parâmetro
            value: Valor do parâmetro
        """
        self.parameters[key] = value
        logger.info(f"Parâmetro '{key}' atualizado para: {value}")
    
    def __str__(self) -> str:
        """Representação em string da estratégia."""
        return f"{self.name} (Parâmetros: {self.parameters})"
    
    def __repr__(self) -> str:
        """Representação da estratégia."""
        return self.__str__()
