"""
Strategies Module
Loads and initializes all trading strategies
Supports: single strategy mode OR ensemble mode with all strategies
"""
import logging
from typing import Dict, List, Optional, Type

logger = logging.getLogger(__name__)

# Import base strategy
from .base_strategy import BaseStrategy

# Import ALL strategy classes
from .momentum import MomentumStrategy
from .stat_arb import StatisticalArbitrageStrategy
from .regime import RegimeStrategy
from .mean_reversion import MeanReversionStrategy
from .cross_exchange_arb import CrossExchangeArbitrageStrategy
from .liquidation_flow import LiquidationFlowStrategy
from .high_prob_bonds import HighProbabilityBondsStrategy
from .bollinger_bands import BollingerBandsStrategy
from .breakout import BreakoutStrategy
from .fibonacci import FibonacciStrategy
from .ichimoku import IchimokuStrategy
from .elliot_wave import ElliotWaveStrategy
from .rsi_divergence import RSIDivergenceStrategy
from .sector_rotation import SectorRotationStrategy
from .stochastic import StochasticStrategy
from .vix_hedge import VIXHedgeStrategy
from .volatility_expansion import VolatilityExpansionStrategy
from .macd_momentum import MACDMomentumStrategy
from .domain_specialization import DomainSpecializationStrategy
from .liquidity_provision import LiquidityProvisionStrategy

# Complete strategy class mapping - ALL 20 strategies
STRATEGY_CLASSES: Dict[str, Type[BaseStrategy]] = {
    # Base strategies
    'momentum': MomentumStrategy,
    'stat_arb': StatisticalArbitrageStrategy,
    'regime': RegimeStrategy,
    'mean_reversion': MeanReversionStrategy,
    
    # Advanced strategies
    'cross_exchange_arb': CrossExchangeArbitrageStrategy,
    'liquidation_flow': LiquidationFlowStrategy,
    'high_prob_bonds': HighProbabilityBondsStrategy,
    
    # Technical analysis strategies
    'bollinger_bands': BollingerBandsStrategy,
    'breakout': BreakoutStrategy,
    'fibonacci': FibonacciStrategy,
    'ichimoku': IchimokuStrategy,
    'elliot_wave': ElliotWaveStrategy,
    'rsi_divergence': RSIDivergenceStrategy,
    'stochastic': StochasticStrategy,
    'macd_momentum': MACDMomentumStrategy,
    
    # Market condition strategies
    'sector_rotation': SectorRotationStrategy,
    'vix_hedge': VIXHedgeStrategy,
    'volatility_expansion': VolatilityExpansionStrategy,
    
    # Specialized strategies
    'domain_specialization': DomainSpecializationStrategy,
    'liquidity_provision': LiquidityProvisionStrategy,
}

# Alias for backward compatibility
strategy_classes = STRATEGY_CLASSES


def get_available_strategies() -> List[str]:
    """Get list of all available strategy names"""
    return list(STRATEGY_CLASSES.keys())


def load_strategy(strategy_name: str, config) -> Optional[BaseStrategy]:
    """Load a single strategy by name"""
    if strategy_name not in STRATEGY_CLASSES:
        logger.warning(f"Strategy not found: {strategy_name}")
        logger.info(f"Available strategies: {get_available_strategies()}")
        return None
    
    try:
        strategy_class = STRATEGY_CLASSES[strategy_name]
        strategy = strategy_class(config)
        logger.info(f"Loaded strategy: {strategy_name}")
        return strategy
    except Exception as e:
        logger.error(f"Failed to load {strategy_name}: {e}")
        return None


def load_all_strategies(config) -> Dict[str, BaseStrategy]:
    """
    Load all enabled strategies from config
    
    Supports two modes:
    1. Single strategy: Only load one specific strategy
    2. Ensemble mode: Load multiple strategies for voting
    """
    
    strategies = {}
    
    # Get enabled strategies from config
    base_strategies = config.get('strategies.base', [])
    advanced_strategies = config.get('strategies.advanced', [])
    enabled = base_strategies + advanced_strategies
    
    # If 'all' is specified, load all available strategies
    if 'all' in enabled:
        enabled = get_available_strategies()
        logger.info("Loading ALL available strategies for ensemble mode")
    
    # Instantiate enabled strategies
    for strategy_name in enabled:
        strategy = load_strategy(strategy_name, config)
        if strategy:
            strategies[strategy_name] = strategy
    
    logger.info(f"Loaded {len(strategies)}/{len(enabled)} strategies")
    
    if len(strategies) == 0:
        logger.warning("No strategies loaded! Check your config.yaml")
    elif len(strategies) == 1:
        logger.info("Running in SINGLE STRATEGY mode")
    else:
        logger.info(f"Running in ENSEMBLE mode with {len(strategies)} strategies")
    
    return strategies


# Export for easy access
__all__ = [
    'BaseStrategy',
    'STRATEGY_CLASSES',
    'strategy_classes',
    'get_available_strategies',
    'load_strategy',
    'load_all_strategies',
]
