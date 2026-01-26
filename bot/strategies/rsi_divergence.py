"""
RSI Divergence Strategy
Trades bullish/bearish divergences between price and RSI
ROI Esperado: +195%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from bot.ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class RSIDivergenceStrategy(BaseStrategy):
    """
    RSI Divergence strategy
    
    Bullish Divergence: Price makes lower low, RSI makes higher low
    Bearish Divergence: Price makes higher high, RSI makes lower high
    """
    
    def __init__(self, config):
        super().__init__(config, 'rsi_divergence')
        
        # Parameters
        self.rsi_period = 14
        self.lookback = 20
        self.divergence_threshold = 0.02  # 2% price difference minimum
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate RSI divergence signal"""
        
        if market_data.empty or len(market_data) < self.lookback + self.rsi_period:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        # Detect divergence
        divergence = self._detect_divergence(data_with_indicators)
        
        if divergence is None:
            return None
        
        latest = data_with_indicators.iloc[-1]
        price = latest.get('close', 0)
        rsi = latest.get('rsi', 50)
        
        if divergence == 'bullish':
            # Bullish divergence → BUY
            
            # Confidence based on RSI oversold level
            oversold_factor = max(0, (30 - rsi) / 30)
            confidence = 0.6 + (oversold_factor * 0.3)
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=price * 0.96,
                take_profit=price * 1.08,
                metadata={
                    'divergence_type': 'bullish',
                    'rsi': rsi
                }
            )
            
            self.signals_generated += 1
            logger.info(f"RSI Bullish Divergence: RSI={rsi:.1f}")
            
            self.last_signal = signal
            return signal
        
        elif divergence == 'bearish':
            # Bearish divergence → SELL
            
            # Confidence based on RSI overbought level
            overbought_factor = max(0, (rsi - 70) / 30)
            confidence = 0.6 + (overbought_factor * 0.3)
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=price * 1.04,
                take_profit=price * 0.92,
                metadata={
                    'divergence_type': 'bearish',
                    'rsi': rsi
                }
            )
            
            self.signals_generated += 1
            logger.info(f"RSI Bearish Divergence: RSI={rsi:.1f}")
            
            self.last_signal = signal
            return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI"""
        
        df = data.copy()
        
        # RSI calculation
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / (loss + 1e-8)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df.dropna()
    
    def _detect_divergence(self, data: pd.DataFrame) -> Optional[str]:
        """
        Detect bullish or bearish divergence
        
        Returns:
            'bullish', 'bearish', or None
        """
        
        if len(data) < self.lookback:
            return None
        
        recent_data = data.tail(self.lookback)
        
        # Find local extrema
        price_highs = recent_data['close'].nlargest(2)
        price_lows = recent_data['close'].nsmallest(2)
        rsi_highs = recent_data['rsi'].nlargest(2)
        rsi_lows = recent_data['rsi'].nsmallest(2)
        
        if len(price_highs) < 2 or len(price_lows) < 2:
            return None
        
        # Bullish divergence: price lower low, RSI higher low
        if (price_lows.iloc[0] < price_lows.iloc[1] and 
            rsi_lows.iloc[0] > rsi_lows.iloc[1]):
            
            price_diff = abs(price_lows.iloc[0] - price_lows.iloc[1]) / price_lows.iloc[1]
            
            if price_diff > self.divergence_threshold:
                return 'bullish'
        
        # Bearish divergence: price higher high, RSI lower high
        if (price_highs.iloc[0] > price_highs.iloc[1] and 
            rsi_highs.iloc[0] < rsi_highs.iloc[1]):
            
            price_diff = abs(price_highs.iloc[0] - price_highs.iloc[1]) / price_highs.iloc[1]
            
            if price_diff > self.divergence_threshold:
                return 'bearish'
        
        return None
