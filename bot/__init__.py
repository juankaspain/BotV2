"""Bot module for trading automation and strategy execution."""

from bot.main import run_bot
from bot.core.execution_engine import ExecutionEngine as TradingEngine
from bot.strategies import BaseStrategy
from bot.exchanges import BaseExchange

__all__ = [
    'run_bot',
    'TradingEngine',
    'BaseStrategy',
    'BaseExchange',
]
