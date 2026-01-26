"""
Market Microstructure Model
Models order book dynamics and price formation
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from collections import deque

logger = logging.getLogger(__name__)


class OrderBook:
    """
    Simulated order book
    
    Maintains bid and ask sides with depth
    """
    
    def __init__(self, levels: int = 10):
        """
        Args:
            levels: Number of price levels to maintain
        """
        self.levels = levels
        
        # Order book structure
        self.bids: deque = deque(maxlen=levels)  # [(price, size), ...]
        self.asks: deque = deque(maxlen=levels)
        
        # State
        self.last_trade_price = 0.0
        self.last_trade_size = 0.0
    
    def initialize(self, mid_price: float, spread_bps: float = 5):
        """
        Initialize order book around mid price
        
        Args:
            mid_price: Middle price
            spread_bps: Spread in basis points
        """
        
        spread = mid_price * (spread_bps / 10000)
        
        # Clear existing
        self.bids.clear()
        self.asks.clear()
        
        # Generate bid levels
        for i in range(self.levels):
            price = mid_price - spread / 2 - (i * spread / 10)
            size = np.random.uniform(5000, 20000)  # Random size
            self.bids.append((price, size))
        
        # Generate ask levels
        for i in range(self.levels):
            price = mid_price + spread / 2 + (i * spread / 10)
            size = np.random.uniform(5000, 20000)
            self.asks.append((price, size))
        
        self.last_trade_price = mid_price
    
    def get_best_bid(self) -> Tuple[float, float]:
        """Get best bid (highest buy price)"""
        if self.bids:
            return self.bids[0]
        return (0.0, 0.0)
    
    def get_best_ask(self) -> Tuple[float, float]:
        """Get best ask (lowest sell price)"""
        if self.asks:
            return self.asks[0]
        return (0.0, 0.0)
    
    def get_spread(self) -> float:
        """Get bid-ask spread"""
        best_bid, _ = self.get_best_bid()
        best_ask, _ = self.get_best_ask()
        
        if best_bid == 0 or best_ask == 0:
            return 0.0
        
        return best_ask - best_bid
    
    def get_mid_price(self) -> float:
        """Get mid price"""
        best_bid, _ = self.get_best_bid()
        best_ask, _ = self.get_best_ask()
        
        if best_bid == 0 or best_ask == 0:
            return self.last_trade_price
        
        return (best_bid + best_ask) / 2
    
    def execute_market_order(self, action: str, size: float) -> Dict:
        """
        Execute market order against order book
        
        Args:
            action: BUY or SELL
            size: Order size in dollars
            
        Returns:
            Execution details
        """
        
        filled_size = 0.0
        total_cost = 0.0
        fills = []
        
        if action == 'BUY':
            # Take from asks
            book = list(self.asks)
            
            for i, (price, available) in enumerate(book):
                if filled_size >= size:
                    break
                
                # Calculate how much to take at this level
                remaining = size - filled_size
                take_size = min(remaining / price, available)
                
                # Execute fill
                fill_cost = take_size * price
                total_cost += fill_cost
                filled_size += fill_cost
                
                fills.append({
                    'price': price,
                    'size': take_size,
                    'cost': fill_cost
                })
                
                # Update book
                new_size = available - take_size
                if new_size > 0:
                    self.asks[i] = (price, new_size)
                else:
                    # Level exhausted, remove it
                    if len(self.asks) > i:
                        self.asks.pop(i)
        
        else:  # SELL
            # Hit bids
            book = list(self.bids)
            
            for i, (price, available) in enumerate(book):
                if filled_size >= size:
                    break
                
                remaining = size - filled_size
                take_size = min(remaining / price, available)
                
                fill_cost = take_size * price
                total_cost += fill_cost
                filled_size += fill_cost
                
                fills.append({
                    'price': price,
                    'size': take_size,
                    'cost': fill_cost
                })
                
                new_size = available - take_size
                if new_size > 0:
                    self.bids[i] = (price, new_size)
                else:
                    if len(self.bids) > i:
                        self.bids.pop(i)
        
        # Calculate average price
        avg_price = total_cost / (filled_size / fills[0]['price']) if fills else 0.0
        
        # Update last trade
        if fills:
            self.last_trade_price = fills[-1]['price']
            self.last_trade_size = filled_size
        
        return {
            'filled': filled_size >= size * 0.95,  # 95% fill threshold
            'filled_size': filled_size,
            'requested_size': size,
            'avg_price': avg_price,
            'fills': fills,
            'num_levels': len(fills)
        }


class MarketMicrostructure:
    """
    Market microstructure model
    
    Simulates realistic market dynamics:
    - Order flow imbalance
    - Price impact
    - Liquidity dynamics
    """
    
    def __init__(self):
        """Initialize microstructure model"""
        
        self.order_book = OrderBook(levels=10)
        
        # Metrics
        self.order_flow_imbalance = 0.0
        self.recent_trades = deque(maxlen=100)
        
        logger.info("✓ Market Microstructure model initialized")
    
    def update(self, market_data: pd.DataFrame):
        """
        Update microstructure based on market data
        
        Args:
            market_data: Latest market data
        """
        
        if market_data.empty:
            return
        
        latest = market_data.iloc[-1]
        price = latest.get('close', 0)
        
        if price == 0:
            return
        
        # Initialize/update order book
        self.order_book.initialize(price)
        
        # Calculate order flow imbalance
        volume = latest.get('volume', 0)
        price_change = latest.get('close', 0) - latest.get('open', 0)
        
        # Positive imbalance = more buying pressure
        if price_change > 0:
            self.order_flow_imbalance = min(1.0, volume / 1000000)
        else:
            self.order_flow_imbalance = max(-1.0, -volume / 1000000)
    
    def get_execution_price(self,
                           action: str,
                           size: float,
                           signal_price: float) -> float:
        """
        Get realistic execution price based on microstructure
        
        Args:
            action: BUY or SELL
            size: Order size
            signal_price: Signal price
            
        Returns:
            Realistic execution price
        """
        
        # Execute against order book
        result = self.order_book.execute_market_order(action, size)
        
        if result['filled']:
            return result['avg_price']
        else:
            # Partial fill, use worst price
            return signal_price * (1.01 if action == 'BUY' else 0.99)
    
    def get_liquidity_score(self) -> float:
        """
        Get current liquidity score [0-1]
        
        Higher = more liquid market
        """
        
        spread = self.order_book.get_spread()
        mid = self.order_book.get_mid_price()
        
        if mid == 0:
            return 0.5
        
        spread_pct = spread / mid
        
        # Lower spread = higher liquidity
        liquidity = 1 - min(spread_pct * 100, 1.0)
        
        return liquidity
