"""
Base Strategy Class
Abstract base class for all trading strategies
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    
    All strategies must inherit from this class and implement:
    - generate_signal()
    - calculate_indicators() (optional)
    """
    
    def __init__(self, config, strategy_name: str):
        """
        Initialize base strategy
        
        Args:
            config: Configuration manager
            strategy_name: Unique strategy identifier
        """
        self.config = config
        self.name = strategy_name
        
        # Performance tracking
        self.trades_history: List[Dict] = []
        self.returns_history: List[float] = []
        self.signals_generated = 0
        self.signals_executed = 0
        
        # State
        self.last_signal: Optional[TradeSignal] = None
        self.is_active = True
        
        logger.debug(f"✓ Strategy {self.name} initialized")
    
    @abstractmethod
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """
        Generate trading signal from market data
        
        This method MUST be implemented by each strategy
        
        Args:
            market_data: DataFrame with normalized market data
            
        Returns:
            TradeSignal or None if no signal
        """
        pass
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        
        Override this method to add strategy-specific indicators
        
        Args:
            data: Market data
            
        Returns:
            DataFrame with indicators added
        """
        return data
    
    def record_trade(self, trade_result: Dict):
        """
        Record trade execution result
        
        Args:
            trade_result: Dict with trade execution details
        """
        self.trades_history.append(trade_result)
        
        # Extract PnL
        pnl_pct = trade_result.get('pnl_pct', 0)
        self.returns_history.append(pnl_pct)
        
        if trade_result.get('executed', False):
            self.signals_executed += 1
    
    def get_performance_metrics(self) -> Dict:
        """
        Get strategy performance metrics
        
        Returns:
            Dict with performance statistics
        """
        
        if not self.returns_history:
            return {
                'returns': [],
                'sharpe': 0.0,
                'trades': 0,
                'win_rate': 0.0
            }
        
        returns_array = np.array(self.returns_history)
        
        # Calculate metrics
        total_return = np.sum(returns_array)
        avg_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        
        # Sharpe ratio (annualized)
        sharpe = (avg_return / (std_return + 1e-8)) * np.sqrt(252)
        
        # Win rate
        winning_trades = np.sum(returns_array > 0)
        win_rate = winning_trades / len(returns_array)
        
        # Max drawdown
        cumulative = np.cumsum(returns_array)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        max_drawdown = np.min(drawdown)
        
        return {
            'returns': self.returns_history[-20:],  # Last 20 returns
            'sharpe': sharpe,
            'total_return': total_return,
            'avg_return': avg_return,
            'std_return': std_return,
            'trades': len(self.trades_history),
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'signals_generated': self.signals_generated,
            'signals_executed': self.signals_executed
        }
    
    def get_recent_performance(self, lookback: int = 20) -> Dict:
        """
        Get recent performance (for adaptive allocation)
        
        Args:
            lookback: Number of recent trades
            
        Returns:
            Dict with recent metrics
        """
        
        recent_returns = self.returns_history[-lookback:] if self.returns_history else []
        
        return {
            'returns': recent_returns,
            'trades': len(recent_returns)
        }
    
    def reset_performance(self):
        """Reset performance tracking"""
        self.trades_history.clear()
        self.returns_history.clear()
        self.signals_generated = 0
        self.signals_executed = 0
        logger.info(f"✓ Strategy {self.name} performance reset")
    
    def activate(self):
        """Activate strategy"""
        self.is_active = True
        logger.info(f"✓ Strategy {self.name} activated")
    
    def deactivate(self):
        """Deactivate strategy"""
        self.is_active = False
        logger.info(f"✓ Strategy {self.name} deactivated")
    
    def __str__(self):
        return f"Strategy({self.name})"
    
    def __repr__(self):
        return self.__str__()


def load_all_strategies(config) -> Dict[str, BaseStrategy]:
    """
    Load all strategy implementations from strategies directory
    
    This function:
    1. Discovers all strategy files in the strategies directory
    2. Imports strategy implementations
    3. Instantiates each strategy with config
    4. Returns dict of all active strategies
    
    Args:
        config: Configuration manager
        
    Returns:
        Dict mapping strategy name -> strategy instance
    """
    
    strategies = {}
    strategies_dir = Path(__file__).parent
    
    logger.info("Loading trading strategies...")
    
    # List of built-in strategies to load
    built_in_strategies = {
        'momentum': 'MomentumStrategy',
        'mean_reversion': 'MeanReversionStrategy',
        'volatility': 'VolatilityStrategy',
        'trend_following': 'TrendFollowingStrategy',
    }
    
    for strategy_module, strategy_class_name in built_in_strategies.items():
        try:
            strategy_file = strategies_dir / f"{strategy_module}.py"
            
            # Check if strategy file exists
            if not strategy_file.exists():
                logger.warning(f"⚠️ Strategy file not found: {strategy_module}.py")
                continue
            
            # Dynamic import
            module_name = f"strategies.{strategy_module}"
            spec = __import__(module_name, fromlist=[strategy_class_name])
            strategy_class = getattr(spec, strategy_class_name, None)
            
            if strategy_class is None:
                logger.warning(f"⚠️ Strategy class {strategy_class_name} not found in {strategy_module}")
                continue
            
            # Instantiate strategy
            strategy_instance = strategy_class(config)
            strategies[strategy_instance.name] = strategy_instance
            
            logger.info(f"✓ Loaded strategy: {strategy_instance.name}")
        
        except ImportError as e:
            logger.warning(f"⚠️ Could not import {strategy_module}: {e}")
            continue
        except Exception as e:
            logger.error(f"❌ Error loading strategy {strategy_module}: {e}")
            continue
    
    if not strategies:
        logger.warning(
            "⚠️ No strategies loaded. Creating dummy strategy for testing..."
        )
        
        # Create a dummy strategy for development/testing
        class DummyStrategy(BaseStrategy):
            """Dummy strategy for testing"""
            async def generate_signal(self, market_data: pd.DataFrame):
                return None
        
        dummy = DummyStrategy(config, "dummy_strategy")
        strategies["dummy_strategy"] = dummy
        logger.info("✓ Loaded dummy strategy (development only)")
    
    logger.info(f"✓ Total strategies loaded: {len(strategies)}")
    return strategies
