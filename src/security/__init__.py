"""Security Module - Phase 1 Complete

Provides comprehensive security features for BotV2:
- CSRF Protection (token-based validation)
- XSS Prevention (HTML sanitization)
- Session Management (secure cookies + timeouts)
- Security Headers (CSP, HSTS, X-Frame-Options, etc.)
- Input Validation (Pydantic models)
- Audit Logging (structured JSON logs)
- Request Validation (size, content-type)

Phase 1 Status: 100% Complete
"""

# CSRF Protection
from .csrf_protection import (
    CSRFProtection,
    init_csrf_protection,
    get_csrf_token,
    require_csrf
)

# XSS Prevention
from .xss_protection import (
    sanitize_html,
    sanitize_dict,
    contains_xss,
    detect_xss_attempt,
    sanitize_request_data,
    xss_protection_middleware,
    escape_html,
    strip_tags
)

# Session Management
from .session_manager import SessionManager

# Security Middleware
from .security_middleware import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    ResponseTimeMiddleware,
    init_security_middleware
)

# Input Validation (Pydantic Models)
from .input_validator import (
    # Authentication
    LoginRequest,
    PasswordChangeRequest,
    
    # Annotations
    AnnotationRequest,
    AnnotationCreate,  # Alias for compatibility
    
    # Configuration
    ConfigUpdateRequest,
    
    # Market Data
    MarketDataRequest,
    MarketSymbolRequest,  # Alias
    OHLCVRequest,  # Alias
    
    # Strategies
    StrategyCreateRequest,
    
    # Trades
    TradeExecutionRequest,
    
    # Validation Helpers
    validate_input,
    validate_request_data,
    get_validation_errors,
    sanitize_filename,
    
    # Legacy functions (backwards compatibility)
    validate_login_request,
    validate_annotation_request,
    validate_market_data_request,
    validate_pagination,
    validate_date_range
)

# Audit Logging
from .audit_logger import (
    SecurityAuditLogger,
    get_audit_logger,
    init_audit_logger
)

# Rate Limiting (if available)
try:
    from .rate_limiter import (
        RateLimiterConfig,
        init_rate_limiter
    )
    HAS_RATE_LIMITER = True
except ImportError:
    HAS_RATE_LIMITER = False

# Secrets Management (existing)
try:
    from .secrets_manager import SecretsManager
    HAS_SECRETS_MANAGER = True
except ImportError:
    HAS_SECRETS_MANAGER = False

# SSL Configuration (existing)
try:
    from .ssl_config import SSLConfig
    HAS_SSL_CONFIG = True
except ImportError:
    HAS_SSL_CONFIG = False


__all__ = [
    # ==================== CSRF Protection ====================
    'CSRFProtection',
    'init_csrf_protection',
    'get_csrf_token',
    'require_csrf',
    
    # ==================== XSS Prevention ====================
    'sanitize_html',
    'sanitize_dict',
    'contains_xss',
    'detect_xss_attempt',
    'sanitize_request_data',
    'xss_protection_middleware',
    'escape_html',
    'strip_tags',
    
    # ==================== Session Management ====================
    'SessionManager',
    
    # ==================== Security Middleware ====================
    'SecurityHeadersMiddleware',
    'RequestValidationMiddleware',
    'ResponseTimeMiddleware',
    'init_security_middleware',
    
    # ==================== Input Validation ====================
    # Authentication Models
    'LoginRequest',
    'PasswordChangeRequest',
    
    # Annotation Models
    'AnnotationRequest',
    'AnnotationCreate',
    
    # Configuration Models
    'ConfigUpdateRequest',
    
    # Market Data Models
    'MarketDataRequest',
    'MarketSymbolRequest',
    'OHLCVRequest',
    
    # Strategy Models
    'StrategyCreateRequest',
    
    # Trade Models
    'TradeExecutionRequest',
    
    # Validation Helpers
    'validate_input',
    'validate_request_data',
    'get_validation_errors',
    'sanitize_filename',
    
    # Legacy validation functions
    'validate_login_request',
    'validate_annotation_request',
    'validate_market_data_request',
    'validate_pagination',
    'validate_date_range',
    
    # ==================== Audit Logging ====================
    'SecurityAuditLogger',
    'get_audit_logger',
    'init_audit_logger',
]

# Add optional exports if available
if HAS_RATE_LIMITER:
    __all__.extend(['RateLimiterConfig', 'init_rate_limiter'])

if HAS_SECRETS_MANAGER:
    __all__.append('SecretsManager')

if HAS_SSL_CONFIG:
    __all__.append('SSLConfig')


__version__ = '1.1.0'
__phase__ = 'Phase 1 - 100% Complete'
