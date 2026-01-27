"""Security module for BotV2.

Provides security-related functionality including:
- CSRF protection
- XSS protection
- Input validation
- Rate limiting
- Session management
- SSL/TLS configuration
- Secrets management
- Audit logging
- Security middleware
- Pydantic validation models
"""

# CSRF Protection
from shared.security.csrf_protection import (
    CSRFProtection,
    init_csrf,
    init_csrf_protection,
    get_csrf_token
)

# XSS Protection
from shared.security.xss_protection import (
    sanitize_html,
    sanitize_input,
    sanitize_dict,
    sanitize_filename,
    strip_tags,
    xss_protect,
    xss_protection_middleware,
    validate_content_type
)

# Input Validation
from shared.security.input_validator import InputValidator, validate_input as validator_validate_input

# Pydantic Validation Models
from shared.security.validation_models import (
    LoginRequest,
    AnnotationCreate,
    validate_input
)

# Rate Limiting
from shared.security.rate_limiter import RateLimiter, init_rate_limiter, rate_limit

# Session Management
from shared.security.session_manager import SessionManager, init_session, login_required

# SSL/TLS Configuration
from shared.security.ssl_config import SSLConfig, init_ssl, get_ssl_context

# Secrets Management
from shared.security.secrets_manager import SecretsManager, get_secrets_manager, get_secret

# Audit Logging
from shared.security.audit_logger import (
    SecurityAuditLogger,
    init_audit_logger,
    get_audit_logger,
    audit_log
)

# Security Middleware
from shared.security.security_middleware import SecurityMiddleware, init_security_middleware

__all__ = [
    # CSRF
    'CSRFProtection',
    'init_csrf',
    'init_csrf_protection',
    'get_csrf_token',
    # XSS
    'sanitize_html',
    'sanitize_input',
    'sanitize_dict',
    'sanitize_filename',
    'strip_tags',
    'xss_protect',
    'xss_protection_middleware',
    'validate_content_type',
    # Input Validation
    'InputValidator',
    'validator_validate_input',
    # Pydantic Models
    'LoginRequest',
    'AnnotationCreate',
    'validate_input',
    # Rate Limiting
    'RateLimiter',
    'init_rate_limiter',
    'rate_limit',
    # Session
    'SessionManager',
    'init_session',
    'login_required',
    # SSL
    'SSLConfig',
    'init_ssl',
    'get_ssl_context',
    # Secrets
    'SecretsManager',
    'get_secrets_manager',
    'get_secret',
    # Audit
    'SecurityAuditLogger',
    'init_audit_logger',
    'get_audit_logger',
    'audit_log',
    # Middleware
    'SecurityMiddleware',
    'init_security_middleware',
]
