#!/usr/bin/env python3
"""
Live Monitor - Real-time trading activity monitoring

Provides:
- WebSocket-based live data streaming
- Real-time PnL updates
- Order flow monitoring
- Market data visualization
"""

import os
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import time

logger = logging.getLogger(__name__)

# Singleton instance
_monitor_instance = None


class LiveMonitor:
    """
    Real-time trading activity monitor.
    
    Provides live data for dashboard visualization including:
    - Live PnL updates
    - Order flow
    - Position changes
    - Market data
    """
    
    def __init__(self):
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        
        # Data stores
        self._live_pnl_history: List[Dict] = []
        self._recent_orders: List[Dict] = []
        self._positions: List[Dict] = []
        self._market_data: Dict[str, Dict] = {}
        
        # Update tracking
        self._last_update = datetime.now()
        self._update_count = 0
        
        # Initialize demo data
        if self.demo_mode:
            self._initialize_demo_data()
        
        logger.info(f"LiveMonitor initialized (demo={self.demo_mode})")
    
    def _initialize_demo_data(self):
        """Initialize demo data for standalone testing"""
        # Initialize PnL history (last 100 points)
        base_time = datetime.now() - timedelta(hours=2)
        pnl = 0
        
        for i in range(100):
            pnl += random.uniform(-50, 60)  # Slightly positive drift
            self._live_pnl_history.append({
                'timestamp': (base_time + timedelta(minutes=i * 1.2)).isoformat(),
                'pnl': round(pnl, 2),
                'equity': round(10000 + pnl, 2)
            })
        
        # Initialize positions
        self._positions = [
            {
                'symbol': 'BTC/USDT',
                'side': 'long',
                'quantity': 0.5,
                'entry_price': 42500,
                'current_price': 42850,
                'pnl': 175.00,
                'pnl_pct': 0.82
            },
            {
                'symbol': 'ETH/USDT',
                'side': 'long',
                'quantity': 5.0,
                'entry_price': 2250,
                'current_price': 2285,
                'pnl': 175.00,
                'pnl_pct': 1.56
            }
        ]
        
        # Initialize market data
        self._market_data = {
            'BTC/USDT': {'price': 42850, 'change_24h': 2.5, 'volume': 125000000},
            'ETH/USDT': {'price': 2285, 'change_24h': 3.2, 'volume': 45000000},
            'SOL/USDT': {'price': 98.50, 'change_24h': -1.5, 'volume': 8500000}
        }
    
    # ==================== LIVE DATA ====================
    
    def get_live_snapshot(self) -> Dict[str, Any]:
        """Get current live monitoring snapshot"""
        return {
            'timestamp': datetime.now().isoformat(),
            'pnl': {
                'current': self._live_pnl_history[-1]['pnl'] if self._live_pnl_history else 0,
                'equity': self._live_pnl_history[-1]['equity'] if self._live_pnl_history else 10000,
                'history': self._live_pnl_history[-50:]  # Last 50 points
            },
            'positions': self._positions,
            'position_count': len(self._positions),
            'market_data': self._market_data,
            'recent_orders': self._recent_orders[-20:],  # Last 20 orders
            'update_count': self._update_count
        }
    
    def get_pnl_history(self, limit: int = 100) -> List[Dict]:
        """Get PnL history"""
        return self._live_pnl_history[-limit:]
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        return self._positions.copy()
    
    def get_recent_orders(self, limit: int = 50) -> List[Dict]:
        """Get recent orders"""
        return self._recent_orders[-limit:]
    
    def get_market_data(self, symbols: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Get market data for symbols"""
        if symbols:
            return {s: self._market_data.get(s, {}) for s in symbols}
        return self._market_data.copy()
    
    # ==================== DATA UPDATES ====================
    
    def update_pnl(self, pnl: float, equity: float):
        """Record new PnL data point"""
        self._live_pnl_history.append({
            'timestamp': datetime.now().isoformat(),
            'pnl': round(pnl, 2),
            'equity': round(equity, 2)
        })
        
        # Keep only last 1000 points
        if len(self._live_pnl_history) > 1000:
            self._live_pnl_history = self._live_pnl_history[-1000:]
        
        self._update_count += 1
        self._last_update = datetime.now()
    
    def update_position(self, position: Dict):
        """Update or add position"""
        symbol = position.get('symbol')
        
        # Find existing position
        for i, pos in enumerate(self._positions):
            if pos['symbol'] == symbol:
                self._positions[i] = position
                return
        
        # Add new position
        self._positions.append(position)
    
    def remove_position(self, symbol: str):
        """Remove closed position"""
        self._positions = [p for p in self._positions if p['symbol'] != symbol]
    
    def add_order(self, order: Dict):
        """Add new order to recent orders"""
        order['timestamp'] = datetime.now().isoformat()
        self._recent_orders.append(order)
        
        # Keep only last 100 orders
        if len(self._recent_orders) > 100:
            self._recent_orders = self._recent_orders[-100:]
    
    def update_market_data(self, symbol: str, data: Dict):
        """Update market data for symbol"""
        self._market_data[symbol] = data
    
    # ==================== DEMO SIMULATION ====================
    
    def simulate_tick(self):
        """Simulate a market tick (for demo mode)"""
        if not self.demo_mode:
            return
        
        # Update PnL with random walk
        last_pnl = self._live_pnl_history[-1]['pnl'] if self._live_pnl_history else 0
        new_pnl = last_pnl + random.uniform(-30, 35)
        self.update_pnl(new_pnl, 10000 + new_pnl)
        
        # Update positions with random price changes
        for pos in self._positions:
            price_change = random.uniform(-0.5, 0.6) * pos['current_price'] / 100
            pos['current_price'] = round(pos['current_price'] + price_change, 2)
            pos['pnl'] = round((pos['current_price'] - pos['entry_price']) * pos['quantity'], 2)
            pos['pnl_pct'] = round((pos['current_price'] / pos['entry_price'] - 1) * 100, 2)
        
        # Update market data
        for symbol, data in self._market_data.items():
            price_change = random.uniform(-0.3, 0.35) * data['price'] / 100
            data['price'] = round(data['price'] + price_change, 2)
            data['change_24h'] = round(data['change_24h'] + random.uniform(-0.1, 0.1), 2)
        
        # Occasionally generate orders
        if random.random() < 0.1:  # 10% chance per tick
            self.add_order({
                'id': f'ORD-{self._update_count}',
                'symbol': random.choice(list(self._market_data.keys())),
                'side': random.choice(['buy', 'sell']),
                'type': random.choice(['market', 'limit']),
                'quantity': round(random.uniform(0.1, 2.0), 3),
                'status': 'filled'
            })
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitor statistics"""
        return {
            'demo_mode': self.demo_mode,
            'pnl_history_size': len(self._live_pnl_history),
            'position_count': len(self._positions),
            'order_count': len(self._recent_orders),
            'market_symbols': len(self._market_data),
            'update_count': self._update_count,
            'last_update': self._last_update.isoformat()
        }


def get_live_monitor() -> LiveMonitor:
    """
    Get the singleton LiveMonitor instance.
    
    Returns:
        LiveMonitor instance
    """
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = LiveMonitor()
    
    return _monitor_instance
