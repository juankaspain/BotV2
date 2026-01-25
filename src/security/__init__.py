"""Security Module

Provides comprehensive security features for BotV2:
- CSRF Protection
- XSS Prevention
- Session Management
- Rate Limiting
- Security Headers
- Input Validation
- Audit Logging
"""

from .csrf_protection import init_csrf_protection, get_csrf_token
from .xss_protection import sanitize_html, sanitize_dict, xss_protection_middleware
from .session_manager import SessionManager
from .security_middleware import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    ResponseTimeMiddleware,
    init_security_middleware
)
from .input_validator import (
    LoginRequest,
    AnnotationCreate,
    OrderCreate,
    StrategyConfig,
    BacktestConfig,
    SettingsUpdate,
    MarketDataRequest,
    AlertCreate,
    ExportRequest,
    validate_input,
    sanitize_filename
)
from .audit_logger import SecurityAuditLogger, get_audit_logger, init_audit_logger
from .rate_limiter import init_rate_limiter, RateLimiterConfig, get_rate_limits

__all__ = [
    # CSRF
    'init_csrf_protection',
    'get_csrf_token',
    
    # XSS
    'sanitize_html',
    'sanitize_dict',
    'xss_protection_middleware',
    
    # Session
    'SessionManager',
    
    # Middleware
    'SecurityHeadersMiddleware',
    'RequestValidationMiddleware',
    'ResponseTimeMiddleware',
    'init_security_middleware',
    
    # Validation
    'LoginRequest',
    'AnnotationCreate',
    'OrderCreate',
    'StrategyConfig',
    'BacktestConfig',
    'SettingsUpdate',
    'MarketDataRequest',
    'AlertCreate',
    'ExportRequest',
    'validate_input',
    'sanitize_filename',
    
    # Audit
    'SecurityAuditLogger',
    'get_audit_logger',
    'init_audit_logger',
    
    # Rate Limiting
    'init_rate_limiter',
    'RateLimiterConfig',
    'get_rate_limits'
]

__version__ = '1.0.0'
