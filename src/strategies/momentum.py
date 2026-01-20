"""
Momentum Strategy
Trades in direction of recent price momentum
ROI Esperado: +180%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class MomentumStrategy(BaseStrategy):
    """
    Momentum-based trading strategy
    
    Entry signals:
    - Price > MA(20) and RSI > 50 → BUY
    - Price < MA(20) and RSI < 50 → SELL
    
    Uses rate of change and moving averages
    """
    
    def __init__(self, config):
        super().__init__(config, 'momentum')
        
        # Strategy parameters
        self.ma_period = 20
        self.rsi_period = 14
        self.roc_period = 10
        
        # Thresholds
        self.rsi_buy_threshold = 50
        self.rsi_sell_threshold = 50
        self.min_roc = 0.02  # 2% minimum rate of change
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate momentum signal"""
        
        if market_data.empty or len(market_data) < self.ma_period:
            return None
        
        # Calculate indicators
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        # Get latest values
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        ma = latest.get('ma', 0)
        rsi = latest.get('rsi', 50)
        roc = latest.get('roc', 0)
        
        # Generate signal
        signal = None
        
        # BUY signal: Price above MA, RSI > 50, positive ROC
        if (price > ma and 
            rsi > self.rsi_buy_threshold and 
            roc > self.min_roc):
            
            confidence = self._calculate_confidence(rsi, roc, 'BUY')
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='BTC',  # Placeholder
                entry_price=price,
                stop_loss=price * 0.95,  # 5% stop loss
                take_profit=price * 1.10  # 10% take profit
            )
            
            self.signals_generated += 1
            logger.debug(f"Momentum BUY signal: confidence={confidence:.2%}")
        
        # SELL signal: Price below MA, RSI < 50, negative ROC
        elif (price < ma and 
              rsi < self.rsi_sell_threshold and 
              roc < -self.min_roc):
            
            confidence = self._calculate_confidence(rsi, roc, 'SELL')
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='BTC',
                entry_price=price,
                stop_loss=price * 1.05,
                take_profit=price * 0.90
            )
            
            self.signals_generated += 1
            logger.debug(f"Momentum SELL signal: confidence={confidence:.2%}")
        
        self.last_signal = signal
        return signal
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate momentum indicators"""
        
        df = data.copy()
        
        # Moving Average
        df['ma'] = df['close'].rolling(window=self.ma_period).mean()
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'], self.rsi_period)
        
        # Rate of Change
        df['roc'] = df['close'].pct_change(periods=self.roc_period)
        
        return df.dropna()
    
    def _calculate_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Relative Strength Index"""
        
        delta = prices.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / (loss + 1e-8)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_confidence(self, rsi: float, roc: float, action: str) -> float:
        """Calculate signal confidence based on indicator strength"""
        
        # RSI contribution
        if action == 'BUY':
            rsi_score = (rsi - 50) / 50  # 0-1 for RSI 50-100
        else:  # SELL
            rsi_score = (50 - rsi) / 50  # 0-1 for RSI 0-50
        
        rsi_score = np.clip(rsi_score, 0, 1)
        
        # ROC contribution
        roc_score = min(abs(roc) / 0.10, 1.0)  # 0-1 for 0-10% ROC
        
        # Combined confidence
        confidence = 0.6 * rsi_score + 0.4 * roc_score
        
        return confidence
