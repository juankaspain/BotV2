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
"""

from shared.security.csrf_protection import CSRFProtection, init_csrf
from shared.security.xss_protection import XSSProtection, init_xss
from shared.security.input_validator import InputValidator, validate_input
from shared.security.rate_limiter import RateLimiter, init_rate_limiter
from shared.security.session_manager import SessionManager, init_session
from shared.security.ssl_config import SSLConfig, init_ssl
from shared.security.secrets_manager import SecretsManager
from shared.security.audit_logger import SecurityAuditLogger
from shared.security.security_middleware import SecurityMiddleware

__all__ = [
    'CSRFProtection',
    'init_csrf',
    'XSSProtection',
    'init_xss',
    'InputValidator',
    'validate_input',
    'RateLimiter',
    'init_rate_limiter',
    'SessionManager',
    'init_session',
    'SSLConfig',
    'init_ssl',
    'SecretsManager',
    'SecurityAuditLogger',
    'SecurityMiddleware',
]
