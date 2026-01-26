"""
Correlation Manager
Manages strategy correlation to reduce portfolio risk
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CorrelationManager:
    """
    Manages correlation between strategies
    
    Key features:
    - Pearson/Spearman correlation calculation
    - Portfolio correlation tracking
    - Signal adjustment based on correlation
    - Correlation-aware position sizing
    """
    
    def __init__(self,
                 threshold: float = 0.7,
                 method: str = "pearson",
                 lookback_minutes: int = 60):
        """
        Args:
            threshold: Correlation threshold for action
            method: Correlation method (pearson or spearman)
            lookback_minutes: Historical window for correlation
        """
        self.threshold = threshold
        self.method = method
        self.lookback_minutes = lookback_minutes
        
        # State
        self.correlation_matrix: Optional[pd.DataFrame] = None
        self.returns_history: Dict[str, List[float]] = {}
        self.last_update: Optional[datetime] = None
        
        logger.info(
            f"✓ Correlation Manager initialized "
            f"(threshold={threshold}, method={method})"
        )
    
    def update_correlations(self,
                           signals: Dict,
                           performance: Dict):
        """
        Update correlation matrix based on recent strategy performance
        
        Args:
            signals: Current strategy signals
            performance: Strategy performance metrics
        """
        
        # Collect returns for each strategy
        for strategy_name, perf in performance.items():
            returns = perf.get('returns', [])
            
            if not returns:
                continue
            
            # Keep only recent returns
            if strategy_name not in self.returns_history:
                self.returns_history[strategy_name] = []
            
            self.returns_history[strategy_name].extend(returns)
            
            # Limit history size
            max_history = self.lookback_minutes
            if len(self.returns_history[strategy_name]) > max_history:
                self.returns_history[strategy_name] = \
                    self.returns_history[strategy_name][-max_history:]
        
        # Calculate correlation matrix
        self._calculate_correlation_matrix()
        
        self.last_update = datetime.now()
    
    def _calculate_correlation_matrix(self):
        """Calculate correlation matrix from returns history"""
        
        if not self.returns_history:
            return
        
        # Build DataFrame of returns
        min_length = min(len(returns) for returns in self.returns_history.values())
        
        if min_length < 2:
            logger.debug("Insufficient data for correlation calculation")
            return
        
        # Align all returns to same length
        aligned_returns = {}
        for strategy, returns in self.returns_history.items():
            aligned_returns[strategy] = returns[-min_length:]
        
        df = pd.DataFrame(aligned_returns)
        
        # Calculate correlation
        if self.method == "pearson":
            self.correlation_matrix = df.corr(method='pearson')
        elif self.method == "spearman":
            self.correlation_matrix = df.corr(method='spearman')
        else:
            logger.warning(f"Unknown correlation method: {self.method}")
            self.correlation_matrix = df.corr(method='pearson')
        
        logger.debug(f"Correlation matrix updated ({len(df.columns)} strategies)")
    
    def adjust_for_correlation(self,
                               signals: Dict,
                               current_positions: Dict) -> Dict:
        """
        Adjust signals based on correlation with current positions
        
        High correlation with existing positions → reduce signal strength
        
        Args:
            signals: Strategy signals
            current_positions: Current portfolio positions
            
        Returns:
            Adjusted signals
        """
        
        if self.correlation_matrix is None or self.correlation_matrix.empty:
            # No correlation data, return original signals
            return signals
        
        adjusted_signals = {}
        
        for strategy_name, signal in signals.items():
            
            # Calculate correlation with current positions
            position_correlation = self._calculate_position_correlation(
                strategy_name,
                current_positions
            )
            
            # Adjust signal confidence based on correlation
            if position_correlation > self.threshold:
                # High correlation → reduce confidence
                penalty = 1 - (position_correlation - self.threshold)
                adjusted_confidence = signal.confidence * penalty
                
                logger.debug(
                    f"{strategy_name}: High correlation {position_correlation:.2%} → "
                    f"confidence reduced by {(1-penalty)*100:.1f}%"
                )
            else:
                adjusted_confidence = signal.confidence
            
            # Create adjusted signal (copy original and modify confidence)
            adjusted_signal = signal
            adjusted_signal.confidence = adjusted_confidence
            adjusted_signals[strategy_name] = adjusted_signal
        
        return adjusted_signals
    
    def _calculate_position_correlation(self,
                                        strategy_name: str,
                                        current_positions: Dict) -> float:
        """
        Calculate average correlation between strategy and current positions
        
        Args:
            strategy_name: Strategy to check
            current_positions: Dict of current positions
            
        Returns:
            Average correlation [0-1]
        """
        
        if not current_positions or self.correlation_matrix is None:
            return 0.0
        
        # Get strategies of current positions
        position_strategies = [
            pos.get('strategy')
            for pos in current_positions.values()
            if pos.get('strategy')
        ]
        
        if not position_strategies:
            return 0.0
        
        # Calculate average correlation
        correlations = []
        
        for pos_strategy in position_strategies:
            if (strategy_name in self.correlation_matrix.index and
                pos_strategy in self.correlation_matrix.columns):
                
                corr = self.correlation_matrix.loc[strategy_name, pos_strategy]
                if not np.isnan(corr):
                    correlations.append(abs(corr))  # Use absolute correlation
        
        if not correlations:
            return 0.0
        
        avg_correlation = np.mean(correlations)
        
        return avg_correlation
    
    def get_portfolio_correlation(self) -> float:
        """
        Get average correlation of entire portfolio
        
        Returns:
            Average pairwise correlation
        """
        
        if self.correlation_matrix is None or self.correlation_matrix.empty:
            return 0.0
        
        # Get upper triangle of correlation matrix (exclude diagonal)
        n = len(self.correlation_matrix)
        
        if n < 2:
            return 0.0
        
        # Extract upper triangle
        upper_triangle = []
        for i in range(n):
            for j in range(i+1, n):
                corr = self.correlation_matrix.iloc[i, j]
                if not np.isnan(corr):
                    upper_triangle.append(abs(corr))
        
        if not upper_triangle:
            return 0.0
        
        return np.mean(upper_triangle)
    
    def get_correlation_factor(self, strategy_name: str) -> float:
        """
        Get correlation adjustment factor for position sizing
        
        Returns:
            Factor [0-1] to multiply position size by
        """
        
        portfolio_corr = self.get_portfolio_correlation()
        
        if portfolio_corr <= self.threshold:
            return 1.0  # No adjustment
        
        # Linear reduction based on excess correlation
        excess = portfolio_corr - self.threshold
        factor = 1 - excess
        
        return max(0.5, factor)  # Floor at 50%
    
    def get_correlation_matrix_dict(self) -> Dict:
        """Get correlation matrix as dict for serialization"""
        
        if self.correlation_matrix is None:
            return {}
        
        return self.correlation_matrix.to_dict()
    
    def get_summary(self) -> Dict:
        """Get correlation summary"""
        
        return {
            'portfolio_correlation': self.get_portfolio_correlation(),
            'threshold': self.threshold,
            'method': self.method,
            'strategies_tracked': len(self.returns_history),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
