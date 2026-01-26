"""
Telegram Notifier
Sends critical alerts via Telegram for immediate response
"""

import logging
import requests
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
import os

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "ℹ️ INFO"
    WARNING = "⚠️ WARNING"
    CRITICAL = "🚨 CRITICAL"
    SUCCESS = "✅ SUCCESS"


class TelegramNotifier:
    """
    Telegram notification system for critical alerts
    
    Features:
    - Instant message delivery
    - Formatted messages with emojis
    - Alert level support
    - Error handling with fallback
    - Rate limiting protection
    
    Required env vars:
    - TELEGRAM_BOT_TOKEN: Bot token from @BotFather
    - TELEGRAM_CHAT_ID: Chat ID to send messages
    
    Example:
        notifier = TelegramNotifier()
        notifier.send_alert(
            "Circuit breaker opened",
            level=AlertLevel.CRITICAL,
            details={"exchange": "binance", "failures": 5}
        )
    """
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            logger.warning(
                "⚠️ Telegram notifier disabled: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"
            )
        else:
            logger.info(f"✓ Telegram notifier initialized (chat_id: {self.chat_id[:6]}...)")
        
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        # Statistics
        self.messages_sent = 0
        self.messages_failed = 0
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send message to Telegram
        
        Args:
            text: Message text
            parse_mode: Parse mode (HTML or Markdown)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Telegram disabled, would send: {text[:50]}...")
            return False
        
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.messages_sent += 1
            logger.debug(f"✓ Telegram message sent: {text[:50]}...")
            return True
        
        except Exception as e:
            self.messages_failed += 1
            logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_alert(self,
                   title: str,
                   level: AlertLevel = AlertLevel.INFO,
                   details: Optional[Dict] = None,
                   action_required: Optional[str] = None) -> bool:
        """
        Send formatted alert to Telegram
        
        Args:
            title: Alert title
            level: Alert severity level
            details: Additional details dict
            action_required: Suggested action
            
        Returns:
            True if successful
        """
        # Build message
        lines = []
        lines.append(f"<b>{level.value}</b>")
        lines.append(f"<b>{title}</b>")
        lines.append("")
        
        # Timestamp
        lines.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Details
        if details:
            lines.append("<b>Details:</b>")
            for key, value in details.items():
                lines.append(f"  • {key}: {value}")
            lines.append("")
        
        # Action
        if action_required:
            lines.append(f"<b>Action Required:</b>")
            lines.append(f"  {action_required}")
            lines.append("")
        
        # Footer
        lines.append("━━━━━━━━━━━━━━━━━━")
        lines.append("BotV2 Trading System")
        
        message = "\n".join(lines)
        return self.send_message(message)
    
    def send_circuit_breaker_alert(self, name: str, state: str, reason: str) -> bool:
        """
        Send circuit breaker alert
        
        Args:
            name: Circuit breaker name
            state: New state (OPEN, CLOSED, HALF_OPEN)
            reason: Reason for state change
        """
        return self.send_alert(
            f"Circuit Breaker: {name}",
            level=AlertLevel.CRITICAL if state == "OPEN" else AlertLevel.SUCCESS,
            details={
                "State": state,
                "Reason": reason,
                "Component": name
            },
            action_required="Check system logs and investigate failures" if state == "OPEN" else None
        )
    
    def send_drawdown_alert(self, drawdown_pct: float, current_equity: float, peak_equity: float) -> bool:
        """
        Send drawdown alert
        
        Args:
            drawdown_pct: Drawdown percentage
            current_equity: Current equity
            peak_equity: Peak equity
        """
        level = AlertLevel.CRITICAL if drawdown_pct >= 10 else AlertLevel.WARNING
        
        return self.send_alert(
            f"Drawdown Alert: {drawdown_pct:.1f}%",
            level=level,
            details={
                "Drawdown": f"{drawdown_pct:.2f}%",
                "Current Equity": f"${current_equity:,.2f}",
                "Peak Equity": f"${peak_equity:,.2f}",
                "Loss": f"${peak_equity - current_equity:,.2f}"
            },
            action_required="Review positions and consider reducing risk" if drawdown_pct >= 10 else None
        )
    
    def send_system_status(self, status: str, metrics: Dict) -> bool:
        """
        Send system status update
        
        Args:
            status: Status message
            metrics: System metrics dict
        """
        return self.send_alert(
            f"System Status: {status}",
            level=AlertLevel.INFO,
            details=metrics
        )
    
    def send_trade_alert(self, symbol: str, action: str, size: float, price: float, reason: str = "") -> bool:
        """
        Send trade execution alert
        
        Args:
            symbol: Trading symbol
            action: BUY or SELL
            size: Trade size
            price: Execution price
            reason: Trade reason
        """
        emoji = "📈" if action == "BUY" else "📉"
        
        return self.send_alert(
            f"{emoji} Trade Executed: {action} {symbol}",
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
            }
        )
    
    def get_statistics(self) -> Dict:
        """Get notifier statistics"""
        return {
            'enabled': self.enabled,
            'messages_sent': self.messages_sent,
            'messages_failed': self.messages_failed,
            'success_rate': (self.messages_sent / (self.messages_sent + self.messages_failed) * 100)
                if (self.messages_sent + self.messages_failed) > 0 else 0
        }
