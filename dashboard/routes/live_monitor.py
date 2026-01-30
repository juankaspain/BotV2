#!/usr/bin/env python3
"""
Live Monitor - Real-time monitoring for trading activity

Provides:
- Activity log tracking
- Strategy signal monitoring
- Open position tracking
- Browser alerts system
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import deque
import random

logger = logging.getLogger(__name__)

# Singleton instance
_monitor_instance = None


class EventType(Enum):
    """Types of activity events"""
    TRADE = 'trade'
    SIGNAL = 'signal'
    ALERT = 'alert'
    SYSTEM = 'system'
    ERROR = 'error'
    INFO = 'info'


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


@dataclass
class ActivityEvent:
    """Activity event record"""
    timestamp: datetime
    event_type: EventType
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'message': self.message,
            'details': self.details
        }


@dataclass
class StrategySignal:
    """Strategy signal record"""
    strategy_name: str
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    timestamp: datetime
    indicators: Dict[str, Any] = field(default_factory=dict)
    ensemble_vote: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
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
    """Open position record"""
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
class BrowserAlert:
    """Browser alert record"""
    timestamp: datetime
    severity: AlertSeverity
    title: str
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'data': self.data
        }


class LiveMonitor:
    """
    Real-time monitoring for trading activity.
    
    Tracks activity logs, signals, positions, and alerts.
    In demo mode, generates simulated data.
    """
    
    def __init__(self, max_events: int = 1000):
        self.max_events = max_events
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        
        # Storage
        self._activity_log: deque = deque(maxlen=max_events)
        self._signals: Dict[str, StrategySignal] = {}  # Key: strategy_name
        self._positions: Dict[str, OpenPosition] = {}  # Key: position_id
        self._alerts: List[BrowserAlert] = []
        
        # Statistics
        self._total_events = 0
        self._total_trades = 0
        self._last_update = datetime.now()
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        if self.demo_mode:
            self._initialize_demo_data()
        
        logger.info(f"LiveMonitor initialized (demo={self.demo_mode})")
    
    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Add some demo activity events
        event_types = [
            (EventType.SYSTEM, "Bot started successfully"),
            (EventType.SIGNAL, "BUY signal generated for BTCUSDT"),
            (EventType.TRADE, "Opened LONG position BTCUSDT"),
            (EventType.INFO, "Strategy MA_Crossover activated"),
        ]
        
        for i, (etype, msg) in enumerate(event_types):
            self._activity_log.append(ActivityEvent(
                timestamp=datetime.now() - timedelta(minutes=len(event_types)-i),
                event_type=etype,
                message=msg,
                details={'demo': True}
            ))
        
        # Add demo signals
        strategies = ['MA_Crossover', 'RSI_Strategy', 'Momentum']
        for strategy in strategies:
            self._signals[strategy] = StrategySignal(
                strategy_name=strategy,
                symbol='BTCUSDT',
                signal_type=random.choice(['BUY', 'SELL', 'HOLD']),
                confidence=round(random.uniform(0.6, 0.95), 2),
                timestamp=datetime.now(),
                indicators={'demo': True},
                ensemble_vote='HOLD'
            )
        
        # Add demo position
        self._positions['demo_pos_1'] = OpenPosition(
            position_id='demo_pos_1',
            symbol='BTCUSDT',
            side='LONG',
            entry_price=50000.0,
            current_price=51000.0,
            size=0.1,
            unrealized_pnl=100.0,
            unrealized_pnl_pct=2.0,
            time_in_position=timedelta(hours=1, minutes=30),
            stop_loss=49000.0,
            stop_loss_pct=2.0,
            take_profit=55000.0,
            strategy='MA_Crossover'
        )
    
    # ==================== ACTIVITY LOG ====================
    
    def add_event(self, event_type: EventType, message: str, details: Dict = None):
        """Add an activity event"""
        with self._lock:
            event = ActivityEvent(
                timestamp=datetime.now(),
                event_type=event_type,
                message=message,
                details=details or {}
            )
            self._activity_log.append(event)
            self._total_events += 1
            self._last_update = datetime.now()
    
    def get_activity_log(self, event_type: EventType = None, limit: int = 50) -> List[Dict]:
        """Get activity log events"""
        with self._lock:
            events = list(self._activity_log)
            
            # Filter by type if specified
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            # Sort by timestamp descending and limit
            events.sort(key=lambda x: x.timestamp, reverse=True)
            events = events[:limit]
            
            return [e.to_dict() for e in events]
    
    def clear_activity_log(self):
        """Clear all activity events"""
        with self._lock:
            self._activity_log.clear()
            logger.info("Activity log cleared")
    
    # ==================== STRATEGY SIGNALS ====================
    
    def update_signal(self, signal: StrategySignal):
        """Update a strategy signal"""
        with self._lock:
            self._signals[signal.strategy_name] = signal
            self._last_update = datetime.now()
    
    def get_strategy_signals(self, strategy_name: str = None) -> List[Dict]:
        """Get strategy signals"""
        with self._lock:
            if strategy_name:
                signal = self._signals.get(strategy_name)
                return [signal.to_dict()] if signal else []
            
            return [s.to_dict() for s in self._signals.values()]
    
    def clear_signals(self):
        """Clear all strategy signals"""
        with self._lock:
            self._signals.clear()
            logger.info("Strategy signals cleared")
    
    # ==================== POSITIONS ====================
    
    def update_position(self, position: OpenPosition):
        """Update an open position"""
        with self._lock:
            self._positions[position.position_id] = position
            self._last_update = datetime.now()
    
    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        with self._lock:
            return [p.to_dict() for p in self._positions.values()]
    
    def close_position(self, position_id: str, final_pnl: float, final_pnl_pct: float):
        """Close a position"""
        with self._lock:
            if position_id in self._positions:
                position = self._positions.pop(position_id)
                self._total_trades += 1
                
                # Add close event
                self.add_event(
                    EventType.TRADE,
                    f"Closed {position.side} {position.symbol}: {final_pnl_pct:+.2f}%",
                    {
                        'position_id': position_id,
                        'symbol': position.symbol,
                        'final_pnl': final_pnl,
                        'final_pnl_pct': final_pnl_pct
                    }
                )
    
    # ==================== ALERTS ====================
    
    def add_alert(self, severity: AlertSeverity, title: str, message: str, data: Dict = None):
        """Add a browser alert"""
        with self._lock:
            alert = BrowserAlert(
                timestamp=datetime.now(),
                severity=severity,
                title=title,
                message=message,
                data=data or {}
            )
            self._alerts.append(alert)
    
    def get_pending_alerts(self, clear: bool = True) -> List[Dict]:
        """Get pending alerts"""
        with self._lock:
            alerts = [a.to_dict() for a in self._alerts]
            
            if clear:
                self._alerts.clear()
            
            return alerts
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        with self._lock:
            return {
                'total_events': self._total_events,
                'total_trades': self._total_trades,
                'active_positions': len(self._positions),
                'active_signals': len(self._signals),
                'pending_alerts': len(self._alerts),
                'last_update': self._last_update.isoformat(),
                'demo_mode': self.demo_mode
            }
    
    def reset_statistics(self):
        """Reset all statistics"""
        with self._lock:
            self._total_events = 0
            self._total_trades = 0
            self._activity_log.clear()
            self._signals.clear()
            self._positions.clear()
            self._alerts.clear()
            self._last_update = datetime.now()
            
            if self.demo_mode:
                self._initialize_demo_data()
            
            logger.info("Monitoring statistics reset")


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
