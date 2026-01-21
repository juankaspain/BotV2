"""
Tests for Notification System
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.notifications.telegram_notifier import TelegramNotifier, AlertLevel
from src.notifications.email_notifier import EmailNotifier
from src.notifications.alert_dispatcher import AlertDispatcher


class TestTelegramNotifier:
    """Test Telegram notifications"""
    
    def test_initialization_with_credentials(self):
        """Test initialization with credentials"""
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        assert notifier.enabled
        assert notifier.bot_token == "test_token"
        assert notifier.chat_id == "123456"
    
    def test_initialization_without_credentials(self):
        """Test initialization without credentials"""
        with patch.dict('os.environ', {}, clear=True):
            notifier = TelegramNotifier()
            assert not notifier.enabled
    
    @patch('requests.post')
    def test_send_message_success(self, mock_post):
        """Test sending message successfully"""
        mock_post.return_value.status_code = 200
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        result = notifier.send_message("Test message")
        assert result is True
        assert notifier.messages_sent == 1
        assert mock_post.called
    
    @patch('requests.post')
    def test_send_alert(self, mock_post):
        """Test sending formatted alert"""
        mock_post.return_value.status_code = 200
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        result = notifier.send_alert(
            "Test Alert",
            level=AlertLevel.WARNING,
            details={"key": "value"}
        )
        
        assert result is True
        assert mock_post.called
    
    @patch('requests.post')
    def test_circuit_breaker_alert(self, mock_post):
        """Test circuit breaker alert"""
        mock_post.return_value.status_code = 200
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        result = notifier.send_circuit_breaker_alert(
            "exchange_api",
            "OPEN",
            "Threshold reached"
        )
        
        assert result is True
    
    @patch('requests.post')
    def test_drawdown_alert(self, mock_post):
        """Test drawdown alert"""
        mock_post.return_value.status_code = 200
        
        notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="123456"
        )
        
        result = notifier.send_drawdown_alert(
            drawdown_pct=12.5,
            current_equity=8750,
            peak_equity=10000
        )
        
        assert result is True


class TestEmailNotifier:
    """Test email notifications"""
    
    def test_initialization_with_config(self):
        """Test initialization with configuration"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password",
            from_email="test@example.com",
            to_emails=["recipient@example.com"]
        )
        
        assert notifier.enabled
    
    def test_initialization_without_config(self):
        """Test initialization without configuration"""
        with patch.dict('os.environ', {}, clear=True):
            notifier = EmailNotifier()
            assert not notifier.enabled
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test sending email successfully"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password",
            from_email="test@example.com",
            to_emails=["recipient@example.com"]
        )
        
        result = notifier.send_email(
            "Test Subject",
            "Test Body",
            html=False
        )
        
        # Mock will succeed by default
        assert result is True
        assert notifier.emails_sent == 1
    
    @patch('smtplib.SMTP')
    def test_send_daily_summary(self, mock_smtp):
        """Test sending daily summary"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password",
            from_email="test@example.com",
            to_emails=["recipient@example.com"]
        )
        
        result = notifier.send_daily_summary(
            total_pnl=150.50,
            trades_count=10,
            win_rate=65.0,
            equity=10150.50
        )
        
        assert result is True
    
    @patch('smtplib.SMTP')
    def test_send_critical_drawdown_alert(self, mock_smtp):
        """Test sending critical drawdown alert"""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password",
            from_email="test@example.com",
            to_emails=["recipient@example.com"]
        )
        
        result = notifier.send_critical_drawdown_alert(
            drawdown_pct=15.0,
            current_equity=8500,
            peak_equity=10000
        )
        
        assert result is True


class TestAlertDispatcher:
    """Test alert dispatcher"""
    
    def test_initialization(self):
        """Test dispatcher initialization"""
        telegram = Mock()
        telegram.enabled = True
        email = Mock()
        email.enabled = True
        
        dispatcher = AlertDispatcher(
            telegram_notifier=telegram,
            email_notifier=email
        )
        
        assert dispatcher.telegram == telegram
        assert dispatcher.email == email
    
    def test_send_critical_alert_routes_to_both(self):
        """Test critical alerts route to Telegram + Email"""
        telegram = Mock()
        telegram.enabled = True
        telegram.send_alert = Mock(return_value=True)
        
        email = Mock()
        email.enabled = True
        email.send_email = Mock(return_value=True)
        
        dispatcher = AlertDispatcher(
            telegram_notifier=telegram,
            email_notifier=email
        )
        
        dispatcher.send_alert(
            "Critical Issue",
            AlertLevel.CRITICAL,
            channels=None  # Auto-route
        )
        
        assert telegram.send_alert.called
        assert email.send_email.called
    
    def test_send_warning_alert_routes_to_telegram(self):
        """Test warning alerts route to Telegram only"""
        telegram = Mock()
        telegram.enabled = True
        telegram.send_alert = Mock(return_value=True)
        
        email = Mock()
        email.enabled = True
        email.send_email = Mock(return_value=True)
        
        dispatcher = AlertDispatcher(
            telegram_notifier=telegram,
            email_notifier=email,
            enable_rate_limiting=False
        )
        
        dispatcher.send_alert(
            "Warning",
            AlertLevel.WARNING,
            channels=None
        )
        
        assert telegram.send_alert.called
        assert not email.send_email.called
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        telegram = Mock()
        telegram.enabled = True
        telegram.send_alert = Mock(return_value=True)
        
        dispatcher = AlertDispatcher(
            telegram_notifier=telegram,
            enable_rate_limiting=True
        )
        
        # Send many alerts
        for i in range(25):
            dispatcher.send_alert(
                f"Alert {i}",
                AlertLevel.INFO,
                channels=['telegram'],
                bypass_dedup=True
            )
        
        # Some should be rate limited
        assert dispatcher.alerts_sent['rate_limited'] > 0
    
    def test_deduplication(self):
        """Test alert deduplication"""
        telegram = Mock()
        telegram.enabled = True
        telegram.send_alert = Mock(return_value=True)
        
        dispatcher = AlertDispatcher(
            telegram_notifier=telegram,
            enable_rate_limiting=False
        )
        
        # Send same alert twice
        for _ in range(2):
            dispatcher.send_alert(
                "Same Alert",
                AlertLevel.INFO,
                channels=['telegram']
            )
        
        # Second should be deduplicated
        assert dispatcher.alerts_sent['deduplicated'] == 1
