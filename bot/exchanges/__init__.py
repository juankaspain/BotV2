"""
Exchange Adapters for BotV2

Supported exchanges:
- Binance (active)
- Coinbase Pro (optional)
- Kraken (optional)
- Finst (preparatory - API not yet available)
"""

from .binance_adapter import BinanceAdapter
from .coinbase_adapter import CoinbaseAdapter
from .kraken_adapter import KrakenAdapter
from .finst_adapter import FinstAdapter

__all__ = [
    'BinanceAdapter',
    'CoinbaseAdapter',
    'KrakenAdapter',
    'FinstAdapter',
]
