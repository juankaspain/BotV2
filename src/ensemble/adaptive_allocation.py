"""
Adaptive Allocation Engine
Allocates capital to strategies based on recent Sharpe ratio
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AdaptiveAllocationEngine:
    """
    Dynamically allocates capital to strategies based on performance
    
    Key features:
    - Sharpe ratio-based weighting
    - Exponential smoothing for stability
    - Automatic rebalancing
    - Drift tracking
    """
    
    def __init__(self,
                 rebalance_freq: str = "daily",
                 smoothing_alpha: float = 0.7,
                 lookback_days: int = 20):
        """
        Args:
            rebalance_freq: Rebalancing frequency (daily, hourly, weekly)
            smoothing_alpha: Exponential smoothing factor [0-1]
            lookback_days: Historical window for Sharpe calculation
        """
        self.rebalance_freq = rebalance_freq
        self.smoothing_alpha = smoothing_alpha
        self.lookback_days = lookback_days
        
        # State
        self.current_weights: Dict[str, float] = {}
        self.sharpe_history: Dict[str, float] = {}
        self.weight_history = []
        self.last_rebalance: Optional[datetime] = None
        
        # Constraints
        self.min_weight = 0.01  # Minimum 1% allocation
        self.max_weight = 0.25  # Maximum 25% allocation
        
        logger.info(
            f"✓ Adaptive Allocation Engine initialized "
            f"(freq={rebalance_freq}, alpha={smoothing_alpha}, lookback={lookback_days}d)"
        )
    
    def calculate_weights(self, strategies_performance: Dict) -> Dict[str, float]:
        """
        Calculate allocation weights based on strategy performance
        
        Args:
            strategies_performance: Dict with strategy performance metrics
                Expected format:
                {
                    'strategy_name': {
                        'returns': [list of returns],
                        'sharpe': current_sharpe,
                        'trades': trade_count
                    }
                }
        
        Returns:
            Dict mapping strategy names to allocation weights (sum to 1.0)
        """
        
        if not strategies_performance:
            logger.warning("No strategy performance data")
            return {}
        
        # Calculate recent Sharpe for each strategy
        recent_sharpe = {}
        
        for strategy_name, perf_data in strategies_performance.items():
            
            # Get returns
            returns = perf_data.get('returns', [])
            
            if len(returns) < 2:
                # Insufficient data, use neutral weight
                recent_sharpe[strategy_name] = 1.0
                continue
            
            # Calculate Sharpe ratio
            sharpe = self._calculate_sharpe(returns)
            
            # Apply exponential smoothing with historical Sharpe
            if strategy_name in self.sharpe_history:
                prev_sharpe = self.sharpe_history[strategy_name]
                smoothed_sharpe = (
                    self.smoothing_alpha * prev_sharpe +
                    (1 - self.smoothing_alpha) * sharpe
                )
            else:
                smoothed_sharpe = sharpe
            
            # Ensure positive (floor at 0.5 to avoid zero weights)
            smoothed_sharpe = max(0.5, smoothed_sharpe)
            
            # Cap at reasonable maximum
            smoothed_sharpe = min(5.0, smoothed_sharpe)
            
            recent_sharpe[strategy_name] = smoothed_sharpe
            self.sharpe_history[strategy_name] = smoothed_sharpe
            
            logger.debug(
                f"{strategy_name}: Sharpe={sharpe:.2f} → Smoothed={smoothed_sharpe:.2f}"
            )
        
        # Convert Sharpe ratios to weights
        weights = self._sharpe_to_weights(recent_sharpe)
        
        # Store weights
        self.current_weights = weights
        self.weight_history.append({
            'timestamp': datetime.now(),
            'weights': weights.copy()
        })
        self.last_rebalance = datetime.now()
        
        # Log top strategies
        top_3 = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        logger.info(f"✓ Weight allocation updated - Top 3: {dict(top_3)}")
        
        return weights
    
    def _sharpe_to_weights(self, sharpe_dict: Dict[str, float]) -> Dict[str, float]:
        """
        Convert Sharpe ratios to portfolio weights using normalized exponential
        
        Args:
            sharpe_dict: Dict mapping strategy names to Sharpe ratios
        
        Returns:
            Dict mapping strategy names to weights (normalized to sum to 1.0)
        """
        
        if not sharpe_dict:
            return {}
        
        # Exponential weighting for non-linear emphasis
        exp_weights = {}
        total_weight = 0
        
        for strategy_name, sharpe in sharpe_dict.items():
            # Use e^sharpe to emphasize higher Sharpe ratios
            exp_weight = np.exp(sharpe / 3.0)  # Divide by 3 to moderate exponential
            exp_weights[strategy_name] = exp_weight
            total_weight += exp_weight
        
        # Normalize and apply constraints
        normalized_weights = {}
        
        for strategy_name, exp_weight in exp_weights.items():
            # Normalize to sum to 1
            weight = exp_weight / total_weight
            
            # Apply min/max constraints
            weight = max(self.min_weight, min(self.max_weight, weight))
            
            normalized_weights[strategy_name] = weight
        
        # Renormalize after constraints to ensure sum to 1.0
        total = sum(normalized_weights.values())
        if total > 0:
            normalized_weights = {k: v / total for k, v in normalized_weights.items()}
        
        return normalized_weights
    
    def _calculate_sharpe(self, returns: list, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio from returns
        
        Args:
            returns: List of period returns
            risk_free_rate: Annual risk-free rate (default 2%)
        
        Returns:
            Sharpe ratio
        """
        
        if len(returns) < 2:
            return 1.0  # Neutral weight if insufficient data
        
        returns_array = np.array(returns)
        
        # Calculate annualized metrics
        annual_return = np.mean(returns_array) * 252  # Assuming daily returns
        annual_std = np.std(returns_array) * np.sqrt(252)
        
        # Avoid division by zero
        if annual_std == 0:
            return 0.0
        
        sharpe = (annual_return - risk_free_rate) / annual_std
        
        return max(0.1, sharpe)  # Floor at 0.1
    
    def should_rebalance(self) -> bool:
        """
        Check if portfolio should be rebalanced based on frequency setting
        
        Returns:
            True if rebalancing is due, False otherwise
        """
        
        if self.last_rebalance is None:
            return True
        
        time_since_rebalance = datetime.now() - self.last_rebalance
        
        if self.rebalance_freq == "hourly":
            return time_since_rebalance.total_seconds() > 3600
        elif self.rebalance_freq == "daily":
            return time_since_rebalance.total_seconds() > 86400
        elif self.rebalance_freq == "weekly":
            return time_since_rebalance.total_seconds() > 604800
        
        return False
    
    def get_weight_history(self, limit: int = 50) -> list:
        """
        Get recent weight history
        
        Args:
            limit: Maximum number of historical entries to return
        
        Returns:
            List of weight history entries
        """
        
        return self.weight_history[-limit:]
    
    def reset(self):
        """
        Reset the allocation engine state
        """
        
        self.current_weights = {}
        self.sharpe_history = {}
        self.weight_history = []
        self.last_rebalance = None
        
        logger.info("✓ Adaptive Allocation Engine reset")
