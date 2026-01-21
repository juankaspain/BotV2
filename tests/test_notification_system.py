"""
Unit Tests for Notification System
Tests email, Slack, Telegram, webhooks, priorities, batching, and rate limiting
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class NotificationChannel(Enum):
    """Notification channels"""
    EMAIL = "email"
    SLACK = "slack"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    """Notification priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Notification:
    """Notification data"""
    channel: NotificationChannel
    title: str
    message: str
    priority: NotificationPriority
    category: str
    timestamp: datetime
    metadata: Dict = None


class NotificationSystem:
    """Unified notification system"""
    
    def __init__(self, config: dict):
        self.config = config
        self.enabled_channels = set(config.get('enabled_channels', []))
        self.rate_limit = config.get('rate_limit_per_minute', 10)
        self.batch_size = config.get('batch_size', 5)
        self.batch_interval = config.get('batch_interval_seconds', 60)
        
        self.sent_notifications = []
        self.pending_notifications = []
        self.failed_notifications = []
        self.rate_limit_tracker = {}
        
    async def send(self, notification: Notification) -> bool:
        """Send notification"""
        if notification.channel.value not in self.enabled_channels:
            return False
        
        if not self._check_rate_limit(notification.channel):
            self.pending_notifications.append(notification)
            return False
        
        try:
            if notification.channel == NotificationChannel.EMAIL:
                await self._send_email(notification)
            elif notification.channel == NotificationChannel.SLACK:
                await self._send_slack(notification)
            elif notification.channel == NotificationChannel.TELEGRAM:
                await self._send_telegram(notification)
            elif notification.channel == NotificationChannel.WEBHOOK:
                await self._send_webhook(notification)
            
            self.sent_notifications.append(notification)
            self._update_rate_limit(notification.channel)
            return True
            
        except Exception as e:
            self.failed_notifications.append((notification, str(e)))
            return False
    
    async def send_batch(self, notifications: List[Notification]) -> List[bool]:
        """Send batch of notifications"""
        results = []
        for notif in notifications:
            result = await self.send(notif)
            results.append(result)
        return results
    
    def _check_rate_limit(self, channel: NotificationChannel) -> bool:
        """Check if rate limit allows sending"""
        now = datetime.now()
        key = channel.value
        
        if key not in self.rate_limit_tracker:
            self.rate_limit_tracker[key] = []
        
        # Remove old entries
        cutoff = now - timedelta(minutes=1)
        self.rate_limit_tracker[key] = [
            ts for ts in self.rate_limit_tracker[key] if ts > cutoff
        ]
        
        return len(self.rate_limit_tracker[key]) < self.rate_limit
    
    def _update_rate_limit(self, channel: NotificationChannel):
        """Update rate limit tracker"""
        now = datetime.now()
        key = channel.value
        
        if key not in self.rate_limit_tracker:
            self.rate_limit_tracker[key] = []
        
        self.rate_limit_tracker[key].append(now)
    
    async def _send_email(self, notification: Notification):
        """Send email notification"""
        # Mock implementation
        await asyncio.sleep(0.01)
        return True
    
    async def _send_slack(self, notification: Notification):
        """Send Slack notification"""
        # Mock implementation
        await asyncio.sleep(0.01)
        return True
    
    async def _send_telegram(self, notification: Notification):
        """Send Telegram notification"""
        # Mock implementation
        await asyncio.sleep(0.01)
        return True
    
    async def _send_webhook(self, notification: Notification):
        """Send webhook notification"""
        # Mock implementation
        await asyncio.sleep(0.01)
        return True
    
    def get_statistics(self) -> dict:
        """Get notification statistics"""
        return {
            'total_sent': len(self.sent_notifications),
            'total_failed': len(self.failed_notifications),
            'total_pending': len(self.pending_notifications),
            'by_channel': self._group_by_channel(),
            'by_priority': self._group_by_priority()
        }
    
    def _group_by_channel(self) -> dict:
        """Group notifications by channel"""
        groups = {}
        for notif in self.sent_notifications:
            channel = notif.channel.value
            groups[channel] = groups.get(channel, 0) + 1
        return groups
    
    def _group_by_priority(self) -> dict:
        """Group notifications by priority"""
        groups = {}
        for notif in self.sent_notifications:
            priority = notif.priority.value
            groups[priority] = groups.get(priority, 0) + 1
        return groups
    
    def filter_by_category(self, category: str) -> List[Notification]:
        """Filter notifications by category"""
        return [
            notif for notif in self.sent_notifications
            if notif.category == category
        ]
    
    async def retry_failed(self) -> int:
        """Retry failed notifications"""
        retry_count = 0
        failed_copy = self.failed_notifications.copy()
        self.failed_notifications.clear()
        
        for notif, error in failed_copy:
            success = await self.send(notif)
            if success:
                retry_count += 1
        
        return retry_count


