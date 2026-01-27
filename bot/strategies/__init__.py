"""
Strategies Module
Loads and initializes all trading strategies
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def load_all_strategies(config) -> Dict:
    """
    Load all enabled strategies
    
    Args:
        config: Configuration manager
    
    Returns:
        Dict mapping strategy name to strategy instance
    """
    
    strategies = {}
    
    # Import strategy classes
    from .momentum import MomentumStrategy
    from .stat_arb import StatisticalArbitrageStrategy
    from .regime import RegimeStrategy
    from .mean_reversion import MeanReversionStrategy
    from .cross_exchange_arb import CrossExchangeArbitrageStrategy
    from .liquidation_flow import LiquidationFlowStrategy
    from .high_prob_bonds import HighProbabilityBondsStrategy
    
    # Get enabled strategies from config
    base_strategies = config.get('strategies.base', [])
    advanced_strategies = config.get('strategies.advanced', [])
    enabled = base_strategies + advanced_strategies
    
    # Strategy class mapping
    strategy_classes = {
        'momentum': MomentumStrategy,
        'stat_arb': StatisticalArbitrageStrategy,
        'regime': RegimeStrategy,
        'mean_reversion': MeanReversionStrategy,
        'cross_exchange_arb': CrossExchangeArbitrageStrategy,
        'liquidation_flow': LiquidationFlowStrategy,
        'high_prob_bonds': HighProbabilityBondsStrategy,
        # Add more as they're implemented
    }
    
    # Instantiate enabled strategies
    for strategy_name in enabled:
        if strategy_name in strategy_classes:
            try:
                strategies[strategy_name] = strategy_classes[strategy_name](config)
                logger.info(f"✓ Loaded strategy: {strategy_name}")
            except Exception as e:
                logger.error(f"Failed to load {strategy_name}: {e}")
        else:
            logger.warning(f"Strategy not found: {strategy_name}")
    
    logger.info(f"✓ Loaded {len(strategies)}/{len(enabled)} strategies")
    
    return strategies
