"""Data models module for BotV2.

Provides data model definitions for:
- Trading entities (orders, positions, trades)
- Market data (tickers, orderbooks, candles)
- User and account models
- Configuration models
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PositionSide(Enum):
    """Position side enumeration"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Trade:
    """Represents a completed trade"""
    id: str
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    timestamp: datetime
    order_id: Optional[str] = None
    fee: float = 0.0
    fee_currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def value(self) -> float:
        """Total value of the trade"""
        return self.price * self.quantity
    
    @property
    def net_value(self) -> float:
        """Net value after fees"""
        return self.value - self.fee
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value if isinstance(self.side, OrderSide) else self.side,
            'price': self.price,
            'quantity': self.quantity,
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'order_id': self.order_id,
            'fee': self.fee,
            'fee_currency': self.fee_currency,
            'value': self.value,
            'metadata': self.metadata
        }


@dataclass
class Position:
    """Represents an open position"""
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float = 0.0
    opened_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def value(self) -> float:
        """Current position value"""
        return self.current_price * self.quantity
    
    @property
    def entry_value(self) -> float:
        """Entry position value"""
        return self.entry_price * self.quantity
    
    @property
    def unrealized_pnl(self) -> float:
        """Unrealized profit/loss"""
        if self.side == PositionSide.LONG:
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """Unrealized P&L as percentage"""
        if self.entry_value == 0:
            return 0.0
        return (self.unrealized_pnl / self.entry_value) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'symbol': self.symbol,
            'side': self.side.value if isinstance(self.side, PositionSide) else self.side,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'value': self.value,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'metadata': self.metadata
        }


@dataclass
class Order:
    """Represents an order"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_price: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_open(self) -> bool:
        """Check if order is still open"""
        return self.status in (OrderStatus.PENDING, OrderStatus.OPEN, OrderStatus.PARTIALLY_FILLED)
    
    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled"""
        return self.status == OrderStatus.FILLED
    
    @property
    def remaining_quantity(self) -> float:
        """Remaining quantity to fill"""
        return self.quantity - self.filled_quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value if isinstance(self.side, OrderSide) else self.side,
            'order_type': self.order_type.value if isinstance(self.order_type, OrderType) else self.order_type,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'status': self.status.value if isinstance(self.status, OrderStatus) else self.status,
            'filled_quantity': self.filled_quantity,
            'average_price': self.average_price,
            'remaining_quantity': self.remaining_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'metadata': self.metadata
        }


@dataclass
class MarketData:
    """Represents market data snapshot"""
    symbol: str
    timestamp: datetime
    bid: float
    ask: float
    last: float
    volume_24h: float = 0.0
    high_24h: float = 0.0
    low_24h: float = 0.0
    change_24h: float = 0.0
    change_24h_percent: float = 0.0
    
    @property
    def mid(self) -> float:
        """Mid price"""
        return (self.bid + self.ask) / 2
    
    @property
    def spread(self) -> float:
        """Bid-ask spread"""
        return self.ask - self.bid
    
    @property
    def spread_percent(self) -> float:
        """Spread as percentage of mid"""
        if self.mid == 0:
            return 0.0
        return (self.spread / self.mid) * 100


__all__ = [
    # Enums
    'OrderSide',
    'OrderType', 
    'OrderStatus',
    'PositionSide',
    # Models
    'Trade',
    'Position',
    'Order',
    'MarketData',
]
