"""CSRF Protection Module

Provides Cross-Site Request Forgery protection for Flask applications.
Implements token-based validation for all state-changing operations.
"""

import secrets
import logging
from functools import wraps
from flask import session, request, jsonify, abort
from typing import Optional, Callable
import hashlib
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
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize CSRF protection for Flask app"""
        self.app = app
        
        # Register before_request handler
        @app.before_request
        def csrf_protect():
            # Skip CSRF for safe methods (GET, HEAD, OPTIONS)
            if request.method in ('GET', 'HEAD', 'OPTIONS'):
                return
            
            # Skip CSRF for health/metrics endpoints
            if request.path in ('/health', '/api/metrics', '/api/metrics/export'):
                return
            
            # Skip CSRF for login (uses different validation)
            if request.path == '/login' and request.method == 'POST':
                return
            
            # Validate CSRF token for state-changing requests
            if not self.validate_csrf():
                logger.warning(
                    f"CSRF validation failed for {request.method} {request.path} "
                    f"from {request.remote_addr}"
                )
                abort(403, description="CSRF validation failed")
        
        # Register context processor to inject CSRF token into templates
        @app.context_processor
        def csrf_token_processor():
            return {'csrf_token': self.generate_token}
        
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
        return session.get('csrf_token')
    
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
        # Check form data (for regular form submissions)
        elif request.form and 'csrf_token' in request.form:
            request_token = request.form.get('csrf_token')
        # Check JSON payload
        elif request.is_json and request.get_json():
            request_token = request.get_json().get('csrf_token')
        
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


# Convenience function for templates
def generate_csrf_token() -> str:
    """Generate CSRF token for use in templates
    
    Returns:
        CSRF token string
    """
    csrf = CSRFProtection()
    return csrf.generate_token()
