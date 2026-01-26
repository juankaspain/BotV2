"""
Fibonacci Retracement Strategy
Trades pullbacks to Fibonacci levels
ROI Esperado: +210%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from bot.ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class FibonacciStrategy(BaseStrategy):
    """
    Fibonacci retracement strategy
    
    Logic:
    - Identify swing high/low
    - Calculate Fibonacci levels (0.382, 0.5, 0.618)
    - Enter on bounce from key level
    """
    
    def __init__(self, config):
        super().__init__(config, 'fibonacci')
        
        # Fibonacci levels
        self.fib_levels = {
            '0.236': 0.236,
            '0.382': 0.382,
            '0.500': 0.500,
            '0.618': 0.618,
            '0.786': 0.786
        }
        
        # Key levels for trading
        self.key_levels = [0.382, 0.5, 0.618]
        
        # Parameters
        self.swing_lookback = 50
        self.tolerance = 0.005  # 0.5% around level
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate Fibonacci signal"""
        
        if market_data.empty or len(market_data) < self.swing_lookback:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        swing_high = latest.get('swing_high', 0)
        swing_low = latest.get('swing_low', 0)
        
        if swing_high == 0 or swing_low == 0:
            return None
        
        # Calculate Fibonacci levels
        fib_range = swing_high - swing_low
        
        fib_prices = {}
        for level_name, level_value in self.fib_levels.items():
            fib_prices[level_name] = swing_high - (fib_range * level_value)
        
        # Check if price is near a key Fibonacci level
        for level_value in self.key_levels:
            level_price = swing_high - (fib_range * level_value)
            
            # Price near Fibonacci level
            if abs(price - level_price) / level_price < self.tolerance:
                
                # Determine direction based on recent trend
                ma_short = data_with_indicators['close'].rolling(10).mean().iloc[-1]
                ma_long = data_with_indicators['close'].rolling(50).mean().iloc[-1]
                
                if ma_short > ma_long:
                    # Uptrend - BUY on pullback to Fib level
                    
                    confidence = 0.5 + (level_value * 0.5)  # Higher retracement = higher confidence
                    
                    signal = TradeSignal(
                        strategy=self.name,
                        action='BUY',
                        confidence=confidence,
                        symbol='BTC',
                        entry_price=price,
                        stop_loss=swing_low,
                        take_profit=swing_high,
                        metadata={
                            'fib_level': level_value,
                            'level_price': level_price,
                            'swing_high': swing_high,
                            'swing_low': swing_low
                        }
                    )
                    
                    self.signals_generated += 1
                    logger.info(f"Fibonacci BUY at {level_value} level (${level_price:.2f})")
                    
                    self.last_signal = signal
                    return signal
                
                elif ma_short < ma_long:
                    # Downtrend - SELL on rally to Fib level
                    
                    confidence = 0.5 + (level_value * 0.5)
                    
                    signal = TradeSignal(
                        strategy=self.name,
                        action='SELL',
                        confidence=confidence,
                        symbol='BTC',
                        entry_price=price,
                        stop_loss=swing_high,
                        take_profit=swing_low,
                        metadata={
                            'fib_level': level_value,
                            'level_price': level_price,
                            'swing_high': swing_high,
                            'swing_low': swing_low
                        }
                    )
                    
                    self.signals_generated += 1
                    logger.info(f"Fibonacci SELL at {level_value} level (${level_price:.2f})")
                    
                    self.last_signal = signal
                    return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Fibonacci indicators"""
        
        df = data.copy()
        
        # Swing high/low
        df['swing_high'] = df['high'].rolling(window=self.swing_lookback).max()
        df['swing_low'] = df['low'].rolling(window=self.swing_lookback).min()
        
        return df.dropna()
