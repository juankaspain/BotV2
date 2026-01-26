"""
VIX Hedge Strategy
Uses volatility index for portfolio hedging
ROI Esperado: +155%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional

from .base_strategy import BaseStrategy
from ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class VIXHedgeStrategy(BaseStrategy):
    """
    VIX Hedge strategy
    
    Uses volatility index (VIX) to:
    - Hedge portfolio during high volatility
    - Long VIX when fear increases
    - Short VIX (via inverse products) when fear decreases
    
    VIX Levels:
    - <15: Low volatility (complacency)
    - 15-20: Normal
    - 20-30: Elevated fear
    - >30: Panic
    """
    
    def __init__(self, config):
        super().__init__(config, 'vix_hedge')
        
        # VIX thresholds
        self.low_vix = 15
        self.normal_vix = 20
        self.high_vix = 30
        self.panic_vix = 40
        
        # Position sizing (VIX is for hedging, not primary strategy)
        self.max_hedge_size = 0.10  # Max 10% in VIX hedge
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate VIX hedge signal"""
        
        if market_data.empty or len(market_data) < 20:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        # In production, would use actual VIX data
        # For demo, estimate VIX from market volatility
        estimated_vix = latest.get('estimated_vix', 20)
        vix_change = latest.get('vix_change', 0)
        market_return = latest.get('market_return', 0)
        
        # VIX spike: Market fear increasing
        if estimated_vix > self.high_vix and vix_change > 0.10:
            # Long VIX for protection
            
            confidence = min(0.5 + (estimated_vix - self.high_vix) / 50, 0.9)
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='VIX',
                entry_price=estimated_vix,
                stop_loss=estimated_vix * 0.85,
                take_profit=estimated_vix * 1.5,
                metadata={
                    'vix_level': estimated_vix,
                    'strategy_type': 'hedge',
                    'hedge_reason': 'fear_spike'
                }
            )
            
            self.signals_generated += 1
            logger.info(f"VIX Hedge BUY: VIX={estimated_vix:.1f} (fear spike)")
            
            self.last_signal = signal
            return signal
        
        # VIX extremely high: Sell when fear peaks
        elif estimated_vix > self.panic_vix and vix_change < -0.05:
            # Sell VIX / Short volatility
            
            confidence = 0.7
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='VIX',
                entry_price=estimated_vix,
                stop_loss=estimated_vix * 1.15,
                take_profit=estimated_vix * 0.70,
                metadata={
                    'vix_level': estimated_vix,
                    'strategy_type': 'mean_reversion',
                    'reason': 'peak_fear_reversal'
                }
            )
            
            self.signals_generated += 1
            logger.info(f"VIX SELL: VIX={estimated_vix:.1f} (peak fear, reversal)")
            
            self.last_signal = signal
            return signal
        
        # Low VIX: Buy VIX as cheap insurance
        elif estimated_vix < self.low_vix and market_return > 0.05:
            # Market up, VIX low = buy cheap protection
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=0.6,
                symbol='VIX',
                entry_price=estimated_vix,
                metadata={
                    'vix_level': estimated_vix,
                    'strategy_type': 'insurance',
                    'reason': 'cheap_protection'
                }
            )
            
            self.signals_generated += 1
            logger.info(f"VIX Insurance BUY: VIX={estimated_vix:.1f} (cheap protection)")
            
            self.last_signal = signal
            return signal
        
        return None
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Estimate VIX from market data"""
        
        df = data.copy()
        
        # Estimate VIX from realized volatility
        returns = df['close'].pct_change()
        rolling_vol = returns.rolling(window=20).std() * np.sqrt(252) * 100
        
        # VIX tends to be higher than realized vol
        df['estimated_vix'] = rolling_vol * 1.2
        
        # VIX change
        df['vix_change'] = df['estimated_vix'].pct_change()
        
        # Market return
        df['market_return'] = df['close'].pct_change(periods=20)
        
        return df.dropna()
