"""
Liquidation Cascade Detector
Detects potential liquidation cascades to prevent catastrophic losses
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LiquidationEvent:
    """Single liquidation event"""
    timestamp: datetime
    symbol: str
    size: float
    price: float
    direction: str  # 'long' or 'short'


class LiquidationDetector:
    """
    Detects liquidation cascades in real-time
    
    Cascade indicators:
    - Sudden spike in liquidation volume
    - Consecutive liquidations in short timeframe
    - Price impact of liquidations
    - Clustering of liquidation prices
    """
    
    def __init__(self, 
                 cascade_threshold: float = 0.6,
                 lookback_window: int = 300):
        """
        Args:
            cascade_threshold: Probability threshold to trigger action (0-1)
            lookback_window: Time window in seconds to analyze
        """
        self.cascade_threshold = cascade_threshold
        self.lookback_window = lookback_window
        
        # Liquidation tracking
        self.recent_liquidations: List[LiquidationEvent] = []
        self.cascade_history: List[Dict] = []
        
        # Thresholds
        self.volume_spike_multiplier = 3.0  # 3x normal volume
        self.time_clustering_seconds = 60   # Events within 60s
        self.min_events_for_cascade = 5
        
        logger.info(
            f"✓ Liquidation Detector initialized "
            f"(threshold={cascade_threshold:.0%}, window={lookback_window}s)"
        )
    
    def add_liquidation(self, event: LiquidationEvent):
        """
        Add observed liquidation event
        
        Args:
            event: LiquidationEvent object
        """
        self.recent_liquidations.append(event)
        
        # Keep only recent events (within lookback window)
        self._cleanup_old_events()
        
        logger.debug(
            f"Liquidation recorded: {event.symbol} {event.direction} "
            f"size={event.size:.4f} @ {event.price:.2f}"
        )
    
    def _cleanup_old_events(self):
        """Remove events outside lookback window"""
        cutoff_time = datetime.now() - timedelta(seconds=self.lookback_window)
        
        self.recent_liquidations = [
            event for event in self.recent_liquidations
            if event.timestamp >= cutoff_time
        ]
    
    async def detect_cascade_risk(self, 
                                   market_data: Dict,
                                   recent_liquidations: List[Dict]) -> Dict:
        """
        Detect cascade probability
        
        Args:
            market_data: Current market data
            recent_liquidations: Recent liquidation events from feed
            
        Returns:
            Dict with cascade probability and details
        """
        
        # Convert to LiquidationEvent objects
        for liq in recent_liquidations:
            event = LiquidationEvent(
                timestamp=liq.get('timestamp', datetime.now()),
                symbol=liq.get('symbol', 'UNKNOWN'),
                size=liq.get('size', 0),
                price=liq.get('price', 0),
                direction=liq.get('direction', 'long')
            )
            self.add_liquidation(event)
        
        # Analyze cascade indicators
        volume_score = self._analyze_volume_spike()
        clustering_score = self._analyze_time_clustering()
        direction_score = self._analyze_directional_bias()
        price_impact_score = self._analyze_price_impact(market_data)
        
        # Weighted average of scores
        weights = {
            'volume': 0.35,
            'clustering': 0.25,
            'direction': 0.20,
            'price_impact': 0.20
        }
        
        cascade_probability = (
            weights['volume'] * volume_score +
            weights['clustering'] * clustering_score +
            weights['direction'] * direction_score +
            weights['price_impact'] * price_impact_score
        )
        
        # Build result
        result = {
            'probability': cascade_probability,
            'threshold': self.cascade_threshold,
            'triggered': cascade_probability >= self.cascade_threshold,
            'scores': {
                'volume_spike': volume_score,
                'time_clustering': clustering_score,
                'directional_bias': direction_score,
                'price_impact': price_impact_score
            },
            'recent_count': len(self.recent_liquidations),
            'timestamp': datetime.now()
        }
        
        # Log if high risk
        if result['triggered']:
            logger.warning(
                f"🚨 CASCADE RISK DETECTED: {cascade_probability:.2%} probability "
                f"({len(self.recent_liquidations)} liquidations in {self.lookback_window}s)"
            )
            self.cascade_history.append(result)
        
        return result
    
    def _analyze_volume_spike(self) -> float:
        """
        Analyze if liquidation volume is spiking
        
        Returns:
            Score 0-1 (0=normal, 1=extreme spike)
        """
        if len(self.recent_liquidations) < 2:
            return 0.0
        
        # Calculate total volume in recent window
        recent_volume = sum(event.size for event in self.recent_liquidations)
        
        # Compare to baseline (use half the window as baseline)
        baseline_window = self.lookback_window // 2
        cutoff_time = datetime.now() - timedelta(seconds=baseline_window)
        
        baseline_events = [
            event for event in self.recent_liquidations
            if event.timestamp < cutoff_time
        ]
        
        if not baseline_events:
            # No baseline, use count as proxy
            if len(self.recent_liquidations) > self.min_events_for_cascade:
                return 0.7
            return 0.0
        
        baseline_volume = sum(event.size for event in baseline_events)
        
        if baseline_volume == 0:
            return 0.5
        
        # Calculate spike multiplier
        spike_multiplier = recent_volume / baseline_volume
        
        # Normalize to 0-1
        score = min(1.0, spike_multiplier / self.volume_spike_multiplier)
        
        logger.debug(f"Volume spike score: {score:.2f} (multiplier: {spike_multiplier:.2f}x)")
        
        return score
    
    def _analyze_time_clustering(self) -> float:
        """
        Analyze if liquidations are clustered in time
        
        Returns:
            Score 0-1 (0=spread out, 1=highly clustered)
        """
        if len(self.recent_liquidations) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_events = sorted(self.recent_liquidations, key=lambda e: e.timestamp)
        
        # Calculate time gaps between consecutive events
        time_gaps = []
        for i in range(1, len(sorted_events)):
            gap = (sorted_events[i].timestamp - sorted_events[i-1].timestamp).total_seconds()
            time_gaps.append(gap)
        
        # Check how many gaps are below clustering threshold
        clustered_gaps = sum(1 for gap in time_gaps if gap <= self.time_clustering_seconds)
        
        # Calculate clustering ratio
        clustering_ratio = clustered_gaps / len(time_gaps) if time_gaps else 0.0
        
        logger.debug(f"Time clustering score: {clustering_ratio:.2f}")
        
        return clustering_ratio
    
    def _analyze_directional_bias(self) -> float:
        """
        Analyze if liquidations are biased in one direction
        
        Returns:
            Score 0-1 (0=balanced, 1=all same direction)
        """
        if len(self.recent_liquidations) < 2:
            return 0.0
        
        # Count directions
        long_count = sum(1 for e in self.recent_liquidations if e.direction == 'long')
        short_count = len(self.recent_liquidations) - long_count
        
        total = len(self.recent_liquidations)
        
        # Calculate bias (how far from 50/50)
        bias = abs(long_count - short_count) / total
        
        logger.debug(
            f"Directional bias score: {bias:.2f} "
            f"(long={long_count}, short={short_count})"
        )
        
        return bias
    
    def _analyze_price_impact(self, market_data: Dict) -> float:
        """
        Analyze price impact of liquidations
        
        Args:
            market_data: Current market data
            
        Returns:
            Score 0-1 (0=no impact, 1=extreme impact)
        """
        if not self.recent_liquidations or not market_data:
            return 0.0
        
        # Get recent price change
        current_price = market_data.get('close', 0)
        if current_price == 0:
            return 0.0
        
        # Calculate price range during liquidation window
        prices = [event.price for event in self.recent_liquidations]
        if not prices:
            return 0.0
        
        price_range = max(prices) - min(prices)
        price_volatility = price_range / current_price
        
        # Normalize (assume >5% volatility is extreme)
        score = min(1.0, price_volatility / 0.05)
        
        logger.debug(f"Price impact score: {score:.2f} (volatility: {price_volatility:.2%})")
        
        return score
    
    def get_cascade_summary(self) -> Dict:
        """Get summary of cascade detection state"""
        
        return {
            'recent_liquidations_count': len(self.recent_liquidations),
            'cascade_history_count': len(self.cascade_history),
            'last_cascade': self.cascade_history[-1] if self.cascade_history else None,
            'lookback_window_seconds': self.lookback_window,
            'cascade_threshold': self.cascade_threshold
        }
    
    def reset(self):
        """Reset detector state"""
        self.recent_liquidations.clear()
        self.cascade_history.clear()
        logger.info("Liquidation detector reset")
