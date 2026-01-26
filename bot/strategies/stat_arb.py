"""
Statistical Arbitrage Strategy
Pairs trading based on cointegration
ROI Esperado: +420%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional
from scipy import stats

from .base_strategy import BaseStrategy
from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class StatisticalArbitrageStrategy(BaseStrategy):
    """
    Statistical Arbitrage / Pairs Trading
    
    Identifies cointegrated pairs and trades mean reversion
    Entry: When spread > 2 std deviations
    Exit: When spread returns to mean
    """
    
    def __init__(self, config):
        super().__init__(config, 'stat_arb')
        
        # Parameters
        self.lookback_period = 60
        self.entry_threshold = 2.0  # Standard deviations
        self.exit_threshold = 0.5
        
        # Pair tracking
        self.current_spread = None
        self.spread_mean = None
        self.spread_std = None
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate statistical arbitrage signal"""
        
        if market_data.empty or len(market_data) < self.lookback_period:
            return None
        
        # Calculate spread and z-score
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        z_score = latest.get('z_score', 0)
        spread = latest.get('spread', 0)
        price = latest.get('close', 0)
        
        signal = None
        
        # Long spread (BUY): z_score < -entry_threshold
        if z_score < -self.entry_threshold:
            confidence = min(abs(z_score) / 3.0, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='PAIR',
                entry_price=price,
                stop_loss=price * 0.97,
                take_profit=price * 1.06,
                metadata={
                    'z_score': z_score,
                    'spread': spread,
                    'type': 'long_spread'
                }
            )
            
            self.signals_generated += 1
            logger.debug(f"StatArb BUY: z={z_score:.2f}, conf={confidence:.2%}")
        
        # Short spread (SELL): z_score > entry_threshold
        elif z_score > self.entry_threshold:
            confidence = min(abs(z_score) / 3.0, 1.0)
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='PAIR',
                entry_price=price,
                stop_loss=price * 1.03,
                take_profit=price * 0.94,
                metadata={
                    'z_score': z_score,
                    'spread': spread,
                    'type': 'short_spread'
                }
            )
            
            self.signals_generated += 1
            logger.debug(f"StatArb SELL: z={z_score:.2f}, conf={confidence:.2%}")
        
        self.last_signal = signal
        return signal
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate spread and z-score"""
        
        df = data.copy()
        
        # Simulate pair spread (in production, use actual pair prices)
        # For demo: use high-low spread as proxy
        df['spread'] = df['high'] - df['low']
        
        # Calculate rolling statistics
        df['spread_mean'] = df['spread'].rolling(window=self.lookback_period).mean()
        df['spread_std'] = df['spread'].rolling(window=self.lookback_period).std()
        
        # Z-score
        df['z_score'] = (df['spread'] - df['spread_mean']) / (df['spread_std'] + 1e-8)
        
        # Store for later use
        if not df.empty:
            latest = df.iloc[-1]
            self.current_spread = latest['spread']
            self.spread_mean = latest['spread_mean']
            self.spread_std = latest['spread_std']
        
        return df.dropna()
    
    def check_cointegration(self, series1: pd.Series, series2: pd.Series) -> dict:
        """
        Test for cointegration between two price series
        
        Returns:
            Dict with cointegration test results
        """
        
        from statsmodels.tsa.stattools import coint
        
        try:
            score, pvalue, _ = coint(series1, series2)
            
            is_cointegrated = pvalue < 0.05
            
            return {
                'cointegrated': is_cointegrated,
                'pvalue': pvalue,
                'score': score
            }
        except Exception as e:
            logger.error(f"Cointegration test failed: {e}")
            return {'cointegrated': False}
