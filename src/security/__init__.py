"""Security Module - Phase 1 Complete

Provides comprehensive security features for BotV2:
- CSRF Protection (token-based validation)
- XSS Prevention (HTML sanitization)
- Session Management (secure cookies + timeouts)
- Security Headers (CSP, HSTS, X-Frame-Options, etc.)
- Input Validation (Pydantic models)
- Audit Logging (structured JSON logs)
- Request Validation (size, content-type)

Phase 1 Status: 90% Complete (integration pending)
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
    
    # Configuration
    ConfigUpdateRequest,
    
    # Market Data
    MarketSymbolRequest,
    OHLCVRequest,
    
    # Strategies
    StrategyCreateRequest,
    
    # Trades
    TradeExecutionRequest,
    
    # Helpers
    validate_request_data,
    get_validation_errors
)

# Audit Logging
from .audit_logger import (
    SecurityAuditLogger,
    get_audit_logger,
    init_audit_logger
)

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
    
    # Configuration Models
    'ConfigUpdateRequest',
    
    # Market Data Models
    'MarketSymbolRequest',
    'OHLCVRequest',
    
    # Strategy Models
    'StrategyCreateRequest',
    
    # Trade Models
    'TradeExecutionRequest',
    
    # Validation Helpers
    'validate_request_data',
    'get_validation_errors',
    
    # ==================== Audit Logging ====================
    'SecurityAuditLogger',
    'get_audit_logger',
    'init_audit_logger',
]

# Add optional exports if available
if HAS_SECRETS_MANAGER:
    __all__.append('SecretsManager')

if HAS_SSL_CONFIG:
    __all__.append('SSLConfig')


__version__ = '1.1.0'
__phase__ = 'Phase 1 - 90% Complete'
