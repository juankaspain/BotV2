"""Input Validation Module

Provides Pydantic models for strict input validation across all API endpoints.
Prevents injection attacks, malformed data, and validates business logic.
"""

import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator, EmailStr
from enum import Enum


class TradingMode(str, Enum):
    """Valid trading modes"""
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"


class OrderType(str, Enum):
    """Valid order types"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, Enum):
    """Valid order sides"""
    BUY = "buy"
    SELL = "sell"


class TimeInForce(str, Enum):
    """Valid time in force values"""
    GTC = "gtc"  # Good till cancel
    IOC = "ioc"  # Immediate or cancel
    FOK = "fok"  # Fill or kill
    DAY = "day"  # Day order


class LoginRequest(BaseModel):
    """Login request validation"""
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('username')
    def validate_username(cls, v):
        """Username: alphanumeric + underscore/hyphen only"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscore, and hyphen')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        """Password: enforce minimum security"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class AnnotationCreate(BaseModel):
    """Annotation creation validation"""
    chart_id: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., min_length=1, max_length=20)
    x: float
    y: float
    text: str = Field(..., min_length=1, max_length=500)
    color: Optional[str] = Field(default='#ffffff', regex=r'^#[0-9a-fA-F]{6}$')
    
    @validator('chart_id')
    def validate_chart_id(cls, v):
        """Chart ID: alphanumeric + underscore only"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid chart_id format')
        return v.strip()
    
    @validator('type')
    def validate_type(cls, v):
        """Type: limited set of values"""
        allowed_types = ['line', 'arrow', 'text', 'box', 'circle']
        if v.lower() not in allowed_types:
            raise ValueError(f'Type must be one of: {allowed_types}')
        return v.lower()
    
    @validator('text')
    def validate_text(cls, v):
        """Text: sanitize and limit length"""
        # Remove control characters
        v = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', v)
        return v.strip()


class OrderCreate(BaseModel):
    """Order creation validation"""
    symbol: str = Field(..., min_length=2, max_length=20)
    side: OrderSide
    type: OrderType
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    stop_price: Optional[float] = Field(default=None, gt=0)
    time_in_force: TimeInForce = TimeInForce.GTC
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Symbol: uppercase alphanumeric + slash only"""
        if not re.match(r'^[A-Z0-9/]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper().strip()
    
    @validator('price')
    def validate_price(cls, v, values):
        """Price: required for LIMIT and STOP_LIMIT orders"""
        if values.get('type') in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            if v is None or v <= 0:
                raise ValueError('Price is required for LIMIT/STOP_LIMIT orders')
        return v
    
    @validator('stop_price')
    def validate_stop_price(cls, v, values):
        """Stop price: required for STOP and STOP_LIMIT orders"""
        if values.get('type') in [OrderType.STOP, OrderType.STOP_LIMIT]:
            if v is None or v <= 0:
                raise ValueError('Stop price is required for STOP/STOP_LIMIT orders')
        return v


class StrategyConfig(BaseModel):
    """Strategy configuration validation"""
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    enabled: bool = True
    symbols: List[str] = Field(..., min_items=1, max_items=50)
    timeframe: str = Field(..., regex=r'^(1m|5m|15m|30m|1h|4h|1d)$')
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        """Name: alphanumeric + spaces/underscores"""
        if not re.match(r'^[a-zA-Z0-9_ -]+$', v):
            raise ValueError('Name can only contain letters, numbers, spaces, and underscores')
        return v.strip()
    
    @validator('symbols')
    def validate_symbols(cls, v):
        """Symbols: uppercase and deduplicate"""
        return list(set(s.upper().strip() for s in v))
    
    @validator('parameters')
    def validate_parameters(cls, v):
        """Parameters: limit depth and size"""
        if len(str(v)) > 10000:  # Max 10KB JSON
            raise ValueError('Parameters too large')
        return v


class BacktestConfig(BaseModel):
    """Backtest configuration validation"""
    strategy_id: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(..., gt=0, le=1000000000)
    symbols: List[str] = Field(..., min_items=1, max_items=100)
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """End date must be after start date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v
    
    @validator('symbols')
    def validate_symbols(cls, v):
        """Symbols: uppercase and deduplicate"""
        return list(set(s.upper().strip() for s in v))


class SettingsUpdate(BaseModel):
    """Settings update validation"""
    trading_mode: Optional[TradingMode] = None
    initial_capital: Optional[float] = Field(default=None, gt=0, le=1000000000)
    risk_per_trade: Optional[float] = Field(default=None, gt=0, le=100)
    max_positions: Optional[int] = Field(default=None, gt=0, le=100)
    stop_loss_pct: Optional[float] = Field(default=None, gt=0, le=100)
    take_profit_pct: Optional[float] = Field(default=None, gt=0, le=1000)
    
    class Config:
        validate_assignment = True


class MarketDataRequest(BaseModel):
    """Market data request validation"""
    symbol: str = Field(..., min_length=2, max_length=20)
    timeframe: str = Field(default='1h', regex=r'^(1m|5m|15m|30m|1h|4h|1d|1w)$')
    limit: int = Field(default=100, ge=1, le=1000)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Symbol: uppercase alphanumeric + slash only"""
        if not re.match(r'^[A-Z0-9/]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper().strip()


class AlertCreate(BaseModel):
    """Alert creation validation"""
    type: str = Field(..., regex=r'^(price|indicator|condition)$')
    symbol: str = Field(..., min_length=2, max_length=20)
    condition: str = Field(..., min_length=1, max_length=100)
    value: float
    enabled: bool = True
    notify_email: Optional[EmailStr] = None
    notify_telegram: Optional[bool] = False
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Symbol: uppercase alphanumeric + slash only"""
        if not re.match(r'^[A-Z0-9/]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper().strip()
    
    @validator('condition')
    def validate_condition(cls, v):
        """Condition: limited operators"""
        allowed_operators = ['>', '<', '>=', '<=', '==', 'crosses_above', 'crosses_below']
        if not any(op in v for op in allowed_operators):
            raise ValueError(f'Condition must contain one of: {allowed_operators}')
        return v.strip()


class ExportRequest(BaseModel):
    """Export request validation"""
    format: str = Field(..., regex=r'^(csv|json|excel)$')
    data_type: str = Field(..., regex=r'^(trades|positions|portfolio|performance)$')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """End date must be after start date"""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


def validate_input(model: BaseModel, data: Dict[str, Any]) -> BaseModel:
    """Validate input data against Pydantic model
    
    Args:
        model: Pydantic model class
        data: Dictionary of data to validate
        
    Returns:
        Validated model instance
        
    Raises:
        ValueError: If validation fails
    """
    try:
        return model(**data)
    except Exception as e:
        raise ValueError(f"Validation error: {str(e)}")


def validate_json_size(data: str, max_size_kb: int = 100) -> bool:
    """Validate JSON payload size
    
    Args:
        data: JSON string
        max_size_kb: Maximum size in kilobytes
        
    Returns:
        True if valid, False otherwise
    """
    size_kb = len(data.encode('utf-8')) / 1024
    return size_kb <= max_size_kb


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and null bytes
    filename = filename.replace('/', '').replace('\\', '').replace('\0', '')
    
    # Remove dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename
