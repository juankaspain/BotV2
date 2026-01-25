"""Input Validation Module

Provides Pydantic-based input validation for all user inputs.
Ensures data integrity and prevents injection attacks.
"""

import logging
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, validator, Field, EmailStr

logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    """Validate login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format (alphanumeric + underscore/dash only)"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only letters, numbers, underscore, and dash')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class AnnotationCreate(BaseModel):
    """Validate annotation creation"""
    chart_id: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., regex=r'^(note|alert|marker)$')
    x: float
    y: float
    text: str = Field(..., min_length=1, max_length=500)
    color: Optional[str] = Field(default='#ffffff', regex=r'^#[0-9A-Fa-f]{6}$')
    
    @validator('chart_id')
    def validate_chart_id(cls, v):
        """Validate chart ID format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid chart ID format')
        return v.strip()
    
    @validator('text')
    def validate_text(cls, v):
        """Validate annotation text (no HTML/scripts)"""
        # Check for dangerous patterns
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError('Annotation text contains dangerous content')
        return v.strip()


class StrategyCreate(BaseModel):
    """Validate strategy creation"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default='', max_length=500)
    type: str = Field(..., regex=r'^(momentum|mean_reversion|arbitrage|ml_based)$')
    parameters: Dict[str, Any] = Field(default_factory=dict)
    active: bool = Field(default=True)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate strategy name"""
        if not re.match(r'^[a-zA-Z0-9_\s-]+$', v):
            raise ValueError('Strategy name contains invalid characters')
        return v.strip()
    
    @validator('parameters')
    def validate_parameters(cls, v):
        """Validate strategy parameters"""
        if not isinstance(v, dict):
            raise ValueError('Parameters must be a dictionary')
        
        # Limit depth to prevent DoS
        if len(str(v)) > 10000:
            raise ValueError('Parameters too large')
        
        return v


class StrategyUpdate(BaseModel):
    """Validate strategy update"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    parameters: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_\s-]+$', v):
            raise ValueError('Strategy name contains invalid characters')
        return v.strip() if v else v


class TradeCreate(BaseModel):
    """Validate trade creation"""
    symbol: str = Field(..., min_length=1, max_length=20)
    side: str = Field(..., regex=r'^(buy|sell)$')
    quantity: float = Field(..., gt=0, le=1000000)
    price: Optional[float] = Field(None, gt=0)
    order_type: str = Field(..., regex=r'^(market|limit|stop|stop_limit)$')
    strategy_id: Optional[int] = None
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate trading symbol format"""
        # Allow letters, numbers, slash, dash
        if not re.match(r'^[A-Z0-9/-]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper().strip()
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive and reasonable"""
        if v <= 0:
            raise ValueError('Quantity must be positive')
        if v > 1000000:
            raise ValueError('Quantity too large')
        return v


class MarketDataRequest(BaseModel):
    """Validate market data request"""
    symbol: str = Field(..., min_length=1, max_length=20)
    timeframe: str = Field(..., regex=r'^(1m|5m|15m|30m|1h|4h|1d)$')
    limit: int = Field(default=100, ge=1, le=1000)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not re.match(r'^[A-Z0-9/-]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper().strip()


class AlertCreate(BaseModel):
    """Validate alert creation"""
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    severity: str = Field(..., regex=r'^(info|warning|error|critical)$')
    category: str = Field(..., regex=r'^(trade|system|risk|strategy)$')
    
    @validator('title', 'message')
    def validate_text_fields(cls, v):
        """Validate text fields for XSS"""
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onload=']
        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError('Text contains dangerous content')
        return v.strip()


class ConfigUpdate(BaseModel):
    """Validate configuration update"""
    key: str = Field(..., min_length=1, max_length=100)
    value: Any
    
    @validator('key')
    def validate_key(cls, v):
        """Validate config key format"""
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Invalid config key format')
        return v.strip()
    
    @validator('value')
    def validate_value(cls, v):
        """Validate config value size"""
        # Prevent DoS through large values
        if isinstance(v, str) and len(v) > 10000:
            raise ValueError('Config value too large')
        if isinstance(v, (list, dict)) and len(str(v)) > 50000:
            raise ValueError('Config value too large')
        return v


class ExportRequest(BaseModel):
    """Validate export request"""
    format: str = Field(..., regex=r'^(json|csv|xlsx)$')
    data_type: str = Field(..., regex=r'^(trades|portfolio|strategies|metrics)$')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Validate date range is logical"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('End date must be after start date')
        return v


def validate_input(model_class: type[BaseModel], data: Dict[str, Any]) -> BaseModel:
    """Validate input data against a Pydantic model
    
    Args:
        model_class: Pydantic model class to validate against
        data: Input data dictionary
    
    Returns:
        Validated model instance
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        return model_class(**data)
    except Exception as e:
        logger.warning(f"Validation failed for {model_class.__name__}: {e}")
        raise


def safe_dict(model: BaseModel) -> Dict[str, Any]:
    """Convert Pydantic model to safe dictionary
    
    Args:
        model: Pydantic model instance
    
    Returns:
        Dictionary with validated data
    """
    return model.dict()
