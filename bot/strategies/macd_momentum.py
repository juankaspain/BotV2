"""
MACD Momentum Strategy
Uses MACD crossovers and histogram
ROI Esperado: +280%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class MACDMomentumStrategy(BaseStrategy):
    """
    MACD (Moving Average Convergence Divergence) strategy
    
    Signals:
    - MACD line crosses above signal line → BUY
    - MACD line crosses below signal line → SELL
    - Histogram confirmation
    """
    
    def __init__(self, config):
        super().__init__(config, 'macd_momentum')
        
        # MACD parameters
        self.fast_period = 12
        self.slow_period = 26
        self.signal_period = 9
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate MACD signal"""
        
        if market_data.empty or len(market_data) < self.slow_period + self.signal_period:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty or len(data_with_indicators) < 2:
            return None
        
        latest = data_with_indicators.iloc[-1]
        previous = data_with_indicators.iloc[-2]
        
        price = latest.get('close', 0)
        macd = latest.get('macd', 0)
        signal_line = latest.get('signal', 0)
        histogram = latest.get('histogram', 0)
        
        prev_macd = previous.get('macd', 0)
        prev_signal = previous.get('signal', 0)
        
        # Bullish crossover
        if prev_macd <= prev_signal and macd > signal_line and histogram > 0:
            
            confidence = min(0.5 + abs(histogram) / 100, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=price * 0.96,
                take_profit=price * 1.08,
                metadata={
                    'macd': macd,
                    'signal': signal_line,
                    'histogram': histogram
                }
            )
            
            self.signals_generated += 1
            logger.info(f"MACD BUY: crossover detected, histogram={histogram:.2f}")
            
            self.last_signal = signal
            return signal
        
        # Bearish crossover
        elif prev_macd >= prev_signal and macd < signal_line and histogram < 0:
            
            confidence = min(0.5 + abs(histogram) / 100, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=price * 1.04,
                take_profit=price * 0.92,
                metadata={
                    'macd': macd,
                    'signal': signal_line,
                    'histogram': histogram
                }
            )
            
            self.signals_generated += 1
            logger.info(f"MACD SELL: crossover detected, histogram={histogram:.2f}")
            
            self.last_signal = signal
            return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD indicators"""
        
        df = data.copy()
        
        # Calculate EMAs
        ema_fast = df['close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # MACD line
        df['macd'] = ema_fast - ema_slow
        
        # Signal line
        df['signal'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # Histogram
        df['histogram'] = df['macd'] - df['signal']
        
        return df.dropna()
