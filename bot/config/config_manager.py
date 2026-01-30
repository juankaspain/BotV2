"""
Config Manager - Singleton Pattern
Loads and manages configuration from config.yaml or settings.yaml
"""

import yaml
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Default configuration for demo mode
DEFAULT_CONFIG = {
    'system': {
        'name': 'BotV2',
        'version': '2.0.0',
        'environment': 'demo',
        'log_level': 'INFO'
    },
    'trading': {
        'initial_capital': 10000.0,
        'trading_interval': 60,
        'max_position_size': 0.1,
        'min_position_size': 0.01,
        'max_open_positions': 5
    },
    'risk': {
        'circuit_breaker': {
            'daily_loss_limit': 0.05,
            'consecutive_losses': 5,
            'cooldown_minutes': 60
        },
        'correlation_threshold': 0.7,
        'max_portfolio_correlation': 0.8,
        'kelly': {
            'fraction': 0.25,
            'max_bet': 0.1
        },
        'sharpe_target': 1.5,
        'max_drawdown_tolerance': 0.15
    },
    'execution': {
        'slippage_model': 'fixed',
        'commission_percent': 0.001,
        'market_impact_percent': 0.0005,
        'order_types': {
            'market': True,
            'limit': True,
            'stop': True
        },
        'simulation': {
            'enabled': True,
            'latency_ms': 100
        }
    },
    'data': {
        'validation': {
            'outlier_std_threshold': 5
        }
    }
}


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
    Loads config.yaml and provides typed access to config.
    Falls back to default config in demo mode.
    """
    
    _instance = None
    _config = None
    _initialized = False
    
    def __new__(cls, config_path: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        # Only initialize once
        if ConfigManager._initialized:
            return
        
        self._load_config(config_path)
        ConfigManager._initialized = True
    
    def _load_config(self, config_path: Optional[str] = None):
        """Load configuration from YAML file or use defaults"""
        
        # Check if we're in demo mode
        demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        
        if config_path is not None:
            config_path = Path(config_path)
        else:
            # Try multiple locations
            possible_paths = [
                Path(__file__).parents[2] / "config.yaml",  # Project root
                Path(__file__).parent / "settings.yaml",    # bot/config/
                Path(__file__).parent / "config.yaml",      # bot/config/
                Path("/app/config.yaml"),                   # Docker
                Path("/app/bot/config/settings.yaml"),      # Docker fallback
            ]
            
            config_path = None
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
        
        # Load config or use defaults
        if config_path and config_path.exists():
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"✓ Configuration loaded from {config_path}")
        elif demo_mode:
            # Use default config in demo mode
            self._config = DEFAULT_CONFIG.copy()
            logger.info("🎮 Demo mode: Using default configuration")
        else:
            # In non-demo mode, require config file
            raise FileNotFoundError(
                f"Config file not found. Searched: {[str(p) for p in possible_paths if 'possible_paths' in dir()]}"
            )
        
        # Load environment variables
        self._load_env_vars()
    
    def _load_env_vars(self):
        """Load sensitive values from environment variables"""
        
        if self._config is None:
            return
        
        # Ensure nested dicts exist
        if 'state_persistence' not in self._config:
            self._config['state_persistence'] = {'storage': {}}
        if 'storage' not in self._config['state_persistence']:
            self._config['state_persistence']['storage'] = {}
        
        if 'markets' not in self._config:
            self._config['markets'] = {'polymarket': {}}
        if 'polymarket' not in self._config['markets']:
            self._config['markets']['polymarket'] = {}
        
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
        return self._config.get('system', {})
    
    @property
    def trading(self) -> TradingConfig:
        """Get trading configuration"""
        cfg = self._config.get('trading', DEFAULT_CONFIG['trading'])
        return TradingConfig(
            initial_capital=cfg.get('initial_capital', 10000.0),
            trading_interval=cfg.get('trading_interval', 60),
            max_position_size=cfg.get('max_position_size', 0.1),
            min_position_size=cfg.get('min_position_size', 0.01),
            max_open_positions=cfg.get('max_open_positions', 5)
        )
    
    @property
    def risk(self) -> RiskConfig:
        """Get risk configuration"""
        cfg = self._config.get('risk', DEFAULT_CONFIG['risk'])
        return RiskConfig(
            circuit_breaker=cfg.get('circuit_breaker', {}),
            correlation_threshold=cfg.get('correlation_threshold', 0.7),
            max_portfolio_correlation=cfg.get('max_portfolio_correlation', 0.8),
            kelly=cfg.get('kelly', {}),
            sharpe_target=cfg.get('sharpe_target', 1.5),
            max_drawdown_tolerance=cfg.get('max_drawdown_tolerance', 0.15)
        )
    
    @property
    def execution(self) -> ExecutionConfig:
        """Get execution configuration"""
        cfg = self._config.get('execution', DEFAULT_CONFIG['execution'])
        return ExecutionConfig(
            slippage_model=cfg.get('slippage_model', 'fixed'),
            commission_percent=cfg.get('commission_percent', 0.001),
            market_impact_percent=cfg.get('market_impact_percent', 0.0005),
            order_types=cfg.get('order_types', {}),
            simulation=cfg.get('simulation', {})
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        if self._config is None:
            return default
        
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
        ConfigManager._initialized = False
        self._load_config()
        ConfigManager._initialized = True
        logger.info("✓ Configuration reloaded")


# DO NOT auto-instantiate - let modules create their own instance
# This prevents errors when importing the module
