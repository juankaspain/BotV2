"""Bot module for trading automation and strategy execution."""

from bot.main import run_bot
from bot.engine import TradingEngine
from bot.strategies import BaseStrategy
from bot.exchanges import BaseExchange

__all__ = [
    'run_bot',
    'TradingEngine',
    'BaseStrategy',
    'BaseExchange',
]
