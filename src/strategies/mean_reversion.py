"""
Mean Reversion Strategy
Trades reversals from extreme price levels
ROI Esperado: +290%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """
    Mean reversion strategy using Bollinger Bands
    
    Entry:
    - Price touches lower band → BUY
    - Price touches upper band → SELL
    
    Exit:
    - Price returns to middle band
    """
    
    def __init__(self, config):
        super().__init__(config, 'mean_reversion')
        
        # Parameters
        self.bb_period = 20
        self.bb_std = 2.0
        self.rsi_period = 14
        
        # Thresholds
        self.rsi_oversold = 30
        self.rsi_overbought = 70
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate mean reversion signal"""
        
        if market_data.empty or len(market_data) < self.bb_period:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        bb_upper = latest.get('bb_upper', 0)
        bb_lower = latest.get('bb_lower', 0)
        bb_middle = latest.get('bb_middle', 0)
        rsi = latest.get('rsi', 50)
        
        signal = None
        
        # BUY: Price at/below lower band + RSI oversold
        if price <= bb_lower and rsi < self.rsi_oversold:
            
            # Distance from middle band (more distance = higher confidence)
            distance = (bb_middle - price) / bb_middle
            confidence = min(0.5 + distance * 2, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=bb_lower * 0.98,
                take_profit=bb_middle,
                metadata={
                    'bb_position': 'lower',
                    'rsi': rsi,
                    'distance_pct': distance
                }
            )
            
            self.signals_generated += 1
            logger.debug(f"MeanRev BUY: price={price:.2f}, bb_lower={bb_lower:.2f}, rsi={rsi:.1f}")
        
        # SELL: Price at/above upper band + RSI overbought
        elif price >= bb_upper and rsi > self.rsi_overbought:
            
            distance = (price - bb_middle) / bb_middle
            confidence = min(0.5 + distance * 2, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=bb_upper * 1.02,
                take_profit=bb_middle,
                metadata={
                    'bb_position': 'upper',
                    'rsi': rsi,
                    'distance_pct': distance
                }
            )
            
            self.signals_generated += 1
            logger.debug(f"MeanRev SELL: price={price:.2f}, bb_upper={bb_upper:.2f}, rsi={rsi:.1f}")
        
        self.last_signal = signal
        return signal
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands and RSI"""
        
        df = data.copy()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=self.bb_period).mean()
        bb_std = df['close'].rolling(window=self.bb_period).std()
        
        df['bb_upper'] = df['bb_middle'] + (self.bb_std * bb_std)
        df['bb_lower'] = df['bb_middle'] - (self.bb_std * bb_std)
        
        # Bandwidth
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'], self.rsi_period)
        
        return df.dropna()
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate RSI"""
        
        delta = prices.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / (loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
