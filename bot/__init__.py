"""Bot module for trading automation and strategy execution.

This module provides the main trading bot functionality.
Imports are done lazily to avoid circular dependencies.
"""

# Lazy imports to avoid circular dependencies and initialization issues
# Do NOT import from bot.main at module level as it triggers config loading

__all__ = [
    'BotV2',
    'main',
]


def get_bot_class():
    """Get the BotV2 class (lazy import)"""
    from bot.main import BotV2
    return BotV2


def main():
    """Run the bot (lazy import)"""
    from bot.main import main as run_main
    return run_main()
