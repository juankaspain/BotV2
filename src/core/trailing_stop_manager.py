"""
Trailing Stop Manager
Dynamic trailing stops for profit protection and risk management
Implements multiple trailing stop types: ATR-based, percentage-based, Chandelier
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class TrailingStopType(Enum):
    """Types of trailing stops"""
    PERCENTAGE = "percentage"          # Fixed percentage from high
    ATR = "atr"                        # ATR-based (Average True Range)
    CHANDELIER = "chandelier"          # Chandelier exit (ATR from highest high)
    DYNAMIC = "dynamic"                # Dynamic based on volatility


@dataclass
class TrailingStop:
    """Individual trailing stop configuration"""
    symbol: str
    position_id: str
    entry_price: float
    current_price: float
    stop_price: float
    highest_price: float
    stop_type: TrailingStopType
    activation_profit: float  # % profit needed to activate
    trail_distance: float     # Distance to trail (% or ATR multiplier)
    activated: bool
    created_at: datetime
    last_updated: datetime
    

class TrailingStopManager:
    """
    Manages dynamic trailing stops for all positions
    
    Features:
    - Multiple stop types (percentage, ATR, chandelier)
    - Activation threshold (only activate after profit)
    - Auto-update on price changes
    - Integration with risk manager
    """
    
    def __init__(self, config):
        """
        Initialize trailing stop manager
        
        Args:
            config: Configuration object with trailing_stops settings
        """
        self.config = config
        
        # Active trailing stops
        self.stops: Dict[str, TrailingStop] = {}
        
        # Configuration
        self.enabled = config.risk.trailing_stops.get('enabled', True)
        self.default_type = TrailingStopType(
            config.risk.trailing_stops.get('default_type', 'percentage')
        )
        self.default_activation = config.risk.trailing_stops.get('activation_profit', 2.0)  # 2%
        self.default_trail_distance = config.risk.trailing_stops.get('trail_distance', 1.0)  # 1%
        
        # ATR settings
        self.atr_period = config.risk.trailing_stops.get('atr_period', 14)
        self.atr_multiplier = config.risk.trailing_stops.get('atr_multiplier', 2.0)
        
        # Chandelier settings
        self.chandelier_period = config.risk.trailing_stops.get('chandelier_period', 22)
        self.chandelier_multiplier = config.risk.trailing_stops.get('chandelier_multiplier', 3.0)
        
        # Statistics
        self.stops_triggered = 0
        self.profits_protected = 0.0
        
        logger.info(
            f"✓ Trailing Stop Manager initialized "
            f"(type={self.default_type.value}, activation={self.default_activation}%)"
        )
    
    def add_position(self,
                    symbol: str,
                    position_id: str,
                    entry_price: float,
                    stop_type: Optional[TrailingStopType] = None,
                    activation_profit: Optional[float] = None,
                    trail_distance: Optional[float] = None) -> TrailingStop:
        """
        Add trailing stop for a new position
        
        Args:
            symbol: Trading symbol
            position_id: Unique position identifier
            entry_price: Entry price of position
            stop_type: Type of trailing stop (default from config)
            activation_profit: Profit % to activate (default from config)
            trail_distance: Trail distance (default from config)
            
        Returns:
            Created TrailingStop object
        """
        
        if not self.enabled:
            logger.debug(f"Trailing stops disabled, skipping {symbol}")
            return None
        
        # Use defaults if not specified
        stop_type = stop_type or self.default_type
        activation_profit = activation_profit or self.default_activation
        trail_distance = trail_distance or self.default_trail_distance
        
        # Calculate initial stop price (at entry, not yet activated)
        initial_stop = self._calculate_stop_price(
            entry_price=entry_price,
            current_price=entry_price,
            highest_price=entry_price,
            stop_type=stop_type,
            trail_distance=trail_distance
        )
        
        # Create trailing stop
        stop = TrailingStop(
            symbol=symbol,
            position_id=position_id,
            entry_price=entry_price,
            current_price=entry_price,
            stop_price=initial_stop,
            highest_price=entry_price,
            stop_type=stop_type,
            activation_profit=activation_profit,
            trail_distance=trail_distance,
            activated=False,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.stops[position_id] = stop
        
        logger.info(
            f"✓ Trailing stop added: {symbol} @ {entry_price:.2f} "
            f"(type={stop_type.value}, activation={activation_profit}%, "
            f"distance={trail_distance}%)"
        )
        
        return stop
    
    def update_position(self, 
                       position_id: str,
                       current_price: float,
                       market_data: Optional[pd.DataFrame] = None) -> bool:
        """
        Update trailing stop based on current price
        
        Args:
            position_id: Position identifier
            current_price: Current market price
            market_data: Market data for ATR calculation (if needed)
            
        Returns:
            True if stop was triggered, False otherwise
        """
        
        if position_id not in self.stops:
            logger.warning(f"Position {position_id} not found in trailing stops")
            return False
        
        stop = self.stops[position_id]
        stop.current_price = current_price
        
        # Update highest price
        if current_price > stop.highest_price:
            stop.highest_price = current_price
        
        # Check activation
        if not stop.activated:
            profit_pct = ((current_price - stop.entry_price) / stop.entry_price) * 100
            
            if profit_pct >= stop.activation_profit:
                stop.activated = True
                logger.info(
                    f"✓ Trailing stop ACTIVATED: {stop.symbol} "
                    f"(profit={profit_pct:.2f}% >= {stop.activation_profit}%)"
                )
        
        # Update stop price if activated
        if stop.activated:
            new_stop_price = self._calculate_stop_price(
                entry_price=stop.entry_price,
                current_price=current_price,
                highest_price=stop.highest_price,
                stop_type=stop.stop_type,
                trail_distance=stop.trail_distance,
                market_data=market_data
            )
            
            # Only move stop up, never down
            if new_stop_price > stop.stop_price:
                logger.debug(
                    f"Trailing stop updated: {stop.symbol} "
                    f"{stop.stop_price:.2f} → {new_stop_price:.2f}"
                )
                stop.stop_price = new_stop_price
        
        stop.last_updated = datetime.now()
        
        # Check if stop triggered
        if current_price <= stop.stop_price and stop.activated:
            profit = current_price - stop.entry_price
            profit_pct = (profit / stop.entry_price) * 100
            
            logger.info(
                f"🎯 TRAILING STOP TRIGGERED: {stop.symbol} @ {current_price:.2f} "
                f"(entry={stop.entry_price:.2f}, profit={profit_pct:.2f}%)"
            )
            
            self.stops_triggered += 1
            self.profits_protected += profit
            
            return True
        
        return False
    
    def _calculate_stop_price(self,
                             entry_price: float,
                             current_price: float,
                             highest_price: float,
                             stop_type: TrailingStopType,
                             trail_distance: float,
                             market_data: Optional[pd.DataFrame] = None) -> float:
        """
        Calculate stop price based on stop type
        
        Args:
            entry_price: Original entry price
            current_price: Current market price
            highest_price: Highest price since entry
            stop_type: Type of trailing stop
            trail_distance: Distance to trail
            market_data: Market data for ATR/Chandelier
            
        Returns:
            Calculated stop price
        """
        
        if stop_type == TrailingStopType.PERCENTAGE:
            # Simple percentage from highest high
            stop = highest_price * (1 - trail_distance / 100)
            
        elif stop_type == TrailingStopType.ATR:
            # ATR-based stop
            if market_data is None or len(market_data) < self.atr_period:
                # Fallback to percentage if no data
                stop = highest_price * (1 - trail_distance / 100)
            else:
                atr = self._calculate_atr(market_data, self.atr_period)
                stop = highest_price - (atr * self.atr_multiplier)
            
        elif stop_type == TrailingStopType.CHANDELIER:
            # Chandelier exit
            if market_data is None or len(market_data) < self.chandelier_period:
                # Fallback to percentage if no data
                stop = highest_price * (1 - trail_distance / 100)
            else:
                atr = self._calculate_atr(market_data, self.chandelier_period)
                period_high = market_data['high'].tail(self.chandelier_period).max()
                stop = period_high - (atr * self.chandelier_multiplier)
            
        elif stop_type == TrailingStopType.DYNAMIC:
            # Dynamic based on volatility
            if market_data is None or len(market_data) < 20:
                stop = highest_price * (1 - trail_distance / 100)
            else:
                volatility = market_data['close'].pct_change().std()
                dynamic_distance = max(trail_distance, volatility * 100 * 2)
                stop = highest_price * (1 - dynamic_distance / 100)
        
        else:
            # Default to percentage
            stop = highest_price * (1 - trail_distance / 100)
        
        return stop
    
    def _calculate_atr(self, data: pd.DataFrame, period: int) -> float:
        """
        Calculate Average True Range
        
        Args:
            data: DataFrame with OHLC data
            period: ATR period
            
        Returns:
            ATR value
        """
        
        if len(data) < period:
            return 0.0
        
        # True Range calculation
        high = data['high']
        low = data['low']
        close_prev = data['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close_prev)
        tr3 = abs(low - close_prev)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR is EMA of TR
        atr = tr.ewm(span=period, adjust=False).mean().iloc[-1]
        
        return atr
    
    def remove_position(self, position_id: str):
        """
        Remove trailing stop for closed position
        
        Args:
            position_id: Position identifier
        """
        
        if position_id in self.stops:
            stop = self.stops[position_id]
            logger.debug(f"Removing trailing stop: {stop.symbol}")
            del self.stops[position_id]
    
    def get_stop_info(self, position_id: str) -> Optional[Dict]:
        """
        Get trailing stop information
        
        Args:
            position_id: Position identifier
            
        Returns:
            Stop information dict or None
        """
        
        if position_id not in self.stops:
            return None
        
        stop = self.stops[position_id]
        
        return {
            'symbol': stop.symbol,
            'position_id': stop.position_id,
            'entry_price': stop.entry_price,
            'current_price': stop.current_price,
            'stop_price': stop.stop_price,
            'highest_price': stop.highest_price,
            'stop_type': stop.stop_type.value,
            'activated': stop.activated,
            'unrealized_profit_pct': ((stop.current_price - stop.entry_price) / stop.entry_price) * 100,
            'distance_to_stop_pct': ((stop.current_price - stop.stop_price) / stop.current_price) * 100,
            'created_at': stop.created_at.isoformat(),
            'last_updated': stop.last_updated.isoformat()
        }
    
    def get_all_stops(self) -> List[Dict]:
        """Get information for all active trailing stops"""
        return [self.get_stop_info(pos_id) for pos_id in self.stops.keys()]
    
    def get_statistics(self) -> Dict:
        """Get trailing stop statistics"""
        
        active_stops = len(self.stops)
        activated_stops = sum(1 for s in self.stops.values() if s.activated)
        
        return {
            'enabled': self.enabled,
            'active_stops': active_stops,
            'activated_stops': activated_stops,
            'stops_triggered_total': self.stops_triggered,
            'profits_protected_total': self.profits_protected,
            'default_type': self.default_type.value,
            'default_activation': self.default_activation,
            'default_trail_distance': self.default_trail_distance
        }
