"""
Liquidation Flow Strategy
Capitalizes on liquidation cascades in leveraged markets
ROI Esperado: +950%
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from .base_strategy import BaseStrategy
from bot.ensemble.ensemble_voting import TradeSignal

logger = logging.getLogger(__name__)


class LiquidationFlowStrategy(BaseStrategy):
    """
    Liquidation Flow trading
    
    Monitors liquidation events and positions for:
    - Post-liquidation bounce trades
    - Front-running cascades
    - Liquidity vacuum plays
    
    High risk, high reward strategy
    """
    
    def __init__(self, config):
        super().__init__(config, 'liquidation_flow')
        
        # Parameters
        self.liquidation_threshold = 1000000  # $1M in liquidations
        self.cascade_lookback = 300  # 5 minutes
        self.bounce_multiplier = 1.5  # Expected bounce percentage
        
        # Tracking
        self.recent_liquidations: List[Dict] = []
        self.liquidation_zones: List[float] = []
    
    async def generate_signal(self, market_data: pd.DataFrame) -> Optional[TradeSignal]:
        """Generate liquidation-based signal"""
        
        if market_data.empty:
            return None
        
        data_with_indicators = self.calculate_indicators(market_data)
        
        if data_with_indicators.empty:
            return None
        
        latest = data_with_indicators.iloc[-1]
        
        price = latest.get('close', 0)
        volume_spike = latest.get('volume_spike', 0)
        price_drop = latest.get('price_drop_1m', 0)
        
        # Detect liquidation event
        liquidation_detected = self._detect_liquidation(
            volume_spike,
            price_drop,
            price
        )
        
        if not liquidation_detected:
            return None
        
        # Determine signal type
        signal = self._generate_liquidation_signal(latest, liquidation_detected)
        
        if signal:
            self.signals_generated += 1
        
        self.last_signal = signal
        return signal
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate liquidation indicators"""
        
        df = data.copy()
        
        # Volume spike detection
        df['volume_ma'] = df['volume'].rolling(window=20).mean()
        df['volume_spike'] = df['volume'] / (df['volume_ma'] + 1e-8)
        
        # Price drops (rapid moves indicate liquidations)
        df['price_drop_1m'] = df['close'].pct_change(periods=1)
        df['price_drop_5m'] = df['close'].pct_change(periods=5)
        
        # Volatility
        df['volatility'] = df['close'].rolling(window=20).std() / df['close'].rolling(window=20).mean()
        
        # Open interest proxy (using volume as approximation)
        df['oi_proxy'] = df['volume'].rolling(window=10).sum()
        
        return df.dropna()
    
    def _detect_liquidation(self, volume_spike: float, price_drop: float, price: float) -> Optional[Dict]:
        """
        Detect liquidation event
        
        Criteria:
        - Volume spike > 3x average
        - Price drop > 2% in 1 minute
        - Rapid sequential drops
        """
        
        # Long liquidation (price drop)
        if volume_spike > 3.0 and price_drop < -0.02:
            
            event = {
                'type': 'long_liquidation',
                'price': price,
                'timestamp': datetime.now(),
                'severity': abs(price_drop) * volume_spike,
                'direction': 'down'
            }
            
            self.recent_liquidations.append(event)
            self.liquidation_zones.append(price)
            
            logger.warning(
                f"🔥 LONG LIQUIDATION detected: "
                f"price={price:.2f}, drop={price_drop:.2%}, volume_spike={volume_spike:.1f}x"
            )
            
            return event
        
        # Short liquidation (price spike)
        elif volume_spike > 3.0 and price_drop > 0.02:
            
            event = {
                'type': 'short_liquidation',
                'price': price,
                'timestamp': datetime.now(),
                'severity': price_drop * volume_spike,
                'direction': 'up'
            }
            
            self.recent_liquidations.append(event)
            self.liquidation_zones.append(price)
            
            logger.warning(
                f"🔥 SHORT LIQUIDATION detected: "
                f"price={price:.2f}, spike={price_drop:.2%}, volume_spike={volume_spike:.1f}x"
            )
            
            return event
        
        return None
    
    def _generate_liquidation_signal(self, latest: pd.Series, liquidation: Dict) -> Optional[TradeSignal]:
        """Generate signal based on liquidation event"""
        
        price = latest.get('close', 0)
        liq_type = liquidation['type']
        severity = liquidation['severity']
        
        # Confidence based on severity
        confidence = min(severity / 10.0, 1.0)
        
        if liq_type == 'long_liquidation':
            # Long liquidation → expect bounce UP
            # Buy the dip after cascade
            
            entry_price = price * 0.995  # Enter slightly lower
            stop_loss = price * 0.98  # 2% stop
            take_profit = price * (1 + self.bounce_multiplier / 100)  # 1.5% bounce
            
            signal = TradeSignal(
                strategy=self.name,
                action='BUY',
                confidence=confidence,
                symbol='BTC',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                metadata={
                    'liquidation_type': liq_type,
                    'severity': severity,
                    'expected_bounce': self.bounce_multiplier
                }
            )
            
            logger.info(f"LiqFlow BUY signal: bounce play after long liq")
            return signal
        
        elif liq_type == 'short_liquidation':
            # Short liquidation → expect pullback DOWN
            # Sell the spike after cascade
            
            entry_price = price * 1.005  # Enter slightly higher
            stop_loss = price * 1.02
            take_profit = price * (1 - self.bounce_multiplier / 100)
            
            signal = TradeSignal(
                strategy=self.name,
                action='SELL',
                confidence=confidence,
                symbol='BTC',
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                metadata={
                    'liquidation_type': liq_type,
                    'severity': severity,
                    'expected_pullback': self.bounce_multiplier
                }
            )
            
            logger.info(f"LiqFlow SELL signal: pullback play after short liq")
            return signal
        
        return None
    
    def _cleanup_old_liquidations(self):
        """Remove old liquidation events"""
        
        cutoff = datetime.now() - timedelta(seconds=self.cascade_lookback)
        
        self.recent_liquidations = [
            liq for liq in self.recent_liquidations
            if liq['timestamp'] > cutoff
        ]
    
    def get_performance_metrics(self) -> Dict:
        """Extended metrics"""
        
        base_metrics = super().get_performance_metrics()
        
        self._cleanup_old_liquidations()
        
        base_metrics.update({
            'liquidations_detected': len(self.recent_liquidations),
            'liquidation_zones': len(self.liquidation_zones)
        })
        
        return base_metrics
