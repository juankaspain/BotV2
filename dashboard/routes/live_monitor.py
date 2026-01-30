#!/usr/bin/env python3
"""
Live Monitor - Real-time trading activity monitoring

Provides:
- WebSocket-based live data streaming
- Real-time PnL updates
- Order flow monitoring
- Market data visualization
- Activity logging with EventType
- Strategy signals tracking
- Position monitoring
"""

import os
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
import time

logger = logging.getLogger(__name__)

# Singleton instance
_monitor_instance = None


# ==================== ENUMS ====================

class EventType(Enum):
    """Types of monitoring events"""
    TRADE = "trade"
    ORDER = "order"
    SIGNAL = "signal"
    ALERT = "alert"
    POSITION = "position"
    SYSTEM = "system"
    ERROR = "error"
    INFO = "info"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ==================== DATA CLASSES ====================

@dataclass
class StrategySignal:
    """Strategy signal data"""
    strategy_name: str
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    indicators: Dict[str, Any] = field(default_factory=dict)
    ensemble_vote: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'indicators': self.indicators,
            'ensemble_vote': self.ensemble_vote
        }


@dataclass
class OpenPosition:
    """Open position data"""
    position_id: str
    symbol: str
    side: str  # LONG, SHORT
    entry_price: float
    current_price: float
    size: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    time_in_position: timedelta
    stop_loss: float
    stop_loss_pct: float
    take_profit: Optional[float] = None
    strategy: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'size': self.size,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_pct': self.unrealized_pnl_pct,
            'time_in_position': str(self.time_in_position),
            'stop_loss': self.stop_loss,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit': self.take_profit,
            'strategy': self.strategy
        }


@dataclass
class ActivityEvent:
    """Activity log event"""
    event_type: EventType
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    severity: AlertSeverity = AlertSeverity.INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'event_type': self.event_type.value,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data,
            'severity': self.severity.value
        }


@dataclass
class BrowserAlert:
    """Browser notification alert"""
    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }


class LiveMonitor:
    """
    Real-time trading activity monitor.
    
    Provides live data for dashboard visualization including:
    - Live PnL updates
    - Order flow
    - Position changes
    - Market data
    - Activity logging
    - Strategy signals
    - Browser alerts
    """
    
    def __init__(self):
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        
        # Data stores
        self._live_pnl_history: List[Dict] = []
        self._recent_orders: List[Dict] = []
        self._positions: List[Dict] = []
        self._market_data: Dict[str, Dict] = {}
        
        # New: Activity and signals
        self._activity_log: List[ActivityEvent] = []
        self._strategy_signals: Dict[str, StrategySignal] = {}
        self._open_positions: Dict[str, OpenPosition] = {}
        self._pending_alerts: List[BrowserAlert] = []
        
        # Update tracking
        self._last_update = datetime.now()
        self._update_count = 0
        self._start_time = datetime.now()
        
        # Statistics
        self._stats = {
            'total_events': 0,
            'total_signals': 0,
            'total_positions_opened': 0,
            'total_positions_closed': 0,
            'total_alerts': 0
        }
        
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
        
        # Initialize positions (legacy format)
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
        
        # Initialize demo open positions (new format)
        self._open_positions = {
            'pos_001': OpenPosition(
                position_id='pos_001',
                symbol='BTCUSDT',
                side='LONG',
                entry_price=42500,
                current_price=42850,
                size=0.5,
                unrealized_pnl=175.00,
                unrealized_pnl_pct=0.82,
                time_in_position=timedelta(hours=2, minutes=30),
                stop_loss=41500,
                stop_loss_pct=2.35,
                take_profit=45000,
                strategy='MA_Crossover'
            ),
            'pos_002': OpenPosition(
                position_id='pos_002',
                symbol='ETHUSDT',
                side='LONG',
                entry_price=2250,
                current_price=2285,
                size=5.0,
                unrealized_pnl=175.00,
                unrealized_pnl_pct=1.56,
                time_in_position=timedelta(hours=1, minutes=15),
                stop_loss=2200,
                stop_loss_pct=2.22,
                take_profit=2400,
                strategy='RSI_Reversal'
            )
        }
        
        # Initialize demo strategy signals
        self._strategy_signals = {
            'MA_Crossover_BTCUSDT': StrategySignal(
                strategy_name='MA_Crossover',
                symbol='BTCUSDT',
                signal_type='BUY',
                confidence=0.85,
                indicators={'sma_50': 42000, 'sma_200': 40500},
                ensemble_vote='BUY'
            ),
            'RSI_Reversal_ETHUSDT': StrategySignal(
                strategy_name='RSI_Reversal',
                symbol='ETHUSDT',
                signal_type='HOLD',
                confidence=0.65,
                indicators={'rsi': 55, 'macd': 0.5},
                ensemble_vote='HOLD'
            )
        }
        
        # Initialize demo activity log
        self._activity_log = [
            ActivityEvent(
                event_type=EventType.TRADE,
                message='Opened LONG position on BTCUSDT',
                severity=AlertSeverity.INFO,
                data={'symbol': 'BTCUSDT', 'side': 'LONG', 'size': 0.5}
            ),
            ActivityEvent(
                event_type=EventType.SIGNAL,
                message='MA_Crossover generated BUY signal for BTCUSDT',
                severity=AlertSeverity.INFO,
                data={'strategy': 'MA_Crossover', 'signal': 'BUY', 'confidence': 0.85}
            )
        ]
    
    # ==================== ACTIVITY LOG ====================
    
    def log_event(self, event_type: EventType, message: str, 
                  data: Dict = None, severity: AlertSeverity = AlertSeverity.INFO):
        """Log an activity event"""
        event = ActivityEvent(
            event_type=event_type,
            message=message,
            data=data or {},
            severity=severity
        )
        self._activity_log.append(event)
        self._stats['total_events'] += 1
        
        # Keep only last 500 events
        if len(self._activity_log) > 500:
            self._activity_log = self._activity_log[-500:]
        
        self._last_update = datetime.now()
    
    def get_activity_log(self, event_type: EventType = None, 
                         limit: int = 50) -> List[Dict]:
        """Get activity log, optionally filtered by type"""
        events = self._activity_log
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Return most recent first
        return [e.to_dict() for e in reversed(events[-limit:])]
    
    def clear_activity_log(self):
        """Clear activity log"""
        self._activity_log = []
    
    # ==================== STRATEGY SIGNALS ====================
    
    def update_signal(self, signal: StrategySignal):
        """Update or add a strategy signal"""
        key = f"{signal.strategy_name}_{signal.symbol}"
        self._strategy_signals[key] = signal
        self._stats['total_signals'] += 1
        
        self.log_event(
            EventType.SIGNAL,
            f"{signal.strategy_name} generated {signal.signal_type} for {signal.symbol}",
            signal.to_dict()
        )
        
        self._last_update = datetime.now()
    
    def get_strategy_signals(self, strategy_name: str = None) -> List[Dict]:
        """Get strategy signals, optionally filtered by strategy"""
        signals = list(self._strategy_signals.values())
        
        if strategy_name:
            signals = [s for s in signals if s.strategy_name == strategy_name]
        
        return [s.to_dict() for s in signals]
    
    def clear_signals(self):
        """Clear all strategy signals"""
        self._strategy_signals = {}
    
    # ==================== POSITIONS ====================
    
    def update_position(self, position: OpenPosition):
        """Update or add an open position"""
        self._open_positions[position.position_id] = position
        self._stats['total_positions_opened'] += 1
        
        self.log_event(
            EventType.POSITION,
            f"Position updated: {position.symbol} {position.side}",
            position.to_dict()
        )
        
        self._last_update = datetime.now()
    
    def close_position(self, position_id: str, final_pnl: float, final_pnl_pct: float):
        """Close a position"""
        if position_id in self._open_positions:
            pos = self._open_positions.pop(position_id)
            self._stats['total_positions_closed'] += 1
            
            self.log_event(
                EventType.TRADE,
                f"Position closed: {pos.symbol} PnL: {final_pnl:.2f} ({final_pnl_pct:.2f}%)",
                {'position_id': position_id, 'pnl': final_pnl, 'pnl_pct': final_pnl_pct},
                AlertSeverity.INFO if final_pnl >= 0 else AlertSeverity.WARNING
            )
            
            self._last_update = datetime.now()
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        return [p.to_dict() for p in self._open_positions.values()]
    
    # ==================== ALERTS ====================
    
    def send_alert(self, title: str, message: str, 
                   severity: AlertSeverity = AlertSeverity.INFO,
                   data: Dict = None):
        """Send a browser alert"""
        alert = BrowserAlert(
            title=title,
            message=message,
            severity=severity,
            data=data or {}
        )
        self._pending_alerts.append(alert)
        self._stats['total_alerts'] += 1
        
        self.log_event(
            EventType.ALERT,
            f"[{severity.value.upper()}] {title}: {message}",
            data or {},
            severity
        )
        
        self._last_update = datetime.now()
    
    def get_pending_alerts(self, clear: bool = True) -> List[Dict]:
        """Get pending alerts, optionally clearing them"""
        alerts = [a.to_dict() for a in self._pending_alerts]
        
        if clear:
            self._pending_alerts = []
        
        return alerts
    
    # ==================== LIVE DATA (Legacy) ====================
    
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
        """Get current positions (legacy format)"""
        return self._positions.copy()
    
    def get_recent_orders(self, limit: int = 50) -> List[Dict]:
        """Get recent orders"""
        return self._recent_orders[-limit:]
    
    def get_market_data(self, symbols: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Get market data for symbols"""
        if symbols:
            return {s: self._market_data.get(s, {}) for s in symbols}
        return self._market_data.copy()
    
    # ==================== DATA UPDATES (Legacy) ====================
    
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
    
    def update_position_legacy(self, position: Dict):
        """Update or add position (legacy format)"""
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
        
        # Update open positions (new format)
        for pos_id, pos in self._open_positions.items():
            price_change = random.uniform(-0.5, 0.6) * pos.current_price / 100
            pos.current_price = round(pos.current_price + price_change, 2)
            pos.unrealized_pnl = round((pos.current_price - pos.entry_price) * pos.size, 2)
            pos.unrealized_pnl_pct = round((pos.current_price / pos.entry_price - 1) * 100, 2)
        
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
        uptime = datetime.now() - self._start_time
        
        return {
            'demo_mode': self.demo_mode,
            'uptime_seconds': int(uptime.total_seconds()),
            'pnl_history_size': len(self._live_pnl_history),
            'position_count': len(self._positions),
            'open_positions_count': len(self._open_positions),
            'order_count': len(self._recent_orders),
            'market_symbols': len(self._market_data),
            'activity_log_size': len(self._activity_log),
            'signal_count': len(self._strategy_signals),
            'pending_alerts': len(self._pending_alerts),
            'update_count': self._update_count,
            'last_update': self._last_update.isoformat(),
            **self._stats
        }
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self._stats = {
            'total_events': 0,
            'total_signals': 0,
            'total_positions_opened': 0,
            'total_positions_closed': 0,
            'total_alerts': 0
        }
        self._start_time = datetime.now()


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
