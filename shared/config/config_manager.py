"""
Config Manager - Singleton Pattern
Loads and manages configuration from settings.yaml
"""

import yaml
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    """Risk management configuration"""
    circuit_breaker: Dict[str, float]
    correlation_threshold: float
    max_portfolio_correlation: float
    kelly: Dict[str, float]
    sharpe_target: float
    max_drawdown_tolerance: float


@dataclass
class TradingConfig:
    """Trading configuration"""
    initial_capital: float
    trading_interval: int
    max_position_size: float
    min_position_size: float
    max_open_positions: int


@dataclass
class ExecutionConfig:
    """Execution configuration"""
    slippage_model: str
    commission_percent: float
    market_impact_percent: float
    order_types: Dict[str, bool]
    simulation: Dict[str, Any]


class ConfigManager:
    """
    Singleton Configuration Manager
    Loads config.yaml from root and provides typed access to config    """
    
    _instance = None
    _config = None
    
    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance
    
    def _load_config(self, config_path: Optional[str] = None):
        """Load configuration from YAML file"""
        
        if config_path is None:
            # Default path
config_path = Path(__file__).parents[2] / "config.yaml"        else:
            config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        logger.info(f"✓ Configuration loaded from {config_path}")
        
        # Load environment variables
        self._load_env_vars()
    
    def _load_env_vars(self):
        """Load sensitive values from environment variables"""
        
        # Database password
        if 'POSTGRES_PASSWORD' in os.environ:
            self._config['state_persistence']['storage']['password'] = \
                os.environ['POSTGRES_PASSWORD']
        
        # API keys
        if 'POLYMARKET_API_KEY' in os.environ:
            self._config['markets']['polymarket']['api_key'] = \
                os.environ['POLYMARKET_API_KEY']
    
    @property
    def system(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self._config['system']
    
    @property
    def trading(self) -> TradingConfig:
        """Get trading configuration"""
        cfg = self._config['trading']
        return TradingConfig(
            initial_capital=cfg['initial_capital'],
            trading_interval=cfg['trading_interval'],
            max_position_size=cfg['max_position_size'],
            min_position_size=cfg['min_position_size'],
            max_open_positions=cfg['max_open_positions']
        )
    
    @property
    def risk(self) -> RiskConfig:
        """Get risk configuration"""
        cfg = self._config['risk']
        return RiskConfig(
            circuit_breaker=cfg['circuit_breaker'],
            correlation_threshold=cfg['correlation_threshold'],
            max_portfolio_correlation=cfg['max_portfolio_correlation'],
            kelly=cfg['kelly'],
            sharpe_target=cfg['sharpe_target'],
            max_drawdown_tolerance=cfg['max_drawdown_tolerance']
        )
    
    @property
    def execution(self) -> ExecutionConfig:
        """Get execution configuration"""
        cfg = self._config['execution']
        return ExecutionConfig(
            slippage_model=cfg['slippage_model'],
            commission_percent=cfg['commission_percent'],
            market_impact_percent=cfg['market_impact_percent'],
            order_types=cfg['order_types'],
            simulation=cfg['simulation']
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def reload(self):
        """Reload configuration from file"""
        self._load_config()
        logger.info("✓ Configuration reloaded")


# Singleton instance
config = ConfigManager()

