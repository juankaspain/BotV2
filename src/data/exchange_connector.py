"""
Exchange Connector - Unified Interface for Market Data
Supports Polymarket, CCXT exchanges with fallback mechanisms
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import aiohttp
import ccxt.async_support as ccxt

logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    """Supported exchange types"""
    POLYMARKET = "polymarket"
    CRYPTO_CEX = "crypto_cex"  # Centralized crypto exchanges
    CRYPTO_DEX = "crypto_dex"  # Decentralized exchanges


@dataclass
class MarketData:
    """Standardized market data structure"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    bid_volume: Optional[float] = None
    ask_volume: Optional[float] = None
    exchange: str = ""
    raw_data: Optional[Dict] = None


class PolymarketConnector:
    """
    Polymarket API Connector
    Connects to Polymarket prediction markets
    """
    
    BASE_URL = "https://clob.polymarket.com"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('POLYMARKET_API_KEY')
        if not self.api_key:
            logger.warning("Polymarket API key not found, some features may be limited")
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.markets_cache: Dict[str, Any] = {}
        self.cache_ttl = 60  # seconds
        self.last_cache_update: Optional[datetime] = None
    
    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def fetch_markets(self) -> List[Dict]:
        """
        Fetch available markets from Polymarket
        
        Returns:
            List of market dictionaries
        """
        await self._ensure_session()
        
        # Check cache
        if self._is_cache_valid():
            logger.debug("Returning cached Polymarket markets")
            return list(self.markets_cache.values())
        
        try:
            url = f"{self.BASE_URL}/markets"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Update cache
                    self.markets_cache = {m['id']: m for m in data}
                    self.last_cache_update = datetime.now()
                    
                    logger.info(f"Fetched {len(data)} markets from Polymarket")
                    return data
                else:
                    logger.error(f"Polymarket API error: {response.status}")
                    return []
        
        except asyncio.TimeoutError:
            logger.error("Polymarket API timeout")
            return []
        except Exception as e:
            logger.error(f"Error fetching Polymarket markets: {e}")
            return []
    
    async def fetch_market_data(self, market_id: str) -> Optional[MarketData]:
        """
        Fetch data for specific market
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            MarketData object or None
        """
        await self._ensure_session()
        
        try:
            url = f"{self.BASE_URL}/markets/{market_id}"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Convert to standardized format
                    return MarketData(
                        symbol=data.get('question', market_id),
                        timestamp=datetime.now(),
                        open=float(data.get('last_price', 0)),
                        high=float(data.get('high_24h', 0)),
                        low=float(data.get('low_24h', 0)),
                        close=float(data.get('last_price', 0)),
                        volume=float(data.get('volume_24h', 0)),
                        bid=float(data.get('best_bid', 0)) if data.get('best_bid') else None,
                        ask=float(data.get('best_ask', 0)) if data.get('best_ask') else None,
                        exchange="polymarket",
                        raw_data=data
                    )
                else:
                    logger.error(f"Market {market_id} fetch error: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.markets_cache or not self.last_cache_update:
            return False
        
        elapsed = (datetime.now() - self.last_cache_update).total_seconds()
        return elapsed < self.cache_ttl
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()


class CryptoExchangeConnector:
    """
    CCXT-based connector for cryptocurrency exchanges
    Supports Binance, Coinbase, Kraken, etc.
    """
    
    def __init__(self, exchange_id: str = 'binance', testnet: bool = True):
        """
        Args:
            exchange_id: CCXT exchange identifier (binance, coinbase, kraken, etc.)
            testnet: Use testnet/sandbox mode if available
        """
        self.exchange_id = exchange_id
        self.testnet = testnet
        self.exchange = None
        
        self._init_exchange()
    
    def _init_exchange(self):
        """Initialize CCXT exchange"""
        try:
            exchange_class = getattr(ccxt, self.exchange_id)
            
            config = {
                'enableRateLimit': True,
                'timeout': 10000,
            }
            
            # Add API keys if available
            api_key = os.getenv(f'{self.exchange_id.upper()}_API_KEY')
            api_secret = os.getenv(f'{self.exchange_id.upper()}_API_SECRET')
            
            if api_key and api_secret:
                config['apiKey'] = api_key
                config['secret'] = api_secret
                logger.info(f"Using authenticated mode for {self.exchange_id}")
            else:
                logger.warning(f"No API keys for {self.exchange_id}, read-only mode")
            
            # Enable testnet if available
            if self.testnet:
                config['sandbox'] = True
                logger.info(f"Using testnet mode for {self.exchange_id}")
            
            self.exchange = exchange_class(config)
            logger.info(f"Initialized {self.exchange_id} connector")
        
        except AttributeError:
            logger.error(f"Exchange '{self.exchange_id}' not supported by CCXT")
            raise
        except Exception as e:
            logger.error(f"Error initializing {self.exchange_id}: {e}")
            raise
    
    async def fetch_ticker(self, symbol: str) -> Optional[MarketData]:
        """
        Fetch ticker data for symbol
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            
        Returns:
            MarketData object or None
        """
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            
            return MarketData(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(ticker['timestamp'] / 1000),
                open=float(ticker.get('open', 0)),
                high=float(ticker.get('high', 0)),
                low=float(ticker.get('low', 0)),
                close=float(ticker.get('last', 0)),
                volume=float(ticker.get('baseVolume', 0)),
                bid=float(ticker.get('bid', 0)) if ticker.get('bid') else None,
                ask=float(ticker.get('ask', 0)) if ticker.get('ask') else None,
                bid_volume=float(ticker.get('bidVolume', 0)) if ticker.get('bidVolume') else None,
                ask_volume=float(ticker.get('askVolume', 0)) if ticker.get('askVolume') else None,
                exchange=self.exchange_id,
                raw_data=ticker
            )
        
        except Exception as e:
            logger.error(f"Error fetching {symbol} from {self.exchange_id}: {e}")
            return None
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str = '1m', limit: int = 100) -> List[MarketData]:
        """
        Fetch OHLCV candles
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe (1m, 5m, 15m, 1h, 1d)
            limit: Number of candles
            
        Returns:
            List of MarketData objects
        """
        try:
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            result = []
            for candle in ohlcv:
                timestamp, open_price, high, low, close, volume = candle
                
                result.append(MarketData(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(timestamp / 1000),
                    open=float(open_price),
                    high=float(high),
                    low=float(low),
                    close=float(close),
                    volume=float(volume),
                    exchange=self.exchange_id
                ))
            
            return result
        
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return []
    
    async def close(self):
        """Close exchange connection"""
        if self.exchange:
            await self.exchange.close()


