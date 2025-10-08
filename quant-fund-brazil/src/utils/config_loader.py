"""
Módulo para carregar e gerenciar configurações do projeto.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Classe para carregar e gerenciar configurações do projeto."""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o carregador de configuração.
        
        Args:
            config_path: Caminho para o arquivo de configuração YAML.
                        Se None, usa o caminho padrão.
        """
        if config_path is None:
            # Caminho padrão relativo à raiz do projeto
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Carrega o arquivo de configuração YAML.
        
        Returns:
            Dicionário com as configurações.
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração.
        
        Args:
            key: Chave da configuração (pode usar notação de ponto, ex: 'data.universe').
            default: Valor padrão se a chave não existir.
        
        Returns:
            Valor da configuração ou o valor padrão.
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_data_config(self) -> Dict[str, Any]:
        """Retorna as configurações de dados."""
        return self.config.get('data', {})
    
    def get_backtesting_config(self) -> Dict[str, Any]:
        """Retorna as configurações de backtesting."""
        return self.config.get('backtesting', {})
    
    def get_risk_config(self) -> Dict[str, Any]:
        """Retorna as configurações de gestão de risco."""
        return self.config.get('risk', {})
    
    def get_strategy_config(self) -> Dict[str, Any]:
        """Retorna as configurações de estratégia."""
        return self.config.get('strategy', {})
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Retorna as configurações de monitoramento."""
        return self.config.get('monitoring', {})


# Instância global do carregador de configuração
config_loader = ConfigLoader()
