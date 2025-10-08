"""
Módulo de estratégias para o projeto de fundo quantitativo.
"""

from .base_strategy import BaseStrategy
from .momentum_strategy import MomentumStrategy

__all__ = ['BaseStrategy', 'MomentumStrategy']
