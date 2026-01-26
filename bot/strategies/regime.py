"""
Regime Detection Strategy
Adapts to market regime (trending, mean-reverting, volatile)
ROI Esperado: +320%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional
from enum import Enum

from .base_strategy import BaseStrategy
from bot.ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    """Market regime types"""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    MEAN_REVERTING = "mean_reverting"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


class RegimeStrategy(BaseStrategy):
    """
    Regime-adaptive strategy
    
    Detects current market regime and applies appropriate tactics:
    - Trending: Momentum following
    - Mean-reverting: Contrarian trades
    - High vol: Reduce exposure
    """
    
    def __init__(self, config):
        super().__init__(config, 'regime')
        
        # Parameters
        self.lookback = 50
        self.trend_threshold = 0.6  # ADX threshold for trending
        self.volatility_lookback = 20
        
        # Current regime
        self.current_regime = MarketRegime.MEAN_REVERTING
        self.regime_confidence = 0.5
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate regime-adaptive signal"""
        
        if market_data.empty or len(market_data) < self.lookback:
            return None
        
        # Detect regime
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        # Detect current regime
        self.current_regime = self._detect_regime(latest)
        
        # Generate signal based on regime
        signal = self._generate_regime_signal(latest)
        
        if signal:
            self.signals_generated += 1
        
        self.last_signal = signal
        return signal
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate regime indicators"""
        
        df = data.copy()
        
        # ADX for trend strength
        df['adx'] = self._calculate_adx(df, self.lookback)
        
        # Volatility (ATR)
        df['atr'] = self._calculate_atr(df, self.volatility_lookback)
        
        # Moving averages for trend direction
        df['ma_short'] = df['close'].rolling(window=10).mean()
        df['ma_long'] = df['close'].rolling(window=50).mean()
        
        # Hurst exponent for mean reversion
        df['hurst'] = df['close'].rolling(window=self.lookback).apply(
            self._calculate_hurst, raw=True
        )
        
        return df.dropna()
    
    def _detect_regime(self, latest_data: pd.Series) -> MarketRegime:
        """Detect current market regime"""
        
        adx = latest_data.get('adx', 0)
        hurst = latest_data.get('hurst', 0.5)
        atr = latest_data.get('atr', 0)
        ma_short = latest_data.get('ma_short', 0)
        ma_long = latest_data.get('ma_long', 0)
        
        # High volatility regime
        atr_mean = latest_data.get('atr', 0)  # Simplified
        if atr > atr_mean * 1.5:
            self.regime_confidence = 0.7
            return MarketRegime.HIGH_VOLATILITY
        
        # Trending regime (ADX > threshold)
        if adx > self.trend_threshold:
            self.regime_confidence = min(adx, 1.0)
            
            if ma_short > ma_long:
                return MarketRegime.TRENDING_UP
            else:
                return MarketRegime.TRENDING_DOWN
        
        # Mean-reverting regime (Hurst < 0.5)
        if hurst < 0.5:
            self.regime_confidence = 0.5 - hurst
            return MarketRegime.MEAN_REVERTING
        
        # Default
        self.regime_confidence = 0.5
        return MarketRegime.MEAN_REVERTING
    
    def _generate_regime_signal(self, latest: pd.Series) -> Optional[TradeSignal]:
        """Generate signal based on detected regime"""
        
        price = latest.get('close', 0)
        
        if self.current_regime == MarketRegime.TRENDING_UP:
            # Momentum: Buy the trend
            return TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=self.regime_confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=price * 0.96,
                take_profit=price * 1.08,
                metadata={'regime': 'trending_up'}
            )
        
        elif self.current_regime == MarketRegime.TRENDING_DOWN:
            # Momentum: Sell the trend
            return TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=self.regime_confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=price * 1.04,
                take_profit=price * 0.92,
                metadata={'regime': 'trending_down'}
            )
        
        elif self.current_regime == MarketRegime.MEAN_REVERTING:
            # Contrarian: Fade extremes
            rsi = latest.get('rsi', 50)
            
            if rsi > 70:  # Overbought → Sell
                return TradeSignal(
                    strategy=self.name,
                    action='SELL',
                    confidence=self.regime_confidence * 0.8,
                    symbol='BTC',
                    entry_price=price,
                    metadata={'regime': 'mean_reverting', 'rsi': rsi}
                )
            elif rsi < 30:  # Oversold → Buy
                return TradeSignal(
                    strategy=self.name,
                    action='BUY',
                    confidence=self.regime_confidence * 0.8,
                    symbol='BTC',
                    entry_price=price,
                    metadata={'regime': 'mean_reverting', 'rsi': rsi}
                )
        
        elif self.current_regime == MarketRegime.HIGH_VOLATILITY:
            # High vol: No signal (reduce exposure)
            logger.debug("High volatility regime: no signal")
            return None
        
        return None
    
    def _calculate_adx(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Average Directional Index"""
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
       
