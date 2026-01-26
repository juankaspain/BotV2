"""XSS Protection Middleware

Automatically sanitizes all incoming request data to prevent XSS attacks.
Applies to JSON, form data, and query parameters.

Usage:
    from src.security.xss_middleware import XSSProtectionMiddleware
    
    middleware = XSSProtectionMiddleware(app)
"""

import logging
from flask import request, Flask
from typing import Dict, Any, List, Union
from .xss_protection import sanitize_html, sanitize_dict

logger = logging.getLogger(__name__)


class XSSProtectionMiddleware:
    """Middleware for automatic XSS protection
    
    Sanitizes all incoming request data before it reaches route handlers.
    """
    
    def __init__(self, app: Flask = None, excluded_paths: List[str] = None):
        """Initialize XSS protection middleware
        
        Args:
            app: Flask application instance
            excluded_paths: List of paths to exclude from sanitization
        """
        self.excluded_paths = excluded_paths or ['/health', '/metrics']
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize middleware for Flask app
        
        Args:
            app: Flask application instance
        """
        @app.before_request
        def sanitize_request_data():
            """Sanitize all incoming request data"""
            
            # Skip excluded paths
            if any(request.path.startswith(path) for path in self.excluded_paths):
                return
            
            # Skip GET requests (read-only)
            if request.method == 'GET':
                return
            
            # Sanitize JSON data
            if request.is_json:
                try:
                    original_json = request.get_json()
                    if original_json:
                        sanitized_json = sanitize_dict(original_json)
                        
                        # Store sanitized data for access in routes
                        request._sanitized_json = sanitized_json
                        
                        logger.debug(f"Sanitized JSON data for {request.path}")
                except Exception as e:
                    logger.error(f"XSS sanitization failed for JSON: {e}")
            
            # Sanitize form data
            elif request.form:
                try:
                    sanitized_form = {}
                    for key, value in request.form.items():
                        if isinstance(value, str):
                            sanitized_form[key] = sanitize_html(value)
                        else:
                            sanitized_form[key] = value
                    
                    # Store sanitized data for access in routes
                    request._sanitized_form = sanitized_form
                    
                    logger.debug(f"Sanitized form data for {request.path}")
                except Exception as e:
                    logger.error(f"XSS sanitization failed for form: {e}")
            
            # Sanitize query parameters
            if request.args:
                try:
                    sanitized_args = {}
                    for key, value in request.args.items():
                        if isinstance(value, str):
                            sanitized_args[key] = sanitize_html(value)
                        else:
                            sanitized_args[key] = value
                    
                    # Store sanitized data for access in routes
                    request._sanitized_args = sanitized_args
                    
                    logger.debug(f"Sanitized query params for {request.path}")
                except Exception as e:
                    logger.error(f"XSS sanitization failed for args: {e}")
        
        logger.info("✅ XSS Protection Middleware enabled")


def get_sanitized_json() -> Dict[str, Any]:
    """Get sanitized JSON from current request
    
    Returns:
        Sanitized JSON data or original if sanitization failed
    """
    if hasattr(request, '_sanitized_json'):
        return request._sanitized_json
    return request.get_json() or {}


def get_sanitized_form() -> Dict[str, Any]:
    """Get sanitized form data from current request
    
    Returns:
        Sanitized form data or original if sanitization failed
    """
    if hasattr(request, '_sanitized_form'):
        return request._sanitized_form
    return dict(request.form)


def get_sanitized_args() -> Dict[str, Any]:
    """Get sanitized query parameters from current request
    
    Returns:
        Sanitized query params or original if sanitization failed
    """
    if hasattr(request, '_sanitized_args'):
        return request._sanitized_args
    return dict(request.args)
