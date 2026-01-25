"""Input Validation Module

Provides Pydantic models for request data validation.
Enforces strict input validation to prevent injection attacks.
"""

import re
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime

logger = logging.getLogger(__name__)


# ==================== AUTHENTICATION MODELS ====================

class LoginRequest(BaseModel):
    """Login request validation
    
    Enforces:
    - Username: 3-20 alphanumeric + underscore/hyphen
    - Password: min 8 chars (dev), min 16 chars (prod)
    """
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                'Username must contain only alphanumeric characters, '
                'underscores, and hyphens'
            )
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        
        # Production: require stronger passwords
        import os
        if os.getenv('FLASK_ENV') == 'production' and len(v) < 16:
            raise ValueError(
                'Production passwords must be at least 16 characters'
            )
        
        return v
    
    class Config:
        str_strip_whitespace = True


class PasswordChangeRequest(BaseModel):
    """Password change request validation"""
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """Validate new password"""
        # Check if same as current password
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        
        # Check strength
        import os
        if os.getenv('FLASK_ENV') == 'production':
            if len(v) < 16:
                raise ValueError('Production passwords must be at least 16 characters')
            
            # Check complexity
            has_upper = any(c.isupper() for c in v)
            has_lower = any(c.islower() for c in v)
            has_digit = any(c.isdigit() for c in v)
            has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)
            
            if not (has_upper and has_lower and has_digit and has_special):
                raise ValueError(
                    'Production passwords must contain uppercase, lowercase, '
                    'digits, and special characters'
                )
        
        return v
    
    @root_validator
    def passwords_match(cls, values):
        """Validate password confirmation"""
        new_pwd = values.get('new_password')
        confirm_pwd = values.get('confirm_password')
        
        if new_pwd != confirm_pwd:
            raise ValueError('Passwords do not match')
        
        return values


# ==================== ANNOTATION MODELS ====================

