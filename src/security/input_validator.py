"""Input Validation Module with Pydantic

Provides schema validation for all API endpoints using Pydantic models.
Ensures type safety and input sanitization.

Usage:
    from src.security.input_validator import validate_login_request
    
    try:
        validated = validate_login_request(request.form)
        username = validated['username']
    except ValueError as e:
        return {'error': str(e)}, 400
"""

import re
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, field_validator, ValidationError
from datetime import datetime


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