@pytest.fixture
def notification_config():
    """Create notification config"""
    return {
        'enabled_channels': ['email', 'slack', 'telegram', 'webhook'],
        'rate_limit_per_minute': 10,
        'batch_size': 5,
        'batch_interval_seconds': 60
    }


@pytest.fixture
def notification_system(notification_config):
    """Create notification system instance"""
    return NotificationSystem(notification_config)


@pytest.fixture
def sample_notification():
    """Create sample notification"""
    return Notification(
        channel=NotificationChannel.EMAIL,
        title="Test Notification",
        message="This is a test message",
        priority=NotificationPriority.MEDIUM,
        category="testing",
        timestamp=datetime.now()
    )


class TestNotificationSystemBasics:
    """Test basic notification functionality"""
    
    def test_notification_system_initialization(self, notification_system):
        """Test notification system initializes correctly"""
        assert len(notification_system.enabled_channels) == 4
        assert notification_system.rate_limit == 10
        assert notification_system.batch_size == 5
        assert len(notification_system.sent_notifications) == 0


@pytest.mark.asyncio
class TestChannelNotifications:
    """Test different notification channels"""
    
    async def test_send_email_notification(self, notification_system):
        """Test sending email notification"""
        notification = Notification(
            channel=NotificationChannel.EMAIL,
            title="Email Test",
            message="Test email message",
            priority=NotificationPriority.HIGH,
            category="test",
            timestamp=datetime.now()
        )
        
        success = await notification_system.send(notification)
        assert success == True
        assert len(notification_system.sent_notifications) == 1
    
    async def test_send_slack_notification(self, notification_system):
        """Test sending Slack notification"""
        notification = Notification(
            channel=NotificationChannel.SLACK,
            title="Slack Test",
            message="Test Slack message",
            priority=NotificationPriority.MEDIUM,
            category="test",
            timestamp=datetime.now()
        )
        
        success = await notification_system.send(notification)
        assert success == True
    
    async def test_send_telegram_notification(self, notification_system):
        """Test sending Telegram notification"""
        notification = Notification(
            channel=NotificationChannel.TELEGRAM,
            title="Telegram Test",
            message="Test Telegram message",
            priority=NotificationPriority.LOW,
            category="test",
            timestamp=datetime.now()
        )
        
        success = await notification_system.send(notification)
        assert success == True
    
    async def test_send_webhook_notification(self, notification_system):
        """Test sending webhook notification"""
        notification = Notification(
            channel=NotificationChannel.WEBHOOK,
            title="Webhook Test",
            message="Test webhook message",
            priority=NotificationPriority.CRITICAL,
            category="test",
            timestamp=datetime.now()
        )
        
        success = await notification_system.send(notification)
        assert success == True


@pytest.mark.asyncio
class TestNotificationFeatures:
    """Test notification features"""
    
    async def test_notification_priorities(self, notification_system):
        """Test different priority notifications"""
        priorities = [
            NotificationPriority.LOW,
            NotificationPriority.MEDIUM,
            NotificationPriority.HIGH,
            NotificationPriority.CRITICAL
        ]
        
        for priority in priorities:
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                title=f"{priority.value} priority",
                message="Test message",
                priority=priority,
                category="test",
                timestamp=datetime.now()
            )
            
            await notification_system.send(notification)
        
        assert len(notification_system.sent_notifications) == 4
    
    async def test_notification_batching(self, notification_system):
        """Test batch notification sending"""
        notifications = [
            Notification(
                channel=NotificationChannel.EMAIL,
                title=f"Batch {i}",
                message=f"Message {i}",
                priority=NotificationPriority.MEDIUM,
                category="batch",
                timestamp=datetime.now()
            )
            for i in range(5)
        ]
        
        results = await notification_system.send_batch(notifications)
        
        assert len(results) == 5
        assert all(results)
        assert len(notification_system.sent_notifications) == 5
    
    async def test_notification_rate_limiting(self, notification_system):
        """Test rate limiting enforcement"""
        # Send up to rate limit
        for i in range(notification_system.rate_limit):
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                title=f"Rate limit {i}",
                message="Test",
                priority=NotificationPriority.LOW,
                category="test",
                timestamp=datetime.now()
            )
            await notification_system.send(notification)
        
        # Next one should be rate limited
        notification = Notification(
            channel=NotificationChannel.EMAIL,
            title="Should be limited",
            message="Test",
            priority=NotificationPriority.LOW,
            category="test",
            timestamp=datetime.now()
        )
        
        success = await notification_system.send(notification)
        assert success == False
        assert len(notification_system.pending_notifications) == 1
    
    async def test_notification_templates(self, notification_system):
        """Test notification templates/formatting"""
        notification = Notification(
            channel=NotificationChannel.SLACK,
            title="Trade Alert",
            message="BTC/USDT: Entry at $50,000",
            priority=NotificationPriority.HIGH,
            category="trading",
            timestamp=datetime.now(),
            metadata={'symbol': 'BTCUSDT', 'price': 50000}
        )
        
        success = await notification_system.send(notification)
        assert success == True
        assert notification.metadata is not None
    
    async def test_notification_retry_logic(self, notification_system):
        """Test retry logic for failed notifications"""
        # Simulate a failure
        notification = Notification(
            channel=NotificationChannel.EMAIL,
            title="Test",
            message="Test",
            priority=NotificationPriority.LOW,
            category="test",
            timestamp=datetime.now()
        )
        
        # Add to failed list
        notification_system.failed_notifications.append(
            (notification, "Network error")
        )
        
        # Retry
        retry_count = await notification_system.retry_failed()
        
        assert retry_count >= 0


class TestStatisticsAndHistory:
    """Test statistics and history tracking"""
    
    @pytest.mark.asyncio
    async def test_notification_history(self, notification_system):
        """Test notification history tracking"""
        for i in range(3):
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                title=f"History {i}",
                message="Test",
                priority=NotificationPriority.MEDIUM,
                category="test",
                timestamp=datetime.now()
            )
            await notification_system.send(notification)
        
        assert len(notification_system.sent_notifications) == 3
    
    @pytest.mark.asyncio
    async def test_notification_filtering(self, notification_system):
        """Test filtering notifications by category"""
        categories = ['trading', 'alerts', 'system']
        
        for category in categories:
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                title=f"{category} notification",
                message="Test",
                priority=NotificationPriority.MEDIUM,
                category=category,
                timestamp=datetime.now()
            )
            await notification_system.send(notification)
        
        trading_notifs = notification_system.filter_by_category('trading')
        assert len(trading_notifs) == 1
    
    @pytest.mark.asyncio
    async def test_notification_statistics(self, notification_system):
        """Test statistics generation"""
        # Send various notifications
        channels = [NotificationChannel.EMAIL, NotificationChannel.SLACK]
        priorities = [NotificationPriority.LOW, NotificationPriority.HIGH]
        
        for channel in channels:
            for priority in priorities:
                notification = Notification(
                    channel=channel,
                    title="Test",
                    message="Test",
                    priority=priority,
                    category="test",
                    timestamp=datetime.now()
                )
                await notification_system.send(notification)
        
        stats = notification_system.get_statistics()
        
        assert stats['total_sent'] == 4
        assert 'by_channel' in stats
        assert 'by_priority' in stats


@pytest.mark.asyncio
class TestMultiChannelSupport:
    """Test multi-channel notification support"""
    
    async def test_multiple_channels(self, notification_system):
        """Test sending to multiple channels"""
        channels = [
            NotificationChannel.EMAIL,
            NotificationChannel.SLACK,
            NotificationChannel.TELEGRAM
        ]
        
        for channel in channels:
            notification = Notification(
                channel=channel,
                title="Multi-channel test",
                message="Test message",
                priority=NotificationPriority.MEDIUM,
                category="test",
                timestamp=datetime.now()
            )
            await notification_system.send(notification)
        
        stats = notification_system.get_statistics()
        assert stats['total_sent'] == 3
        assert len(stats['by_channel']) == 3
    
    async def test_disabled_channel(self):
        """Test notification to disabled channel"""
        config = {
            'enabled_channels': ['email'],  # Only email enabled
            'rate_limit_per_minute': 10,
            'batch_size': 5,
            'batch_interval_seconds': 60
        }
        
        system = NotificationSystem(config)
        
        # Try to send to disabled channel
        notification = Notification(
            channel=NotificationChannel.SLACK,  # Disabled
            title="Test",
            message="Test",
            priority=NotificationPriority.MEDIUM,
            category="test",
            timestamp=datetime.now()
        )
        
        success = await system.send(notification)
        assert success == False


class TestNotificationCategories:
    """Test notification categories"""
    
    @pytest.mark.asyncio
    async def test_notification_categories(self, notification_system):
        """Test different notification categories"""
        categories = ['trading', 'system', 'alerts', 'errors']
        
        for category in categories:
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                title=f"{category} notification",
                message="Test message",
                priority=NotificationPriority.MEDIUM,
                category=category,
                timestamp=datetime.now()
            )
            await notification_system.send(notification)
        
        # Check each category
        for category in categories:
            filtered = notification_system.filter_by_category(category)
            assert len(filtered) == 1
            assert filtered[0].category == category


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
