"""Input Validation Module with Pydantic

Provides schema validation for all API endpoints using Pydantic models.
Ensures type safety and input sanitization.

Usage:
    from src.security.input_validator import validate_input, LoginRequest
    
    try:
        validated = validate_input(LoginRequest, request.form)
        username = validated.username
    except ValidationError as e:
        return {'error': str(e)}, 400
"""

import re
from typing import Optional, Dict, Any, List, Type, TypeVar
from pydantic import BaseModel, field_validator, ValidationError
from datetime import datetime
import os

T = TypeVar('T', bound=BaseModel)


# ==================== LOGIN VALIDATION ====================

class LoginRequest(BaseModel):
    """Login request validation schema"""
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format"""
        if not v or len(v.strip()) == 0:
            raise ValueError('Username is required')
        
        v = v.strip()
        
        # Length check
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        if len(v) > 20:
            raise ValueError('Username must be at most 20 characters')
        
        # Format check (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscore, and hyphen')
        
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password (basic check, hash comparison done separately)"""
        if not v or len(v) == 0:
            raise ValueError('Password is required')
        
        # Length check only (no complexity check to avoid leaking requirements)
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('Password is too long')
        
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request validation"""
    old_password: str
    new_password: str
    confirm_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters')
        if len(v) > 128:
            raise ValueError('New password is too long')
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def validate_confirm(cls, v: str, info) -> str:
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


def validate_login_request(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate login request data
    
    Args:
        data: Request form data
    
    Returns:
        Validated data dictionary
    
    Raises:
        ValueError: If validation fails
    """
    try:
        validated = LoginRequest(
            username=data.get('username', ''),
            password=data.get('password', '')
        )
        return validated.model_dump()
    except ValidationError as e:
        errors = [err['msg'] for err in e.errors()]
        raise ValueError(', '.join(errors))


# ==================== ANNOTATION VALIDATION ====================

class AnnotationRequest(BaseModel):
    """Annotation creation validation schema"""
    chart_id: str
    type: str
    x: float
    y: float
    text: str
    color: Optional[str] = '#ffffff'
    
    @field_validator('chart_id')
    @classmethod
    def validate_chart_id(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Chart ID is required')
        
        v = v.strip()
        
        # Alphanumeric and underscore only
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid chart ID format')
        
        if len(v) > 50:
            raise ValueError('Chart ID too long')
        
        return v
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed_types = ['trend', 'support', 'resistance', 'note', 'alert']
        
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {allowed_types}')
        
        return v
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Text is required')
        
        v = v.strip()
        
        if len(v) > 500:
            raise ValueError('Text too long (max 500 characters)')
        
        # Check for dangerous patterns (basic XSS prevention)
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onload=',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Text contains potentially dangerous content')
        
        return v
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        # Hex color validation
        if not re.match(r'^#[0-9a-fA-F]{6}$', v):
            raise ValueError('Color must be in hex format (#RRGGBB)')
        
        return v


# Alias for compatibility with web_app.py
AnnotationCreate = AnnotationRequest