class AnnotationRequest(BaseModel):
    """Annotation creation/update validation"""
    chart_id: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., min_length=1, max_length=20)
    x: float
    y: float
    text: str = Field(..., min_length=1, max_length=500)
    color: Optional[str] = Field(default='#ffffff', max_length=20)
    
    @validator('chart_id')
    def validate_chart_id(cls, v):
        """Validate chart ID format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Invalid chart_id format')
        return v
    
    @validator('type')
    def validate_annotation_type(cls, v):
        """Validate annotation type"""
        allowed_types = ['note', 'arrow', 'line', 'rect', 'circle']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {allowed_types}')
        return v
    
    @validator('color')
    def validate_color(cls, v):
        """Validate color format"""
        if v and not re.match(r'^#[0-9a-fA-F]{6}$', v):
            raise ValueError('Color must be hex format (#RRGGBB)')
        return v
    
    @validator('text')
    def validate_text(cls, v):
        """Sanitize annotation text"""
        # Strip HTML tags for security
        import re
        clean_text = re.sub(r'<[^>]+>', '', v)
        return clean_text.strip()


# ==================== CONFIGURATION MODELS ====================

class ConfigUpdateRequest(BaseModel):
    """Configuration update validation"""
    key: str = Field(..., min_length=1, max_length=100)
    value: Any
    
    @validator('key')
    def validate_config_key(cls, v):
        """Validate config key format"""
        # Only allow specific config keys
        allowed_keys = [
            'trading_mode',
            'initial_capital',
            'trading_interval',
            'max_positions',
            'risk_per_trade',
            'stop_loss_pct',
            'take_profit_pct',
            'enable_notifications',
            'notification_channels'
        ]
        
        if v not in allowed_keys:
            raise ValueError(f'Invalid config key: {v}')
        
        return v
    
    @root_validator
    def validate_value_for_key(cls, values):
        """Validate value based on key"""
        key = values.get('key')
        value = values.get('value')
        
        if key == 'trading_mode':
            if value not in ['paper', 'live']:
                raise ValueError('trading_mode must be "paper" or "live"')
        
        elif key == 'initial_capital':
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError('initial_capital must be positive number')
        
        elif key == 'trading_interval':
            if not isinstance(value, int) or value < 1:
                raise ValueError('trading_interval must be positive integer')
        
        elif key in ['max_positions', 'risk_per_trade', 'stop_loss_pct', 'take_profit_pct']:
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f'{key} must be positive number')
        
        return values


# ==================== MARKET DATA MODELS ====================

class MarketSymbolRequest(BaseModel):
    """Market symbol validation"""
    symbol: str = Field(..., min_length=2, max_length=20)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate symbol format"""
        # Allow alphanumeric, slash, hyphen (BTC/USD, EUR-USD)
        if not re.match(r'^[A-Z0-9/-]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper()


class OHLCVRequest(BaseModel):
    """OHLCV data request validation"""
    symbol: str = Field(..., min_length=2, max_length=20)
    timeframe: str = Field(..., min_length=2, max_length=5)
    limit: int = Field(default=100, ge=1, le=500)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate symbol format"""
        if not re.match(r'^[A-Z0-9/-]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper()
    
    @validator('timeframe')
    def validate_timeframe(cls, v):
        """Validate timeframe"""
        allowed = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        if v not in allowed:
            raise ValueError(f'Timeframe must be one of: {allowed}')
        return v


# ==================== STRATEGY MODELS ====================

class StrategyCreateRequest(BaseModel):
    """Strategy creation validation"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(default='', max_length=500)
    strategy_type: str = Field(..., min_length=3, max_length=50)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate strategy name"""
        # Remove HTML tags
        import re
        clean_name = re.sub(r'<[^>]+>', '', v)
        return clean_name.strip()
    
    @validator('strategy_type')
    def validate_strategy_type(cls, v):
        """Validate strategy type"""
        allowed_types = [
            'trend_following',
            'mean_reversion',
            'breakout',
            'momentum',
            'arbitrage',
            'market_making'
        ]
        
        if v not in allowed_types:
            raise ValueError(f'Strategy type must be one of: {allowed_types}')
        
        return v


# ==================== TRADE MODELS ====================

class TradeExecutionRequest(BaseModel):
    """Trade execution validation"""
    symbol: str = Field(..., min_length=2, max_length=20)
    side: str = Field(..., min_length=3, max_length=4)
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(default=None, gt=0)
    order_type: str = Field(default='market', min_length=5, max_length=10)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate symbol"""
        if not re.match(r'^[A-Z0-9/-]+$', v.upper()):
            raise ValueError('Invalid symbol format')
        return v.upper()
    
    @validator('side')
    def validate_side(cls, v):
        """Validate trade side"""
        if v.lower() not in ['buy', 'sell']:
            raise ValueError('Side must be "buy" or "sell"')
        return v.lower()
    
    @validator('order_type')
    def validate_order_type(cls, v):
        """Validate order type"""
        allowed_types = ['market', 'limit', 'stop', 'stop_limit']
        if v.lower() not in allowed_types:
            raise ValueError(f'Order type must be one of: {allowed_types}')
        return v.lower()


# ==================== HELPER FUNCTIONS ====================

def validate_request_data(model: BaseModel, data: Dict[str, Any]) -> tuple[bool, Optional[BaseModel], Optional[str]]:
    """Validate request data against Pydantic model
    
    Args:
        model: Pydantic model class
        data: Request data dictionary
        
    Returns:
        Tuple of (is_valid, validated_data, error_message)
    """
    try:
        validated = model(**data)
        return True, validated, None
    except Exception as e:
        logger.warning(f"Validation failed for {model.__name__}: {e}")
        return False, None, str(e)


def get_validation_errors(model: BaseModel, data: Dict[str, Any]) -> List[str]:
    """Get list of validation errors
    
    Args:
        model: Pydantic model class
        data: Request data dictionary
        
    Returns:
        List of error messages
    """
    try:
        model(**data)
        return []
    except Exception as e:
        if hasattr(e, 'errors'):
            return [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return [str(e)]
