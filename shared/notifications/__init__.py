"""Notifications module for BotV2.

Provides notification services including:
- Email notifications
- Telegram bot integration
- Slack webhooks
- Discord integration
- Push notifications
- SMS alerts
"""

from shared.notifications.email_notifier import EmailNotifier
from shared.notifications.telegram_notifier import TelegramNotifier
from shared.notifications.slack_notifier import SlackNotifier
from shared.notifications.notification_manager import NotificationManager

__all__ = [
    'EmailNotifier',
    'TelegramNotifier',
    'SlackNotifier',
    'NotificationManager',
]
