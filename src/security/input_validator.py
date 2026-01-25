"""Input Validation Module

Provides comprehensive input validation using Pydantic models.
Ensures type safety and prevents injection attacks through strict validation.
"""

import logging
import re
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, validator, Field, constr, conint, confloat
from enum import Enum

logger = logging.getLogger(__name__)


# ==================== ENUMS ====================

class OrderType(str, Enum):
    """Order type enumeration"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, Enum):
    """Order side enumeration"""
    BUY = "buy"
    SELL = "sell"


class TimeframeType(str, Enum):
    """Timeframe enumeration"""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class AnnotationType(str, Enum):
    """Annotation type enumeration"""
    NOTE = "note"
    BUY_SIGNAL = "buy_signal"
    SELL_SIGNAL = "sell_signal"
    SUPPORT = "support"
    RESISTANCE = "resistance"
    ALERT = "alert"


# ==================== BASE VALIDATORS ====================

def validate_symbol(symbol: str) -> str:
    """Validate trading symbol format"""
    if not re.match(r'^[A-Z]{2,10}(/[A-Z]{2,10})?$', symbol):
        raise ValueError('Invalid symbol format. Use: AAPL or BTC/USD')
    return symbol.upper()


def validate_username(username: str) -> str:
    """Validate username format"""
    if not re.match(r'^[a-zA-Z0-9_-]{3,20}$', username):
        raise ValueError(
            'Username must be 3-20 characters, alphanumeric with _ or - only'
        )
    return username


def validate_password(password: str, min_length: int = 8) -> str:
    """Validate password strength"""
    if len(password) < min_length:
        raise ValueError(f'Password must be at least {min_length} characters')
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '12345678', 'admin', 'admin123', 'qwerty',
        'password123', 'letmein', 'welcome', 'monkey'
    ]
    if password.lower() in weak_passwords:
        raise ValueError('Password is too common. Choose a stronger password.')
    
    return password


def validate_color(color: str) -> str:
    """Validate hex color format"""
    if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
        raise ValueError('Color must be in hex format: #RRGGBB')
    return color.upper()


# ==================== REQUEST MODELS ====================

class LoginRequest(BaseModel):
    """Login request validation"""
    username: constr(min_length=3, max_length=20)
    password: constr(min_length=8, max_length=128)
    
    @validator('username')
    def validate_username_format(cls, v):
        return validate_username(v)
    
    @validator('password')
    def validate_password_strength(cls, v):
        return validate_password(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "SecurePass123!"
            }
        }


class AnnotationRequest(BaseModel):
    """Annotation creation request"""
    chart_id: constr(min_length=1, max_length=50)
    type: AnnotationType
    x: Union[str, float, int]  # Timestamp or numeric value
    y: confloat(ge=-1e10, le=1e10)  # Numeric value with reasonable bounds
    text: constr(min_length=1, max_length=500)
    color: Optional[str] = "#FFFFFF"
    
    @validator('color')
    def validate_color_format(cls, v):
        if v:
            return validate_color(v)
        return "#FFFFFF"
    
    @validator('text')
    def sanitize_text(cls, v):
        # Remove potential XSS attempts
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f'Text contains dangerous pattern: {pattern}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "equity_chart",
                "type": "note",
                "x": "2026-01-25T12:00:00Z",
                "y": 10500.50,
                "text": "Important market event",
                "color": "#FF5733"
            }
        }


class OrderRequest(BaseModel):
    """Trading order request"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: confloat(gt=0, le=1e9)
    price: Optional[confloat(gt=0, le=1e9)] = None
    stop_price: Optional[confloat(gt=0, le=1e9)] = None
    
    @validator('symbol')
    def validate_symbol_format(cls, v):
        return validate_symbol(v)
    
    @validator('price')
    def validate_price_required(cls, v, values):
        if values.get('order_type') in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
            if v is None:
                raise ValueError('Price is required for limit orders')
        return v
    
    @validator('stop_price')
    def validate_stop_price_required(cls, v, values):
        if values.get('order_type') in [OrderType.STOP, OrderType.STOP_LIMIT]:
            if v is None:
                raise ValueError('Stop price is required for stop orders')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "BTC/USD",
                "side": "buy",
                "order_type": "limit",
                "quantity": 0.5,
                "price": 43500.00
            }
        }


class StrategyConfigRequest(BaseModel):
    """Strategy configuration request"""
    name: constr(min_length=1, max_length=100)
    description: Optional[constr(max_length=500)] = None
    enabled: bool = True
    parameters: Optional[Dict[str, Any]] = None
    
    @validator('name')
    def validate_name_safe(cls, v):
        # Allow alphanumeric, spaces, underscores, hyphens
        if not re.match(r'^[a-zA-Z0-9 _-]+$', v):
            raise ValueError(
                'Strategy name can only contain letters, numbers, spaces, _ and -'
            )
        return v
    
    @validator('parameters')
    def validate_parameters(cls, v):
        if v:
            # Limit parameter keys to safe characters
            for key in v.keys():
                if not re.match(r'^[a-zA-Z0-9_]+$', key):
                    raise ValueError(f'Invalid parameter key: {key}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Mean Reversion Strategy",
                "description": "Trades based on price reversion to mean",
                "enabled": true,
                "parameters": {
                    "lookback_period": 20,
                    "threshold": 2.0
                }
            }
        }


class MarketDataRequest(BaseModel):
    """Market data request"""
    symbol: str
    timeframe: TimeframeType = TimeframeType.H1
    limit: conint(ge=1, le=1000) = 100
    
    @validator('symbol')
    def validate_symbol_format(cls, v):
        return validate_symbol(v)
    
    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "ETH/USD",
                "timeframe": "1h",
                "limit": 100
            }
        }


class SettingsUpdateRequest(BaseModel):
    """Settings update request"""
    trading_enabled: Optional[bool] = None
    max_position_size: Optional[confloat(gt=0, le=1e9)] = None
    risk_per_trade: Optional[confloat(ge=0, le=100)] = None  # Percentage
    notification_enabled: Optional[bool] = None
    email: Optional[str] = None
    
    @validator('email')
    def validate_email_format(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('risk_per_trade')
    def validate_risk_range(cls, v):
        if v is not None and v > 10:
            raise ValueError('Risk per trade should not exceed 10%')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "trading_enabled": true,
                "max_position_size": 5000.00,
                "risk_per_trade": 2.0,
                "notification_enabled": true,
                "email": "user@example.com"
            }
        }


class ExportRequest(BaseModel):
    """Export data request"""
    format: str = Field(..., pattern='^(json|csv)$')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "csv",
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-01-31T23:59:59Z"
            }
        }


# ==================== RESPONSE MODELS ====================

class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": true,
                "message": "Operation completed successfully",
                "data": {"id": 123}
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": false,
                "error": "Validation failed",
                "details": {"field": "username", "message": "Username too short"}
            }
        }


# ==================== VALIDATION HELPERS ====================

def validate_request(model: type[BaseModel], data: Dict[str, Any]) -> BaseModel:
    """Validate request data against Pydantic model
    
    Args:
        model: Pydantic model class
        data: Request data dictionary
    
    Returns:
        Validated model instance
    
    Raises:
        ValueError: If validation fails
    """
    try:
        return model(**data)
    except Exception as e:
        logger.warning(f"Validation failed for {model.__name__}: {e}")
        raise ValueError(f"Validation error: {e}")


def sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize request data by removing dangerous patterns
    
    Args:
        data: Request data dictionary
    
    Returns:
        Sanitized data dictionary
    """
    from .xss_protection import sanitize_json
    return sanitize_json(data)
