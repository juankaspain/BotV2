"""
Risk Manager - Complete Risk Management System
Implements Circuit Breaker, Kelly Sizing, Real-time Monitoring
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    GREEN = "green"      # Normal operations
    YELLOW = "yellow"    # Caution - reduced size
    RED = "red"         # Stop all trading


@dataclass
class RiskMetrics:
    """Current risk metrics snapshot"""
    timestamp: datetime
    portfolio_value: float
    daily_drawdown: float
    max_drawdown: float
    daily_pnl: float
    position_correlation: float
    leverage_ratio: float
    var_95: float  # Value at Risk 95%


class CircuitBreaker:
    """
    3-Level Circuit Breaker
    Level 1: -5% DD → Caution
    Level 2: -10% DD → Reduce 50%
    Level 3: -15% DD → Stop trading
    """
    
    def __init__(self, 
                 level_1: float = -5.0,
                 level_2: float = -10.0,
                 level_3: float = -15.0,
                 cooldown_minutes: int = 30):
        """
        Args:
            level_1: Level 1 drawdown threshold (%)
            level_2: Level 2 drawdown threshold (%)
            level_3: Level 3 drawdown threshold (%)
            cooldown_minutes: Minutes to wait after trigger
        """
        self.level_1 = level_1
        self.level_2 = level_2
        self.level_3 = level_3
        self.cooldown_minutes = cooldown_minutes
        
        self.state = CircuitBreakerState.GREEN
        self.triggered_at: Optional[datetime] = None
        self.triggered_level = 0
        self.trigger_history = []
    
    def check(self, daily_drawdown: float) -> CircuitBreakerState:
        """
        Check circuit breaker levels
        
        Args:
            daily_drawdown: Current daily drawdown in %
            
        Returns:
            Current circuit breaker state
        """
        
        # Check cooldown period
        if self.triggered_at is not None:
            elapsed = (datetime.now() - self.triggered_at).total_seconds() / 60
            if elapsed < self.cooldown_minutes:
                logger.debug(f"Circuit breaker in cooldown: {elapsed:.1f}/{self.cooldown_minutes} min")
                return self.state
        
        # Check levels
        if daily_drawdown <= self.level_3:
            self._trigger(CircuitBreakerState.RED, 3, daily_drawdown)
            
        elif daily_drawdown <= self.level_2:
            self._trigger(CircuitBreakerState.YELLOW, 2, daily_drawdown)
            
        elif daily_drawdown <= self.level_1:
            self._trigger(CircuitBreakerState.YELLOW, 1, daily_drawdown)
            
        else:
            # Reset to green if recovered
            if self.state != CircuitBreakerState.GREEN:
                logger.info(f"✓ Circuit breaker recovered: {daily_drawdown:.2%} DD")
            self.state = CircuitBreakerState.GREEN
            self.triggered_level = 0
        
        return self.state
    
    def _trigger(self, state: CircuitBreakerState, level: int, drawdown: float):
        """Trigger circuit breaker"""
        
        if self.state != state or self.triggered_level != level:
            # New trigger
            self.state = state
            self.triggered_level = level
            self.triggered_at = datetime.now()
            
            self.trigger_history.append({
                'timestamp': self.triggered_at,
                'level': level,
                'state': state.value,
                'drawdown': drawdown
            })
            
            if level == 3:
                logger.critical(f"🚨 CIRCUIT BREAKER LEVEL 3 (RED): {drawdown:.2%} DD - STOP TRADING")
            elif level == 2:
                logger.warning(f"⚠️ CIRCUIT BREAKER LEVEL 2 (YELLOW): {drawdown:.2%} DD - REDUCE 50%")
            elif level == 1:
                logger.warning(f"⚠️ CIRCUIT BREAKER LEVEL 1 (YELLOW): {drawdown:.2%} DD - CAUTION")
    
    def can_trade(self) -> bool:
        """Can we open new trades?"""
        return self.state != CircuitBreakerState.RED
    
    def get_size_multiplier(self) -> float:
        """Get position size multiplier based on state"""
        multipliers = {
            CircuitBreakerState.GREEN: 1.0,   # 100% normal
            CircuitBreakerState.YELLOW: 0.5,  # 50% reduced
            CircuitBreakerState.RED: 0.0      # 0% stopped
        }
        return multipliers[self.state]
    
    def get_state_info(self) -> Dict:
        """Get current state information"""
        return {
            'state': self.state.value,
            'level': self.triggered_level,
            'triggered_at': self.triggered_at,
            'can_trade': self.can_trade(),
            'size_multiplier': self.get_size_multiplier(),
            'trigger_count': len(self.trigger_history)
        }


class RiskManager:
    """
    Complete Risk Management System
    - Kelly Criterion position sizing
    - Real-time risk monitoring
    - Circuit breaker integration
    - Correlation-aware sizing
    """
    
    def __init__(self, config):
        """Initialize risk manager"""
        
        self.config = config
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            level_1=config.risk.circuit_breaker['level_1_drawdown'],
            level_2=config.risk.circuit_breaker['level_2_drawdown'],
            level_3=config.risk.circuit_breaker['level_3_drawdown'],
            cooldown_minutes=config.risk.circuit_breaker.get('cooldown_minutes', 30)
        )
        
        # Portfolio tracking
        self.daily_start_value: Optional[float] = None
        self.max_portfolio_value: Optional[float] = None
        self.portfolio_value_history: List[float] = []
        
        # Risk metrics
        self.current_metrics: Optional[RiskMetrics] = None
        self.metrics_history: List[RiskMetrics] = []
        
        # Limits
        self.max_position_size = config.trading.max_position_size
        self.min_position_size = config.trading.min_position_size
        self.kelly_fraction = config.risk.kelly['fraction']
        self.min_probability = config.risk.kelly['min_probability']
        
        logger.info("✓ Risk Manager initialized")
    
    def update_metrics(self, portfolio_value: float):
        """
        Update risk metrics
        
        Args:
            portfolio_value: Current portfolio value
        """
        
        # Initialize tracking
        if self.daily_start_value is None:
            self.daily_start_value = portfolio_value
            self.max_portfolio_value = portfolio_value
        
        # Update max value
        if portfolio_value > self.max_portfolio_value:
            self.max_portfolio_value = portfolio_value
        
        # Calculate metrics
        daily_dd = self._calculate_daily_drawdown(portfolio_value)
        max_dd = self._calculate_max_drawdown(portfolio_value)
        daily_pnl = portfolio_value - self.daily_start_value
        
        # Create metrics snapshot
        self.current_metrics = RiskMetrics(
            timestamp=datetime.now(),
            portfolio_value=portfolio_value,
            daily_drawdown=daily_dd,
            max_drawdown=max_dd,
            daily_pnl=daily_pnl,
            position_correlation=0.0,  # Updated externally
            leverage_ratio=1.0,  # Updated externally
            var_95=0.0  # Updated externally
        )
        
        self.metrics_history.append(self.current_metrics)
        self.portfolio_value_history.append(portfolio_value)
        
        # Check circuit breaker
        self.circuit_breaker.check(daily_dd * 100)  # Convert to %
    
    def _calculate_daily_drawdown(self, current_value: float) -> float:
        """Calculate daily drawdown"""
        if self.daily_start_value is None or self.daily_start_value == 0:
            return 0.0
        
        return (current_value - self.daily_start_value) / self.daily_start_value
    
    def _calculate_max_drawdown(self, current_value: float) -> float:
        """Calculate maximum drawdown from peak"""
        if self.max_portfolio_value is None or self.max_portfolio_value == 0:
            return 0.0
        
        return (current_value - self.max_portfolio_value) / self.max_portfolio_value
    
    def get_daily_drawdown(self) -> float:
        """Get current daily drawdown in %"""
        if self.current_metrics:
            return self.current_metrics.daily_drawdown * 100
        return 0.0
    
    def compute_kelly_fraction(self, win_probability: float, capital: float) -> float:
        """
        Compute Kelly Criterion position size
        
        Kelly = (bp - q) / b
        where:
            b = win/loss ratio (assuming 1:1 for simplicity)
            p = win probability
            q = loss probability (1 - p)
        
        Args:
            win_probability: Probability of winning trade [0-1]
            capital: Available capital
            
        Returns:
            Position size as fraction of capital
        """
        
        # Validate probability
        if win_probability < self.min_probability:
            logger.debug(f"Win probability {win_probability:.2%} below minimum {self.min_probability:.2%}")
            return 0.0
        
        # Kelly formula (assuming 1:1 risk/reward)
        b = 1.0  # Risk/reward ratio
        p = win_probability
        q = 1 - win_probability
        
        # Raw Kelly
        kelly_raw = (b * p - q) / b
        
        # Apply conservative fraction
        kelly_conservative = kelly_raw * self.kelly_fraction
        
        # Ensure non-negative
        kelly_conservative = max(0, kelly_conservative)
        
        logger.debug(
            f"Kelly sizing: p={p:.2%} → raw={kelly_raw:.2%} → "
            f"conservative={kelly_conservative:.2%}"
        )
        
        return kelly_conservative
    
    def apply_limits(self, position_size: float) -> float:
        """
        Apply all risk limits to position size
        
        Args:
            position_size: Raw position size
            
        Returns:
            Position size after applying limits
        """
        
        # Clip to min/max
        limited = np.clip(
            position_size,
            self.min_position_size,
            self.max_position_size
        )
        
        if limited != position_size:
            logger.debug(f"Position size limited: {position_size:.4f} → {limited:.4f}")
        
        return limited
    
    def correlation_aware_sizing(self, 
                                 base_size: float,
                                 portfolio_correlation: float) -> float:
        """
        Adjust position size for portfolio correlation
        
        Args:
            base_size: Base position size
            portfolio_correlation: Average portfolio correlation [0-1]
            
        Returns:
            Adjusted position size
        """
        
        correlation_threshold = self.config.risk.correlation_threshold
        
        if portfolio_correlation > correlation_threshold:
            # Apply penalty
            excess_correlation = portfolio_correlation - correlation_threshold
            penalty = 1 - excess_correlation
            adjusted = base_size * penalty
            
            logger.debug(
                f"Correlation penalty: {portfolio_correlation:.2%} > {correlation_threshold:.2%} → "
                f"size reduced by {(1-penalty)*100:.1f}%"
            )
            
            return adjusted
        
        return base_size
    
    async def emergency_reduce_positions(self, portfolio: Dict):
        """
        Emergency position reduction (e.g., liquidation cascade detected)
        
        Args:
            portfolio: Current portfolio dict
        """
        
        logger.critical("🚨 EMERGENCY: Reducing all positions by 50%")
        
        # Reduce each position by 50%
        for symbol in list(portfolio['positions'].keys()):
            position = portfolio['positions'][symbol]
            position['size'] *= 0.5
            
            if position['size'] < 0.001:
                # Remove tiny positions
                del portfolio['positions'][symbol]
                logger.info(f"Closed position: {symbol}")
            else:
                logger.info(f"Reduced position: {symbol} to {position['size']:.4f}")
    
    async def close_all_positions(self, portfolio: Dict):
        """
        Close all open positions
        
        Args:
            portfolio: Current portfolio dict
        """
        
        logger.critical("🚨 EMERGENCY: Closing all positions")
        
        closed_count = len(portfolio['positions'])
        portfolio['positions'].clear()
        
        logger.info(f"✓ Closed {closed_count} positions")
    
    def reset_daily_tracking(self):
        """Reset daily tracking (call at start of new trading day)"""
        
        if self.current_metrics:
            self.daily_start_value = self.current_metrics.portfolio_value
            logger.info(f"Daily tracking reset. Start value: €{self.daily_start_value:.2f}")
    
    def get_risk_report(self) -> Dict:
        """Get comprehensive risk report"""
        
        if not self.current_metrics:
            return {}
        
        return {
            'timestamp': self.current_metrics.timestamp.isoformat(),
            'portfolio_value': self.current_metrics.portfolio_value,
            'daily_drawdown_pct': self.current_metrics.daily_drawdown * 100,
            'max_drawdown_pct': self.current_metrics.max_drawdown * 100,
            'daily_pnl': self.current_metrics.daily_pnl,
            'circuit_breaker': self.circuit_breaker.get_state_info(),
            'limits': {
                'max_position_size': self.max_position_size,
                'min_position_size': self.min_position_size,
                'kelly_fraction': self.kelly_fraction
            }
        }