def validate_annotation_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate annotation request data
    
    Args:
        data: Request JSON data
    
    Returns:
        Validated data dictionary
    
    Raises:
        ValueError: If validation fails
    """
    try:
        validated = AnnotationRequest(**data)
        return validated.model_dump()
    except ValidationError as e:
        errors = [err['msg'] for err in e.errors()]
        raise ValueError(', '.join(errors))


# ==================== CONFIGURATION VALIDATION ====================

class ConfigUpdateRequest(BaseModel):
    """Configuration update validation"""
    section: str
    key: str
    value: Any
    
    @field_validator('section')
    @classmethod
    def validate_section(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid section format')
        return v
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError('Invalid key format')
        return v


# ==================== MARKET DATA VALIDATION ====================

class MarketDataRequest(BaseModel):
    """Market data request validation schema"""
    symbol: str
    timeframe: Optional[str] = '1h'
    limit: Optional[int] = 100
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Symbol is required')
        
        v = v.strip().upper()
        
        # Alphanumeric, slash, hyphen only
        if not re.match(r'^[A-Z0-9/-]+$', v):
            raise ValueError('Invalid symbol format')
        
        if len(v) > 20:
            raise ValueError('Symbol too long')
        
        return v
    
    @field_validator('timeframe')
    @classmethod
    def validate_timeframe(cls, v: str) -> str:
        allowed_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        
        if v not in allowed_timeframes:
            raise ValueError(f'Timeframe must be one of: {allowed_timeframes}')
        
        return v
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Limit must be at least 1')
        if v > 500:
            raise ValueError('Limit must be at most 500')
        
        return v


# Aliases for different naming conventions
MarketSymbolRequest = MarketDataRequest
OHLCVRequest = MarketDataRequest


def validate_market_data_request(symbol: str, timeframe: str = '1h', limit: int = 100) -> Dict[str, Any]:
    """Validate market data request
    
    Args:
        symbol: Trading symbol
        timeframe: Candle timeframe
        limit: Number of candles
    
    Returns:
        Validated data dictionary
    
    Raises:
        ValueError: If validation fails
    """
    try:
        validated = MarketDataRequest(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        return validated.model_dump()
    except ValidationError as e:
        errors = [err['msg'] for err in e.errors()]
        raise ValueError(', '.join(errors))


# ==================== STRATEGY VALIDATION ====================

class StrategyCreateRequest(BaseModel):
    """Strategy creation validation"""
    name: str
    type: str
    parameters: Dict[str, Any]
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError('Strategy name must be at least 3 characters')
        if len(v) > 50:
            raise ValueError('Strategy name too long')
        if not re.match(r'^[a-zA-Z0-9_ -]+$', v):
            raise ValueError('Invalid strategy name format')
        return v.strip()
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed_types = ['trend_following', 'mean_reversion', 'momentum', 'arbitrage', 'custom']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {allowed_types}')
        return v


# ==================== TRADE VALIDATION ====================

class TradeExecutionRequest(BaseModel):
    """Trade execution validation"""
    symbol: str
    side: str
    type: str
    quantity: float
    price: Optional[float] = None
    
    @field_validator('side')
    @classmethod
    def validate_side(cls, v: str) -> str:
        if v not in ['buy', 'sell']:
            raise ValueError('Side must be buy or sell')
        return v
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ['market', 'limit', 'stop', 'stop_limit']:
            raise ValueError('Invalid order type')
        return v
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


# ==================== GENERIC VALIDATORS ====================

def validate_pagination(page: int = 1, per_page: int = 20) -> Dict[str, int]:
    """Validate pagination parameters
    
    Args:
        page: Page number (1-indexed)
        per_page: Items per page
    
    Returns:
        Validated pagination dict
    
    Raises:
        ValueError: If validation fails
    """
    if page < 1:
        raise ValueError('Page must be at least 1')
    if page > 1000:
        raise ValueError('Page number too high')
    
    if per_page < 1:
        raise ValueError('Per page must be at least 1')
    if per_page > 100:
        raise ValueError('Per page must be at most 100')
    
    return {'page': page, 'per_page': per_page}


def validate_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Optional[datetime]]:
    """Validate date range parameters
    
    Args:
        start_date: ISO format date string
        end_date: ISO format date string
    
    Returns:
        Validated date range dict
    
    Raises:
        ValueError: If validation fails
    """
    result = {'start_date': None, 'end_date': None}
    
    if start_date:
        try:
            result['start_date'] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid start_date format (use ISO 8601)')
    
    if end_date:
        try:
            result['end_date'] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid end_date format (use ISO 8601)')
    
    if result['start_date'] and result['end_date']:
        if result['start_date'] > result['end_date']:
            raise ValueError('start_date must be before end_date')
    
    return result


def validate_input(model_class: Type[T], data: Dict[str, Any]) -> T:
    """Generic input validation using Pydantic models
    
    Args:
        model_class: Pydantic model class to use for validation
        data: Data dictionary to validate
    
    Returns:
        Validated model instance
    
    Raises:
        ValidationError: If validation fails
    """
    return model_class(**data)


def validate_request_data(model_class: Type[T], data: Dict[str, Any]) -> T:
    """Alias for validate_input for compatibility"""
    return validate_input(model_class, data)


def get_validation_errors(e: ValidationError) -> List[str]:
    """Extract error messages from ValidationError
    
    Args:
        e: Pydantic ValidationError
    
    Returns:
        List of error message strings
    """
    return [err['msg'] for err in e.errors()]


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize filename to prevent directory traversal and other attacks
    
    Args:
        filename: Original filename
        max_length: Maximum allowed filename length
    
    Returns:
        Sanitized filename
    
    Raises:
        ValueError: If filename is invalid or too long
    """
    if not filename or len(filename.strip()) == 0:
        raise ValueError('Filename cannot be empty')
    
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    # Allow: alphanumeric, underscore, hyphen, dot
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    
    # Prevent hidden files
    if sanitized.startswith('.'):
        sanitized = '_' + sanitized[1:]
    
    # Prevent double extensions that might bypass filters
    sanitized = sanitized.replace('..', '.')
    
    # Check length
    if len(sanitized) > max_length:
        # Keep extension, truncate name
        name, ext = os.path.splitext(sanitized)
        max_name_length = max_length - len(ext)
        sanitized = name[:max_name_length] + ext
    
    # Ensure it's not empty after sanitization
    if not sanitized or sanitized == '.':
        raise ValueError('Filename invalid after sanitization')
    
    return sanitized
