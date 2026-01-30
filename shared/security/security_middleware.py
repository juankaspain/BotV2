# -*- coding: utf-8 -*-
"""
Security Middleware Module
Provides security middleware for Flask applications

FIX: Now respects FLASK_ENV to disable CSP/HSTS in development mode
"""

import os
import logging
from functools import wraps
from flask import request, g, abort

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for Flask
    
    IMPORTANT: In development mode (FLASK_ENV=development), restrictive
    security headers like CSP and HSTS are DISABLED to allow:
    - External CDN resources (Google Fonts, Chart.js, Bootstrap, etc.)
    - HTTP connections without forcing HTTPS
    - Inline scripts and styles for development convenience
    
    In production mode (FLASK_ENV=production), all security headers
    are enabled for maximum protection.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.is_development = os.getenv('FLASK_ENV', 'development').lower() == 'development'
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Re-check environment when initializing
        self.is_development = os.getenv('FLASK_ENV', 'development').lower() == 'development'
        
        # Log the mode
        if self.is_development:
            logger.info("[SecurityMiddleware] Development mode - CSP/HSTS DISABLED")
        else:
            logger.info("[SecurityMiddleware] Production mode - Full security headers ENABLED")
        
        # Add security headers
        @app.after_request
        def add_security_headers(response):
            # Always add these basic security headers (safe for development)
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Check environment for restrictive headers
            is_dev = os.getenv('FLASK_ENV', 'development').lower() == 'development'
            
            if not is_dev:
                # PRODUCTION ONLY: Add restrictive security headers
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
                
                # Full CSP for production
                csp_policy = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                    "cdn.jsdelivr.net cdn.socket.io cdn.plot.ly unpkg.com cdn.sheetjs.com cdnjs.cloudflare.com; "
                    "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.jsdelivr.net cdnjs.cloudflare.com; "
                    "font-src 'self' fonts.gstatic.com fonts.googleapis.com cdnjs.cloudflare.com data:; "
                    "img-src 'self' data: https: blob:; "
                    "connect-src 'self' wss: ws: localhost:*; "
                    "frame-ancestors 'none'"
                )
                response.headers['Content-Security-Policy'] = csp_policy
            else:
                # DEVELOPMENT: NO restrictive headers
                # Remove CSP header if it was set by another middleware
                if 'Content-Security-Policy' in response.headers:
                    del response.headers['Content-Security-Policy']
                
                # Remove HSTS in development
                if 'Strict-Transport-Security' in response.headers:
                    del response.headers['Strict-Transport-Security']
            
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
            # Skip HTTPS check in development
            is_dev = os.getenv('FLASK_ENV', 'development').lower() == 'development'
            if is_dev:
                return f(*args, **kwargs)
            
            if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
                abort(403)
            return f(*args, **kwargs)
        return decorated_function


def init_security_middleware(app):
    """Initialize security middleware"""
    return SecurityMiddleware(app)
