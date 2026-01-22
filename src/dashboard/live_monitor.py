#!/usr/bin/env python3
"""
Live Monitor v4.3 - Real-time Bot Monitoring System

Provides real-time visibility into bot operations:
- Activity log stream (last 50 events)
- Strategy signals monitoring
- Open positions tracking
- Browser notifications for critical events

Author: Juan Carlos Garcia Arriero
Date: 22 Enero 2026
Version: 4.3.0
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import json

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class EventType(Enum):
    """Types of events for the activity log"""
    TRADE = "trade"
    SIGNAL = "signal"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    POSITION_OPEN = "position_open"
    POSITION_CLOSE = "position_close"
    CIRCUIT_BREAKER = "circuit_breaker"
    DRAWDOWN = "drawdown"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"


# ==================== DATA CLASSES ====================

@dataclass
class ActivityEvent:
    """Represents a single activity event"""
    timestamp: datetime
    event_type: EventType
    message: str
    details: Dict[str, Any]
    severity: AlertSeverity = AlertSeverity.INFO
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'message': self.message,
            'details': self.details,
            'severity': self.severity.value
        }


@dataclass
class StrategySignal:
    """Real-time strategy signal"""
    strategy_name: str
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    indicators: Dict[str, float]
    ensemble_vote: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'confidence': round(self.confidence, 3),
            'timestamp': self.timestamp.isoformat(),
            'indicators': {k: round(v, 4) for k, v in self.indicators.items()},
            'ensemble_vote': self.ensemble_vote
        }


@dataclass
class OpenPosition:
    """Open position monitoring"""
    position_id: str
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    current_price: float
    size: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    time_in_position: timedelta
    stop_loss: float
    stop_loss_pct: float  # % of stop loss reached
    take_profit: Optional[float] = None
    strategy: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': round(self.entry_price, 4),
            'current_price': round(self.current_price, 4),
            'size': round(self.size, 4),
            'unrealized_pnl': round(self.unrealized_pnl, 2),
            'unrealized_pnl_pct': round(self.unrealized_pnl_pct, 2),
            'time_in_position': str(self.time_in_position),
            'stop_loss': round(self.stop_loss, 4),
            'stop_loss_pct': round(self.stop_loss_pct, 2),
            'take_profit': round(self.take_profit, 4) if self.take_profit else None,
            'strategy': self.strategy
        }


@dataclass
class BrowserAlert:
    """Browser notification alert"""
    title: str
    message: str
    severity: AlertSeverity
    timestamp: datetime
    action_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'timestamp': self.timestamp.isoformat(),
            'action_url': self.action_url
        }


# ==================== LIVE MONITOR ====================

class LiveMonitor:
    """
    Real-time monitoring system for bot operations.
    
    Features:
    - Activity log stream (last 50 events)
    - Strategy signals monitoring
    - Open positions tracking
    - Browser alerts for critical events
    """
    
    def __init__(self, max_events: int = 50, enable_alerts: bool = True):
        """
        Initialize Live Monitor.
        
        Args:
            max_events: Maximum number of events to keep in memory
            enable_alerts: Enable browser notifications
        """
        self.max_events = max_events
        self.enable_alerts = enable_alerts
        
        # Thread-safe deque for activity events
        self.activity_log: deque = deque(maxlen=max_events)
        self._lock = threading.Lock()
        
        # Strategy signals (latest per strategy-symbol)
        self.strategy_signals: Dict[str, StrategySignal] = {}
        
        # Open positions (keyed by position_id)
        self.open_positions: Dict[str, OpenPosition] = {}
        
        # Pending browser alerts
        self.pending_alerts: deque = deque(maxlen=20)
        
        # Statistics
        self.stats = {
            'total_events': 0,
            'events_by_type': {et.value: 0 for et in EventType},
            'total_alerts': 0,
            'last_update': datetime.now()
        }
        
        logger.info(f"LiveMonitor v4.3 initialized (max_events={max_events}, alerts={enable_alerts})")
    
    # ==================== ACTIVITY LOG ====================
    
    def log_event(self, 
                  event_type: EventType, 
                  message: str, 
                  details: Dict[str, Any] = None,
                  severity: AlertSeverity = AlertSeverity.INFO) -> None:
        """
        Log an activity event.
        
        Args:
            event_type: Type of event
            message: Human-readable message
            details: Additional event details
            severity: Event severity
        """
        if details is None:
            details = {}
        
        event = ActivityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            message=message,
            details=details,
            severity=severity
        )
        
        with self._lock:
            self.activity_log.append(event)
            self.stats['total_events'] += 1
            self.stats['events_by_type'][event_type.value] += 1
            self.stats['last_update'] = datetime.now()
        
        logger.debug(f"Event logged: {event_type.value} - {message}")
        
        # Check if alert should be triggered
        if self.enable_alerts and severity in [AlertSeverity.WARNING, AlertSeverity.CRITICAL]:
            self._maybe_trigger_alert(event)
    
    def get_activity_log(self, 
                         event_type: Optional[EventType] = None,
                         limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent activity events.
        
        Args:
            event_type: Filter by event type (None = all)
            limit: Maximum number of events to return
        
        Returns:
            List of event dictionaries
        """
        with self._lock:
            events = list(self.activity_log)
        
        # Filter by type if specified
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Sort by timestamp (newest first) and limit
        events = sorted(events, key=lambda x: x.timestamp, reverse=True)[:limit]
        
        return [e.to_dict() for e in events]
    
    def clear_activity_log(self) -> None:
        """Clear all activity events"""
        with self._lock:
            self.activity_log.clear()
        logger.info("Activity log cleared")
    
    # ==================== STRATEGY SIGNALS ====================
    
    def update_signal(self, signal: StrategySignal) -> None:
        """
        Update real-time strategy signal.
        
        Args:
            signal: Strategy signal to update
        """
        key = f"{signal.strategy_name}_{signal.symbol}"
        
        with self._lock:
            self.strategy_signals[key] = signal
        
        # Log signal as event
        self.log_event(
            EventType.SIGNAL,
            f"{signal.strategy_name}: {signal.signal_type} {signal.symbol}",
            details={
                'confidence': signal.confidence,
                'ensemble_vote': signal.ensemble_vote,
                'indicators': signal.indicators
            },
            severity=AlertSeverity.INFO
        )
    
    def get_strategy_signals(self, strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current strategy signals.
        
        Args:
            strategy_name: Filter by strategy name (None = all)
        
        Returns:
            List of signal dictionaries
        """
        with self._lock:
            signals = list(self.strategy_signals.values())
        
        # Filter by strategy if specified
        if strategy_name:
            signals = [s for s in signals if s.strategy_name == strategy_name]
        
        # Sort by timestamp (newest first)
        signals = sorted(signals, key=lambda x: x.timestamp, reverse=True)
        
        return [s.to_dict() for s in signals]
    
    def clear_signals(self) -> None:
        """Clear all strategy signals"""
        with self._lock:
            self.strategy_signals.clear()
        logger.info("Strategy signals cleared")
    
    # ==================== POSITION MONITORING ====================
    
    def update_position(self, position: OpenPosition) -> None:
        """
        Update open position.
        
        Args:
            position: Position to update
        """
        with self._lock:
            self.open_positions[position.position_id] = position
        
        logger.debug(f"Position updated: {position.position_id} - P&L: {position.unrealized_pnl_pct:.2f}%")
    
    def close_position(self, position_id: str, final_pnl: float, final_pnl_pct: float) -> None:
        """
        Mark position as closed.
        
        Args:
            position_id: ID of position to close
            final_pnl: Final P&L in currency
            final_pnl_pct: Final P&L in percentage
        """
        with self._lock:
            position = self.open_positions.pop(position_id, None)
        
        if position:
            # Log position close event
            self.log_event(
                EventType.POSITION_CLOSE,
                f"Closed {position.side} {position.symbol}",
                details={
                    'final_pnl': final_pnl,
                    'final_pnl_pct': final_pnl_pct,
                    'entry_price': position.entry_price,
                    'exit_price': position.current_price,
                    'time_in_position': str(position.time_in_position)
                },
                severity=AlertSeverity.SUCCESS if final_pnl > 0 else AlertSeverity.WARNING
            )
            
            # Trigger alert for significant profit
            if self.enable_alerts and final_pnl_pct > 5.0:
                self._trigger_alert(
                    title="\ud83d\ude80 Profitable Position Closed",
                    message=f"{position.symbol}: +{final_pnl_pct:.2f}% profit",
                    severity=AlertSeverity.SUCCESS
                )
            
            logger.info(f"Position closed: {position_id} - Final P&L: {final_pnl_pct:.2f}%")
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions.
        
        Returns:
            List of position dictionaries
        """
        with self._lock:
            positions = list(self.open_positions.values())
        
        # Sort by unrealized P&L (most profitable first)
        positions = sorted(positions, key=lambda x: x.unrealized_pnl_pct, reverse=True)
        
        return [p.to_dict() for p in positions]
    
    # ==================== ALERTS SYSTEM ====================
    
    def _maybe_trigger_alert(self, event: ActivityEvent) -> None:
        """
        Check if event should trigger a browser alert.
        
        Args:
            event: Activity event to check
        """
        # Circuit breaker activation
        if event.event_type == EventType.CIRCUIT_BREAKER:
            self._trigger_alert(
                title="\u26a0\ufe0f Circuit Breaker Activated",
                message=event.message,
                severity=AlertSeverity.CRITICAL
            )
        
        # High drawdown
        elif event.event_type == EventType.DRAWDOWN:
            drawdown_pct = event.details.get('drawdown_pct', 0)
            if drawdown_pct > 10.0:
                self._trigger_alert(
                    title="\ud83d\udcc9 High Drawdown Alert",
                    message=f"Current drawdown: {drawdown_pct:.2f}%",
                    severity=AlertSeverity.WARNING
                )
        
        # Critical errors
        elif event.event_type == EventType.ERROR and event.severity == AlertSeverity.CRITICAL:
            self._trigger_alert(
                title="\u274c Critical Error",
                message=event.message,
                severity=AlertSeverity.CRITICAL
            )
    
    def _trigger_alert(self, title: str, message: str, severity: AlertSeverity, action_url: str = None) -> None:
        """
        Trigger a browser alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity
            action_url: Optional URL for action button
        """
        alert = BrowserAlert(
            title=title,
            message=message,
            severity=severity,
            timestamp=datetime.now(),
            action_url=action_url
        )
        
        with self._lock:
            self.pending_alerts.append(alert)
            self.stats['total_alerts'] += 1
        
        logger.info(f"Alert triggered: {title} - {message}")
    
    def get_pending_alerts(self, clear: bool = True) -> List[Dict[str, Any]]:
        """
        Get pending browser alerts.
        
        Args:
            clear: Clear alerts after retrieval
        
        Returns:
            List of alert dictionaries
        """
        with self._lock:
            alerts = list(self.pending_alerts)
            if clear:
                self.pending_alerts.clear()
        
        return [a.to_dict() for a in alerts]
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get monitoring statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            stats = self.stats.copy()
            stats['activity_log_size'] = len(self.activity_log)
            stats['strategy_signals_count'] = len(self.strategy_signals)
            stats['open_positions_count'] = len(self.open_positions)
            stats['pending_alerts_count'] = len(self.pending_alerts)
            stats['last_update'] = stats['last_update'].isoformat()
        
        return stats
    
    def reset_statistics(self) -> None:
        """Reset monitoring statistics"""
        with self._lock:
            self.stats = {
                'total_events': 0,
                'events_by_type': {et.value: 0 for et in EventType},
                'total_alerts': 0,
                'last_update': datetime.now()
            }
        logger.info("Statistics reset")


# ==================== GLOBAL INSTANCE ====================

# Global live monitor instance
_live_monitor: Optional[LiveMonitor] = None


def get_live_monitor() -> LiveMonitor:
    """
    Get or create global LiveMonitor instance.
    
    Returns:
        Global LiveMonitor instance
    """
    global _live_monitor
    if _live_monitor is None:
        _live_monitor = LiveMonitor()
    return _live_monitor


def initialize_live_monitor(max_events: int = 50, enable_alerts: bool = True) -> LiveMonitor:
    """
    Initialize global LiveMonitor with custom settings.
    
    Args:
        max_events: Maximum number of events to keep
        enable_alerts: Enable browser notifications
    
    Returns:
        Initialized LiveMonitor instance
    """
    global _live_monitor
    _live_monitor = LiveMonitor(max_events=max_events, enable_alerts=enable_alerts)
    return _live_monitor
