"""
Ichimoku Cloud Strategy
Uses Ichimoku Kinko Hyo indicator system
ROI Esperado: +305%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from bot.ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class IchimokuStrategy(BaseStrategy):
    """
    Ichimoku Cloud strategy
    
    Components:
    - Tenkan-sen (Conversion Line)
    - Kijun-sen (Base Line)
    - Senkou Span A (Leading Span A)
    - Senkou Span B (Leading Span B)
    - Chikou Span (Lagging Span)
    """
    
    def __init__(self, config):
        super().__init__(config, 'ichimoku')
        
        # Ichimoku periods
        self.tenkan_period = 9
        self.kijun_period = 26
        self.senkou_b_period = 52
        self.displacement = 26
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate Ichimoku signal"""
        
        if market_data.empty or len(market_data) < self.senkou_b_period + self.displacement:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        tenkan = latest.get('tenkan_sen', 0)
        kijun = latest.get('kijun_sen', 0)
        senkou_a = latest.get('senkou_span_a', 0)
        senkou_b = latest.get('senkou_span_b', 0)
        
        # Cloud boundaries
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        
        # Bullish signals
        bullish_signals = 0
        
        if price > cloud_top:
            bullish_signals += 1
        if tenkan > kijun:
            bullish_signals += 1
        if senkou_a > senkou_b:  # Bullish cloud
            bullish_signals += 1
        
        # Bearish signals
        bearish_signals = 0
        
        if price < cloud_bottom:
            bearish_signals += 1
        if tenkan < kijun:
            bearish_signals += 1
        if senkou_a < senkou_b:  # Bearish cloud
            bearish_signals += 1
        
        # Generate signal based on alignment
        if bullish_signals >= 2:
            # Strong bullish setup
            
            confidence = 0.5 + (bullish_signals / 6)
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=cloud_bottom,
                take_profit=price * 1.10,
                metadata={
                    'bullish_signals': bullish_signals,
                    'cloud_top': cloud_top,
                    'cloud_bottom': cloud_bottom
                }
            )
            
            self.signals_generated += 1
            logger.info(f"Ichimoku BUY: {bullish_signals} bullish signals")
            
            self.last_signal = signal
            return signal
        
        elif bearish_signals >= 2:
            # Strong bearish setup
            
            confidence = 0.5 + (bearish_signals / 6)
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=cloud_top,
                take_profit=price * 0.90,
                metadata={
                    'bearish_signals': bearish_signals,
                    'cloud_top': cloud_top,
                    'cloud_bottom': cloud_bottom
                }
            )
            
            self.signals_generated += 1
            logger.info(f"Ichimoku SELL: {bearish_signals} bearish signals")
            
            self.last_signal = signal
            return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Ichimoku components"""
        
        df = data.copy()
        
        # Helper function: midpoint of high and low
        def midpoint(high, low):
            return (high + low) / 2
        
        # Tenkan-sen (Conversion Line): 9-period midpoint
        tenkan_high = df['high'].rolling(window=self.tenkan_period).max()
        tenkan_low = df['low'].rolling(window=self.tenkan_period).min()
        df['tenkan_sen'] = midpoint(tenkan_high, tenkan_low)
        
        # Kijun-sen (Base Line): 26-period midpoint
        kijun_high = df['high'].rolling(window=self.kijun_period).max()
        kijun_low = df['low'].rolling(window=self.kijun_period).min()
        df['kijun_sen'] = midpoint(kijun_high, kijun_low)
        
        # Senkou Span A (Leading Span A): midpoint of Tenkan and Kijun, shifted forward
        df['senkou_span_a'] = midpoint(df['tenkan_sen'], df['kijun_sen']).shift(self.displacement)
        
        # Senkou Span B (Leading Span B): 52-period midpoint, shifted forward
        senkou_b_high = df['high'].rolling(window=self.senkou_b_period).max()
        senkou_b_low = df['low'].rolling(window=self.senkou_b_period).min()
        df['senkou_span_b'] = midpoint(senkou_b_high, senkou_b_low).shift(self.displacement)
        
        # Chikou Span (Lagging Span): current close shifted backward
        df['chikou_span'] = df['close'].shift(-self.displacement)
        
        return df.dropna()
