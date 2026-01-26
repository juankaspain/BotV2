"""CSRF Protection Module

Provides Cross-Site Request Forgery protection for Flask applications.
Implements token-based validation for all state-changing operations.
"""

import secrets
import logging
from functools import wraps
from flask import session, request, jsonify, abort, Flask
from typing import Optional, Callable
import time

logger = logging.getLogger(__name__)


class CSRFProtection:
    """CSRF Protection Manager
    
    Implements token-based CSRF protection with the following features:
    - Automatic token generation and validation
    - Token rotation on each request
    - Time-based token expiration
    - Double-submit cookie pattern
    - Integration with Flask sessions
    """
    
    def __init__(self, app=None, token_length: int = 32, token_ttl: int = 3600):
        """
        Initialize CSRF protection
        
        Args:
            app: Flask application instance
            token_length: Length of CSRF token in bytes (default: 32)
            token_ttl: Token time-to-live in seconds (default: 3600 = 1 hour)
        """
        self.token_length = token_length
        self.token_ttl = token_ttl
        self.app = app
        self._enabled = True
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize CSRF protection for Flask app"""
        self.app = app
        
        # Check if CSRF is enabled
        self._enabled = app.config.get('CSRF_ENABLED', True)
        
        if not self._enabled:
            logger.warning("⚠️ CSRF Protection DISABLED")
            return
        
        # Register before_request handler
        @app.before_request
        def csrf_protect():
            # Skip if disabled
            if not self._enabled:
                return
            
            # Skip CSRF for safe methods (GET, HEAD, OPTIONS)
            if request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
                return
            
            # Skip CSRF for exempt endpoints
            if hasattr(request, '_csrf_exempt') and request._csrf_exempt:
                return
            
            # Skip CSRF for health/metrics endpoints
            exempt_paths = [
                '/health',
                '/api/metrics',
                '/api/metrics/export',
                '/api/metrics/snapshot'
            ]
            if request.path in exempt_paths:
                return
            
            # Validate CSRF token for state-changing requests
            if not self.validate_csrf():
                logger.warning(
                    f"CSRF validation failed for {request.method} {request.path} "
                    f"from {request.remote_addr}"
                )
                
                # Log to security audit if available
                try:
                    from .audit_logger import get_audit_logger
                    audit_logger = get_audit_logger()
                    audit_logger.log_csrf_failure(
                        reason='invalid_or_missing_token'
                    )
                except Exception:
                    pass
                
                abort(403, description="CSRF validation failed")
        
        # Register context processor to inject CSRF token into templates
        @app.context_processor
        def csrf_token_processor():
            return {'csrf_token': self.generate_token}
        
        # Add after_request handler for token rotation
        @app.after_request
        def rotate_csrf_token(response):
            # Only rotate on successful POST/PUT/DELETE
            if request.method in ('POST', 'PUT', 'DELETE', 'PATCH') and response.status_code < 400:
                # Generate new token for next request
                new_token = self.generate_token()
                # Add token to response cookie (optional double-submit pattern)
                response.set_cookie(
                    'csrf_token',
                    new_token,
                    max_age=self.token_ttl,
                    secure=app.config.get('SESSION_COOKIE_SECURE', True),
                    httponly=False,  # Needs to be readable by JavaScript
                    samesite='Lax'
                )
            return response
        
        logger.info("✅ CSRF Protection enabled")
    
    def generate_token(self) -> str:
        """Generate a new CSRF token and store it in session
        
        Returns:
            The generated CSRF token
        """
        # Generate random token
        token = secrets.token_urlsafe(self.token_length)
        
        # Store token and timestamp in session
        session['csrf_token'] = token
        session['csrf_token_time'] = time.time()
        
        return token
    
    def get_token(self) -> Optional[str]:
        """Get the current CSRF token from session
        
        Returns:
            Current CSRF token or None if not found
        """
        token = session.get('csrf_token')
        
        # Generate new token if not exists
        if not token:
            token = self.generate_token()
        
        return token
    
    def validate_csrf(self) -> bool:
        """Validate CSRF token from request
        
        Checks:
        1. Token exists in session
        2. Token is not expired
        3. Token from request matches session token
        
        Returns:
            True if token is valid, False otherwise
        """
        # Get token from session
        session_token = session.get('csrf_token')
        session_time = session.get('csrf_token_time', 0)
        
        if not session_token:
            logger.debug("CSRF token not found in session")
            return False
        
        # Check token expiration
        if time.time() - session_time > self.token_ttl:
            logger.debug("CSRF token expired")
            session.pop('csrf_token', None)
            session.pop('csrf_token_time', None)
            return False
        
        # Get token from request (header or form data)
        request_token = None
        
        # Check X-CSRF-Token header (preferred for AJAX requests)
        if 'X-CSRF-Token' in request.headers:
            request_token = request.headers.get('X-CSRF-Token')
        # Check X-CSRFToken header (alternative)
        elif 'X-CSRFToken' in request.headers:
            request_token = request.headers.get('X-CSRFToken')
        # Check form data (for regular form submissions)
        elif request.form and 'csrf_token' in request.form:
            request_token = request.form.get('csrf_token')
        # Check JSON payload
        elif request.is_json:
            try:
                json_data = request.get_json(silent=True)
                if json_data and 'csrf_token' in json_data:
                    request_token = json_data.get('csrf_token')
            except Exception:
                pass
        
        if not request_token:
            logger.debug("CSRF token not found in request")
            return False
        
        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(session_token, request_token)
    
    def exempt(self, view_func: Callable) -> Callable:
        """Decorator to exempt a view from CSRF protection
        
        Use with caution - only for public APIs or webhooks
        
        Example:
            @app.route('/webhook', methods=['POST'])
            @csrf.exempt
            def webhook():
                return 'OK'
        """
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            # Set flag to skip CSRF validation
            request._csrf_exempt = True
            return view_func(*args, **kwargs)
        
        return wrapper


def require_csrf(f: Callable) -> Callable:
    """Decorator to explicitly require CSRF validation
    
    Useful for critical endpoints that should never bypass CSRF.
    
    Example:
        @app.route('/transfer', methods=['POST'])
        @require_csrf
        def transfer_funds():
            return jsonify({'status': 'success'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        csrf = CSRFProtection()
        if not csrf.validate_csrf():
            logger.warning(
                f"CSRF validation failed (explicit) for {request.path} "
                f"from {request.remote_addr}"
            )
            return jsonify({
                'error': 'CSRF validation failed',
                'message': 'Invalid or missing CSRF token'
            }), 403
        return f(*args, **kwargs)
    
    return decorated_function


# Global CSRF instance
_csrf_protection: Optional[CSRFProtection] = None


def init_csrf_protection(
    app: Flask,
    token_length: int = 32,
    token_ttl: int = 3600
) -> CSRFProtection:
    """Initialize CSRF protection for Flask app
    
    Args:
        app: Flask application instance
        token_length: Length of CSRF token in bytes (default: 32)
        token_ttl: Token time-to-live in seconds (default: 3600 = 1 hour)
        
    Returns:
        CSRFProtection instance
    """
    global _csrf_protection
    _csrf_protection = CSRFProtection(app, token_length, token_ttl)
    return _csrf_protection


def get_csrf_token() -> Optional[str]:
    """Get current CSRF token from session
    
    Returns:
        CSRF token string or None
    """
    global _csrf_protection
    if _csrf_protection:
        return _csrf_protection.get_token()
    
    # Fallback: try to get from session directly
    return session.get('csrf_token')


# Convenience function for templates (deprecated, use csrf_token() instead)
def generate_csrf_token() -> str:
    """Generate CSRF token for use in templates
    
    Returns:
        CSRF token string
    """
    token = get_csrf_token()
    if not token:
        # Generate new one
        csrf = CSRFProtection()
        token = csrf.generate_token()
    return token
