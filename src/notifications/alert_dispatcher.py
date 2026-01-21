"""
Alert Dispatcher
Routes alerts to appropriate channels based on severity and type
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
import time

from .telegram_notifier import TelegramNotifier, AlertLevel
from .email_notifier import EmailNotifier

logger = logging.getLogger(__name__)


class AlertDispatcher:
    """
    Central alert dispatcher for routing notifications
    
    Features:
    - Multi-channel routing (Telegram, Email)
    - Priority-based routing
    - Rate limiting per channel
    - Alert deduplication
    - Circuit breaker integration
    - Drawdown monitoring
    
    Routing Rules:
    - CRITICAL alerts → Telegram + Email
    - WARNING alerts → Telegram
    - INFO alerts → Email (daily summary)
    - Circuit breaker OPEN → Telegram INSTANT
    - Drawdown >10% → Telegram + Email
    """
    
    def __init__(self,
                 telegram_notifier: Optional[TelegramNotifier] = None,
                 email_notifier: Optional[EmailNotifier] = None,
                 enable_rate_limiting: bool = True):
        """
        Initialize alert dispatcher
        
        Args:
            telegram_notifier: Telegram notifier instance
            email_notifier: Email notifier instance
            enable_rate_limiting: Enable rate limiting
        """
        self.telegram = telegram_notifier or TelegramNotifier()
        self.email = email_notifier or EmailNotifier()
        self.enable_rate_limiting = enable_rate_limiting
        
        # Rate limiting
        self.rate_limits = {
            'telegram': {'max_per_hour': 20, 'tokens': []},
            'email': {'max_per_hour': 10, 'tokens': []}
        }
        
        # Alert deduplication
        self.recent_alerts = defaultdict(list)  # key -> [timestamps]
        self.dedup_window = 300  # 5 minutes
        
        # Drawdown monitoring
        self.last_drawdown_alert = None
        self.drawdown_alert_cooldown = 3600  # 1 hour
        
        # Statistics
        self.alerts_sent = {
            'telegram': 0,
            'email': 0,
            'rate_limited': 0,
            'deduplicated': 0
        }
        
        logger.info(
            f"✓ Alert Dispatcher initialized "
            f"(Telegram: {self.telegram.enabled}, Email: {self.email.enabled})"
        )
    
    def _check_rate_limit(self, channel: str) -> bool:
        """
        Check if channel is rate limited
        
        Args:
            channel: Channel name (telegram/email)
            
        Returns:
            True if allowed, False if rate limited
        """
        if not self.enable_rate_limiting:
            return True
        
        now = time.time()
        config = self.rate_limits[channel]
        
        # Remove old tokens
        config['tokens'] = [
            t for t in config['tokens']
            if now - t < 3600  # 1 hour window
        ]
        
        # Check limit
        if len(config['tokens']) >= config['max_per_hour']:
            logger.warning(f"Rate limit reached for {channel}")
            self.alerts_sent['rate_limited'] += 1
            return False
        
        # Add token
        config['tokens'].append(now)
        return True
    
    def _is_duplicate(self, alert_key: str) -> bool:
        """
        Check if alert is duplicate
        
        Args:
            alert_key: Alert identification key
            
        Returns:
            True if duplicate, False otherwise
        """
        now = time.time()
        
        # Remove old alerts
        self.recent_alerts[alert_key] = [
            t for t in self.recent_alerts[alert_key]
            if now - t < self.dedup_window
        ]
        
        # Check if exists
        if self.recent_alerts[alert_key]:
            logger.debug(f"Duplicate alert suppressed: {alert_key}")
            self.alerts_sent['deduplicated'] += 1
            return True
        
        # Add alert
        self.recent_alerts[alert_key].append(now)
        return False
    
    def send_alert(self,
                   title: str,
                   level: AlertLevel,
                   details: Optional[Dict] = None,
                   channels: Optional[List[str]] = None,
                   bypass_rate_limit: bool = False,
                   bypass_dedup: bool = False) -> Dict[str, bool]:
        """
        Send alert to appropriate channels
        
        Args:
            title: Alert title
            level: Alert level
            details: Alert details
            channels: Specific channels to use (None = auto-route)
            bypass_rate_limit: Skip rate limiting
            bypass_dedup: Skip deduplication
            
        Returns:
            Dict of channel -> success status
        """
        results = {}
        
        # Auto-route if channels not specified
        if channels is None:
            if level == AlertLevel.CRITICAL:
                channels = ['telegram', 'email']
            elif level == AlertLevel.WARNING:
                channels = ['telegram']
            else:
                channels = ['email']
        
        # Deduplication check
        alert_key = f"{title}_{level.value}"
        if not bypass_dedup and self._is_duplicate(alert_key):
            return {ch: False for ch in channels}
        
        # Send to each channel
        for channel in channels:
            # Rate limit check
            if not bypass_rate_limit and not self._check_rate_limit(channel):
                results[channel] = False
                continue
            
            # Send
            success = False
            if channel == 'telegram' and self.telegram.enabled:
                success = self.telegram.send_alert(title, level, details)
                if success:
                    self.alerts_sent['telegram'] += 1
            
            elif channel == 'email' and self.email.enabled:
                # Convert to email format
                subject = f"{level.value} - {title}"
                body = self._format_email_body(title, level, details)
                success = self.email.send_email(subject, body, html=True)
                if success:
                    self.alerts_sent['email'] += 1
            
            results[channel] = success
        
        return results
    
    def _format_email_body(self, title: str, level: AlertLevel, details: Optional[Dict]) -> str:
        """Format alert as email HTML"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>{level.value} {title}</h2>
            <p><b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        if details:
            html += "<h3>Details:</h3><ul>"
            for key, value in details.items():
                html += f"<li><b>{key}:</b> {value}</li>"
            html += "</ul>"
        
        html += """
            <p style="margin-top: 30px; color: #666;">
                <small>BotV2 Trading System</small>
            </p>
        </body>
        </html>
        """
        return html
    
    def alert_circuit_breaker(self, name: str, state: str, reason: str) -> Dict[str, bool]:
        """
        Alert circuit breaker state change
        
        Args:
            name: Circuit breaker name
            state: New state
            reason: Reason for change
            
        Returns:
            Channel results
        """
        level = AlertLevel.CRITICAL if state == "OPEN" else AlertLevel.SUCCESS
        
        return self.send_alert(
            f"Circuit Breaker: {name}",
            level=level,
            details={
                "State": state,
                "Reason": reason,
                "Component": name
            },
            channels=['telegram'] if state == "OPEN" else ['telegram'],
            bypass_rate_limit=(state == "OPEN")  # Always send OPEN alerts
        )
    
    def alert_drawdown(self,
                      drawdown_pct: float,
                      current_equity: float,
                      peak_equity: float) -> Dict[str, bool]:
        """
        Alert on drawdown
        
        Args:
            drawdown_pct: Drawdown percentage
            current_equity: Current equity
            peak_equity: Peak equity
            
        Returns:
            Channel results
        """
        # Check cooldown
        now = time.time()
        if self.last_drawdown_alert:
            elapsed = now - self.last_drawdown_alert
            if elapsed < self.drawdown_alert_cooldown:
                logger.debug("Drawdown alert in cooldown period")
                return {}
        
        self.last_drawdown_alert = now
        
        # Determine severity
        if drawdown_pct >= 10:
            level = AlertLevel.CRITICAL
            channels = ['telegram', 'email']
        elif drawdown_pct >= 5:
            level = AlertLevel.WARNING
            channels = ['telegram']
        else:
            level = AlertLevel.WARNING
            channels = ['telegram']
        
        return self.send_alert(
            f"Drawdown Alert: {drawdown_pct:.1f}%",
            level=level,
            details={
                "Drawdown": f"{drawdown_pct:.2f}%",
                "Current Equity": f"${current_equity:,.2f}",
                "Peak Equity": f"${peak_equity:,.2f}",
                "Loss": f"${peak_equity - current_equity:,.2f}"
            },
            channels=channels,
            bypass_rate_limit=(drawdown_pct >= 10)
        )
    
    def send_daily_summary(self,
                          total_pnl: float,
                          trades_count: int,
                          win_rate: float,
                          equity: float,
                          additional_metrics: Optional[Dict] = None) -> Dict[str, bool]:
        """
        Send daily summary (email only)
        
        Args:
            total_pnl: Daily P&L
            trades_count: Number of trades
            win_rate: Win rate
            equity: Current equity
            additional_metrics: Additional metrics
            
        Returns:
            Channel results
        """
        return {
            'email': self.email.send_daily_summary(
                total_pnl, trades_count, win_rate, equity, additional_metrics
            )
        }
    
    def alert_system_startup(self) -> Dict[str, bool]:
        """Alert system startup"""
        return self.send_alert(
            "System Started",
            level=AlertLevel.INFO,
            details={
                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Status": "Operational"
            },
            channels=['telegram']
        )
    
    def alert_system_shutdown(self, reason: str = "Manual") -> Dict[str, bool]:
        """Alert system shutdown"""
        return self.send_alert(
            "System Shutdown",
            level=AlertLevel.WARNING,
            details={
                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Reason": reason
            },
            channels=['telegram', 'email']
        )
    
    def alert_trade(self,
                   symbol: str,
                   action: str,
                   size: float,
                   price: float,
                   reason: str = "") -> Dict[str, bool]:
        """Alert trade execution"""
        return self.send_alert(
            f"Trade: {action} {symbol}",
            level=AlertLevel.INFO,
            details={
                "Symbol": symbol,
                "Action": action,
                "Size": f"{size:.8f}",
                "Price": f"${price:,.2f}",
                "Reason": reason
            } if reason else {
                "Symbol": symbol,
                "Action": action,
                "Size": f"{size:.8f}",
                "Price": f"${price:,.2f}"
            },
            channels=['telegram']
        )
    
    def get_statistics(self) -> Dict:
        """Get dispatcher statistics"""
        return {
            'alerts_sent': self.alerts_sent,
            'telegram_stats': self.telegram.get_statistics(),
            'email_stats': self.email.get_statistics(),
            'rate_limits': {
                'telegram': len(self.rate_limits['telegram']['tokens']),
                'email': len(self.rate_limits['email']['tokens'])
            }
        }
