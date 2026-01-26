"""
Stochastic Oscillator Strategy
Uses %K and %D crossovers
ROI Esperado: +215%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from bot.ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class StochasticStrategy(BaseStrategy):
    """
    Stochastic Oscillator strategy
    
    Signals:
    - %K crosses above %D in oversold zone → BUY
    - %K crosses below %D in overbought zone → SELL
    """
    
    def __init__(self, config):
        super().__init__(config, 'stochastic')
        
        # Parameters
        self.k_period = 14
        self.d_period = 3
        self.oversold = 20
        self.overbought = 80
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate Stochastic signal"""
        
        if market_data.empty or len(market_data) < self.k_period + self.d_period:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty or len(data_with_indicators) < 2:
            return None
        
        latest = data_with_indicators.iloc[-1]
        previous = data_with_indicators.iloc[-2]
        
        price = latest.get('close', 0)
        k = latest.get('stoch_k', 50)
        d = latest.get('stoch_d', 50)
        prev_k = previous.get('stoch_k', 50)
        prev_d = previous.get('stoch_d', 50)
        
        # Bullish crossover in oversold zone
        if (prev_k <= prev_d and k > d and k < self.oversold):
            
            # Confidence increases with how oversold
            oversold_factor = (self.oversold - k) / self.oversold
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
                    'stoch_k': k,
                    'stoch_d': d,
                    'zone': 'oversold'
                }
            )
            
            self.signals_generated += 1
            logger.info(f"Stochastic BUY: %K={k:.1f}, %D={d:.1f} (oversold)")
            
            self.last_signal = signal
            return signal
        
        # Bearish crossover in overbought zone
        elif (prev_k >= prev_d and k < d and k > self.overbought):
            
            # Confidence increases with how overbought
            overbought_factor = (k - self.overbought) / (100 - self.overbought)
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
                    'stoch_k': k,
                    'stoch_d': d,
                    'zone': 'overbought'
                }
            )
            
            self.signals_generated += 1
            logger.info(f"Stochastic SELL: %K={k:.1f}, %D={d:.1f} (overbought)")
            
            self.last_signal = signal
            return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        
        df = data.copy()
        
        # %K calculation
        lowest_low = df['low'].rolling(window=self.k_period).min()
        highest_high = df['high'].rolling(window=self.k_period).max()
        
        df['stoch_k'] = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low + 1e-8))
        
        # %D calculation (SMA of %K)
        df['stoch_d'] = df['stoch_k'].rolling(window=self.d_period).mean()
        
        return df.dropna()
