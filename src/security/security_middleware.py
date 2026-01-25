"""Security Middleware Module

Provides security headers, CSP policies, and request/response filtering.
"""

import logging
from flask import request, make_response
from typing import Optional, Dict, List
import time

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """Security Headers Middleware
    
    Automatically adds security headers to all responses:
    - Content-Security-Policy (CSP)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(self, app=None, config: Optional[Dict] = None):
        """
        Initialize security headers middleware
        
        Args:
            app: Flask application instance
            config: Security configuration dictionary
        """
        self.config = config or {}
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware for Flask app"""
        self.app = app
        
        @app.after_request
        def add_security_headers(response):
            """Add security headers to response"""
            
            # Content-Security-Policy
            if not response.headers.get('Content-Security-Policy'):
                response.headers['Content-Security-Policy'] = self._get_csp_header()
            
            # Prevent MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Prevent clickjacking
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            
            # XSS Protection (legacy browsers)
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy (formerly Feature-Policy)
            response.headers['Permissions-Policy'] = (
                'geolocation=(), microphone=(), camera=()'
            )
            
            # Strict-Transport-Security (HSTS) - only in production with HTTPS
            if app.config.get('FORCE_HTTPS', False):
                response.headers['Strict-Transport-Security'] = (
                    'max-age=31536000; includeSubDomains; preload'
                )
            
            # Cache control for sensitive pages
            if request.path.startswith('/api/'):
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            
            return response
        
        logger.info("✅ Security Headers Middleware enabled")
    
    def _get_csp_header(self) -> str:
        """Generate Content-Security-Policy header
        
        Returns:
            CSP header string
        """
        # Default CSP policy (production-grade)
        csp_directives = {
            'default-src': ["'self'"],
            'script-src': [
                "'self'",
                "https://cdn.socket.io",
                "https://cdn.plot.ly",
                "https://cdn.jsdelivr.net"  # For DOMPurify
            ],
            'style-src': [
                "'self'",
                "'unsafe-inline'",  # Required for Plotly and inline styles
                "https://fonts.googleapis.com"
            ],
            'img-src': [
                "'self'",
                "data:",
                "https:"
            ],
            'font-src': [
                "'self'",
                "https://fonts.gstatic.com"
            ],
            'connect-src': [
                "'self'",
                "ws://localhost:*",
                "wss://localhost:*",
                "ws://127.0.0.1:*",
                "wss://127.0.0.1:*"
            ],
            'frame-ancestors': ["'none'"],
            'base-uri': ["'self'"],
            'form-action': ["'self'"]
        }
        
        # Allow custom CSP from config
        if 'csp' in self.config:
            csp_directives.update(self.config['csp'])
        
        # Build CSP header string
        csp_parts = []
        for directive, sources in csp_directives.items():
            sources_str = ' '.join(sources)
            csp_parts.append(f"{directive} {sources_str}")
        
        return '; '.join(csp_parts)


class RequestValidationMiddleware:
    """Request Validation Middleware
    
    Validates incoming requests for:
    - Maximum content length
    - Content-Type validation
    - Request size limits
    - Suspicious patterns
    """
    
    def __init__(self, app=None, max_content_length: int = 16 * 1024 * 1024):
        """
        Initialize request validation middleware
        
        Args:
            app: Flask application instance
            max_content_length: Maximum request body size in bytes (default: 16MB)
        """
        self.max_content_length = max_content_length
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware for Flask app"""
        self.app = app
        app.config['MAX_CONTENT_LENGTH'] = self.max_content_length
        
        @app.before_request
        def validate_request():
            """Validate incoming request"""
            
            # Validate Content-Length
            content_length = request.content_length
            if content_length and content_length > self.max_content_length:
                logger.warning(
                    f"Request too large: {content_length} bytes from {request.remote_addr}"
                )
                return {'error': 'Request too large'}, 413
            
            # Validate Content-Type for POST/PUT requests
            if request.method in ('POST', 'PUT', 'PATCH'):
                content_type = request.content_type
                allowed_types = [
                    'application/json',
                    'application/x-www-form-urlencoded',
                    'multipart/form-data'
                ]
                
                if content_type and not any(
                    content_type.startswith(t) for t in allowed_types
                ):
                    logger.warning(
                        f"Invalid Content-Type: {content_type} from {request.remote_addr}"
                    )
                    return {'error': 'Invalid Content-Type'}, 415
        
        logger.info(f"✅ Request Validation Middleware enabled (max {self.max_content_length // 1024 // 1024}MB)")


class ResponseTimeMiddleware:
    """Response Time Middleware
    
    Adds X-Response-Time header to track request processing time.
    Useful for performance monitoring.
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware for Flask app"""
        self.app = app
        
        @app.before_request
        def start_timer():
            request._start_time = time.time()
        
        @app.after_request
        def add_response_time(response):
            if hasattr(request, '_start_time'):
                elapsed = time.time() - request._start_time
                response.headers['X-Response-Time'] = f"{elapsed * 1000:.2f}ms"
            return response
        
        logger.info("✅ Response Time Middleware enabled")


def init_security_middleware(app, config: Optional[Dict] = None):
    """Initialize all security middleware
    
    Args:
        app: Flask application instance
        config: Security configuration dictionary
    """
    SecurityHeadersMiddleware(app, config)
    RequestValidationMiddleware(app)
    ResponseTimeMiddleware(app)
    
    logger.info("✅ All security middleware initialized")
