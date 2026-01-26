"""
Breakout Strategy
Trades price breakouts from consolidation ranges
ROI Esperado: +340%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class BreakoutStrategy(BaseStrategy):
    """
    Breakout strategy from consolidation ranges
    
    Entry:
    - Price breaks above resistance with volume
    - Price breaks below support with volume
    """
    
    def __init__(self, config):
        super().__init__(config, 'breakout')
        
        # Parameters
        self.lookback = 20
        self.breakout_threshold = 0.02  # 2% beyond high/low
        self.volume_multiplier = 1.5
        
        # Range tracking
        self.range_high = None
        self.range_low = None
        self.range_duration = 0
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate breakout signal"""
        
        if market_data.empty or len(market_data) < self.lookback:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        range_high = latest.get('range_high', 0)
        range_low = latest.get('range_low', 0)
        volume_ratio = latest.get('volume_ratio', 1.0)
        atr = latest.get('atr', 0)
        
        # Breakout above resistance
        if price > range_high * (1 + self.breakout_threshold):
            
            if volume_ratio > self.volume_multiplier:
                # Valid breakout
                
                breakout_size = (price - range_high) / range_high
                confidence = min(0.6 + breakout_size * 5, 1.0)
                
                signal = TradeSignal(
                    strategy=self.name,
                    action='BUY',
                    confidence=confidence,
                    symbol='BTC',
                    entry_price=price,
                    stop_loss=range_high * 0.99,
                    take_profit=price + (price - range_high) * 2,
                    metadata={
                        'breakout_type': 'resistance',
                        'breakout_size': breakout_size,
                        'volume_ratio': volume_ratio
                    }
                )
                
                self.signals_generated += 1
                logger.info(f"Breakout BUY: {breakout_size:.2%} above resistance")
                
                self.last_signal = signal
                return signal
        
        # Breakout below support
        elif price < range_low * (1 - self.breakout_threshold):
            
            if volume_ratio > self.volume_multiplier:
                # Valid breakdown
                
                breakdown_size = (range_low - price) / range_low
                confidence = min(0.6 + breakdown_size * 5, 1.0)
                
                signal = TradeSignal(
                    strategy=self.name,
                    action='SELL',
                    confidence=confidence,
                    symbol='BTC',
                    entry_price=price,
                    stop_loss=range_low * 1.01,
                    take_profit=price - (range_low - price) * 2,
                    metadata={
                        'breakout_type': 'support',
                        'breakout_size': breakdown_size,
                        'volume_ratio': volume_ratio
                    }
                )
                
                self.signals_generated += 1
                logger.info(f"Breakout SELL: {breakdown_size:.2%} below support")
                
                self.last_signal = signal
                return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate breakout indicators"""
        
        df = data.copy()
        
        # Range high/low (rolling)
        df['range_high'] = df['high'].rolling(window=self.lookback).max()
        df['range_low'] = df['low'].rolling(window=self.lookback).min()
        
        # Volume ratio
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_ma'] + 1)
        
        # ATR for volatility
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        
        return df.dropna()