class ExchangeConnector:
    """
    Unified Exchange Connector with fallback support
    Main interface for fetching market data from multiple sources
    """
    
    def __init__(self, config):
        """
        Args:
            config: ConfigManager instance
        """
        self.config = config
        
        # Initialize connectors
        self.polymarket = None
        self.crypto_exchanges: Dict[str, CryptoExchangeConnector] = {}
        self.primary_exchange = config.markets.get('primary', 'polymarket')
        
        self._init_connectors()
    
    def _init_connectors(self):
        """Initialize all configured connectors"""
        
        # Polymarket
        if self.primary_exchange == 'polymarket':
            try:
                self.polymarket = PolymarketConnector()
                logger.info("✓ Polymarket connector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Polymarket: {e}")
        
        # Crypto exchanges (for diversification)
        crypto_exchanges = self.config.get('markets.crypto_exchanges', ['binance'])
        testnet = self.config.get('markets.testnet', True)
        
        for exchange_id in crypto_exchanges:
            try:
                connector = CryptoExchangeConnector(exchange_id, testnet=testnet)
                self.crypto_exchanges[exchange_id] = connector
                logger.info(f"✓ {exchange_id} connector initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize {exchange_id}: {e}")
    
    async def fetch_market_data(self) -> Dict[str, MarketData]:
        """
        Fetch current market data from all sources
        
        Returns:
            Dictionary mapping symbols to MarketData objects
        """
        all_data = {}
        
        # Fetch from Polymarket
        if self.polymarket:
            try:
                markets = await self.polymarket.fetch_markets()
                
                # Fetch data for top markets (limit to avoid rate limits)
                for market in markets[:10]:  # Top 10 markets
                    market_id = market.get('id')
                    if market_id:
                        data = await self.polymarket.fetch_market_data(market_id)
                        if data:
                            all_data[f"PM_{market_id}"] = data
                
                logger.info(f"Fetched {len(all_data)} Polymarket markets")
            
            except Exception as e:
                logger.error(f"Error fetching Polymarket data: {e}")
        
        # Fetch from crypto exchanges
        symbols = self.config.get('markets.crypto_symbols', ['BTC/USDT', 'ETH/USDT'])
        
        for exchange_id, connector in self.crypto_exchanges.items():
            for symbol in symbols:
                try:
                    data = await connector.fetch_ticker(symbol)
                    if data:
                        key = f"{exchange_id}_{symbol.replace('/', '_')}"
                        all_data[key] = data
                
                except Exception as e:
                    logger.error(f"Error fetching {symbol} from {exchange_id}: {e}")
        
        if all_data:
            logger.info(f"✓ Fetched {len(all_data)} total market data points")
        else:
            logger.warning("⚠️ No market data fetched from any source")
        
        return all_data
    
    async def close(self):
        """Close all connections"""
        if self.polymarket:
            await self.polymarket.close()
        
        for connector in self.crypto_exchanges.values():
            await connector.close()
        
        logger.info("All exchange connections closed")
