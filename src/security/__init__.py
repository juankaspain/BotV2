"""Security Module - Phase 1 Implementation

Provides comprehensive security features:
- CSRF Protection
- XSS Prevention
- Security Headers & CSP
- Session Management
- Input Validation
"""

from .csrf_protection import CSRFProtection, require_csrf, generate_csrf_token
from .xss_protection import (
    XSSProtection,
    sanitize_html,
    sanitize_json,
    validate_url,
    escape_js,
    safe_format
)
from .security_middleware import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    ResponseTimeMiddleware,
    init_security_middleware
)
from .session_manager import (
    SessionManager,
    get_session_manager,
    init_session_manager
)

__all__ = [
    # CSRF Protection
    'CSRFProtection',
    'require_csrf',
    'generate_csrf_token',
    
    # XSS Protection
    'XSSProtection',
    'sanitize_html',
    'sanitize_json',
    'validate_url',
    'escape_js',
    'safe_format',
    
    # Security Middleware
    'SecurityHeadersMiddleware',
    'RequestValidationMiddleware',
    'ResponseTimeMiddleware',
    'init_security_middleware',
    
    # Session Management
    'SessionManager',
    'get_session_manager',
    'init_session_manager',
]

__version__ = '1.0.0'
