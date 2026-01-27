# -*- coding: utf-8 -*-
"""
Security Middleware Module
Provides security middleware for Flask applications
"""

from functools import wraps
from flask import request, g, abort


class SecurityMiddleware:
    """Security middleware for Flask"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Add security headers
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'"
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            return response
        
        # Request validation
        @app.before_request
        def validate_request():
            # Check for suspicious patterns
            if self._is_suspicious_request(request):
                abort(403)
    
    @staticmethod
    def _is_suspicious_request(req):
        """Check for suspicious request patterns"""
        # Check for SQL injection patterns
        suspicious_patterns = [
            "UNION SELECT",
            "DROP TABLE",
            "<script>",
            "javascript:",
            "../",
            "..%2f"
        ]
        
        # Check query string
        query_string = req.query_string.decode('utf-8', errors='ignore').upper()
        for pattern in suspicious_patterns:
            if pattern.upper() in query_string:
                return True
        
        return False
    
    @staticmethod
    def require_https(f):
        """Decorator to require HTTPS"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
                abort(403)
            return f(*args, **kwargs)
        return decorated_function


def init_security_middleware(app):
    """Initialize security middleware"""
    return SecurityMiddleware(app)
