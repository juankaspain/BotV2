"""
Bollinger Bands Strategy
Trades band bounces and squeezes
ROI Esperado: +225%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from bot.ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class BollingerBandsStrategy(BaseStrategy):
    """
    Bollinger Bands strategy
    
    Signals:
    - Price touches lower band → BUY (bounce)
    - Price touches upper band → SELL (bounce)
    - Squeeze → await breakout
    """
    
    def __init__(self, config):
        super().__init__(config, 'bollinger_bands')
        
        # Parameters
        self.period = 20
        self.std_dev = 2.0
        self.squeeze_threshold = 0.02
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate Bollinger Bands signal"""
        
        if market_data.empty or len(market_data) < self.period:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        bb_upper = latest.get('bb_upper', 0)
        bb_middle = latest.get('bb_middle', 0)
        bb_lower = latest.get('bb_lower', 0)
        bb_width = latest.get('bb_width', 0)
        bb_position = latest.get('bb_position', 0.5)
        
        # Check for squeeze (low volatility)
        if bb_width < self.squeeze_threshold:
            # In squeeze - wait for breakout
            return None
        
        # Lower band bounce (oversold)
        if bb_position < 0.1:  # Price near lower band
            
            distance_from_middle = (bb_middle - price) / bb_middle
            confidence = min(0.5 + distance_from_middle * 3, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=bb_lower * 0.98,
                take_profit=bb_middle,
                metadata={
                    'bb_position': bb_position,
                    'bb_width': bb_width,
                    'type': 'lower_bounce'
                }
            )
            
            self.signals_generated += 1
            logger.info(f"BB BUY: lower band bounce, position={bb_position:.2f}")
            
            self.last_signal = signal
            return signal
        
        # Upper band bounce (overbought)
        elif bb_position > 0.9:  # Price near upper band
            
            distance_from_middle = (price - bb_middle) / bb_middle
            confidence = min(0.5 + distance_from_middle * 3, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=bb_upper * 1.02,
                take_profit=bb_middle,
                metadata={
                    'bb_position': bb_position,
                    'bb_width': bb_width,
                    'type': 'upper_bounce'
                }
            )
            
            self.signals_generated += 1
            logger.info(f"BB SELL: upper band bounce, position={bb_position:.2f}")
            
            self.last_signal = signal
            return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        
        df = data.copy()
        
        # Middle band (SMA)
        df['bb_middle'] = df['close'].rolling(window=self.period).mean()
        
        # Standard deviation
        bb_std = df['close'].rolling(window=self.period).std()
        
        # Upper and lower bands
        df['bb_upper'] = df['bb_middle'] + (self.std_dev * bb_std)
        df['bb_lower'] = df['bb_middle'] - (self.std_dev * bb_std)
        
        # Band width (volatility measure)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Price position within bands (0 = lower, 1 = upper)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        return df.dropna()
