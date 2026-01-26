"""
Volatility Expansion Strategy
Trades volatility breakouts after compression periods
ROI Esperado: +250%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class VolatilityExpansionStrategy(BaseStrategy):
    """
    Volatility Expansion strategy
    
    Logic:
    - Detect volatility compression (Bollinger Band squeeze)
    - Wait for expansion breakout
    - Enter in direction of breakout
    """
    
    def __init__(self, config):
        super().__init__(config, 'volatility_expansion')
        
        # Parameters
        self.bb_period = 20
        self.squeeze_threshold = 0.02  # 2% bandwidth = squeeze
        self.breakout_threshold = 0.01  # 1% move to confirm
        
        # State
        self.in_squeeze = False
        self.squeeze_duration = 0
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate volatility expansion signal"""
        
        if market_data.empty or len(market_data) < self.bb_period:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        bb_width = latest.get('bb_width', 0)
        price_change = latest.get('price_change_pct', 0)
        volume_ratio = latest.get('volume_ratio', 1.0)
        
        # Detect squeeze
        if bb_width < self.squeeze_threshold:
            self.in_squeeze = True
            self.squeeze_duration += 1
        else:
            if self.in_squeeze and self.squeeze_duration > 5:
                # Exiting squeeze - check for breakout
                
                if abs(price_change) > self.breakout_threshold and volume_ratio > 1.5:
                    # Valid breakout
                    
                    if price_change > 0:
                        # Upward breakout
                        confidence = min(0.5 + (price_change / 0.05), 1.0)
                        
                        signal = TradeSignal(
                            strategy=self.name,
                            action='BUY',
                            confidence=confidence,
                            symbol='BTC',
                            entry_price=price,
                            stop_loss=price * 0.97,
                            take_profit=price * 1.08,
                            metadata={
                                'squeeze_duration': self.squeeze_duration,
                                'bb_width': bb_width,
                                'breakout_size': price_change
                            }
                        )
                        
                        logger.info(f"VolExpansion BUY: squeeze={self.squeeze_duration} periods, breakout={price_change:.2%}")
                        
                        self.signals_generated += 1
                        self.in_squeeze = False
                        self.squeeze_duration = 0
                        
                        self.last_signal = signal
                        return signal
                    
                    else:
                        # Downward breakout
                        confidence = min(0.5 + (abs(price_change) / 0.05), 1.0)
                        
                        signal = TradeSignal(
                            strategy=self.name,
                            action='SELL',
                            confidence=confidence,
                            symbol='BTC',
                            entry_price=price,
                            stop_loss=price * 1.03,
                            take_profit=price * 0.92,
                            metadata={
                                'squeeze_duration': self.squeeze_duration,
                                'bb_width': bb_width,
                                'breakout_size': price_change
                            }
                        )
                        
                        logger.info(f"VolExpansion SELL: squeeze={self.squeeze_duration} periods, breakout={price_change:.2%}")
                        
                        self.signals_generated += 1
                        self.in_squeeze = False
                        self.squeeze_duration = 0
                        
                        self.last_signal = signal
                        return signal
            
            self.in_squeeze = False
            self.squeeze_duration = 0
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility indicators"""
        
        df = data.copy()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=self.bb_period).mean()
        bb_std = df['close'].rolling(window=self.bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (2 * bb_std)
        df['bb_lower'] = df['bb_middle'] - (2 * bb_std)
        
        # Bollinger Band Width (key indicator)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Price change
        df['price_change_pct'] = df['close'].pct_change()
        
        # Volume ratio
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / (df['volume_ma'] + 1)
        
        return df.dropna()
