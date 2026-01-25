"""Rate Limiter Configuration Module

Centralized rate limiting configuration and setup.
"""

import logging
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from typing import Optional
import os

logger = logging.getLogger(__name__)


class RateLimiterConfig:
    """Rate Limiter Configuration"""
    
    # Default rate limits
    DEFAULT_LIMIT = "10 per minute"
    API_LIMIT = "30 per minute"
    LOGIN_LIMIT = "5 per minute"
    EXPORT_LIMIT = "5 per minute"
    
    # Exempt paths (no rate limiting)
    EXEMPT_PATHS = [
        '/health',
        '/api/metrics',
        '/static',
        '/favicon.ico'
    ]
    
    def __init__(self, app: Optional[Flask] = None):
        """Initialize rate limiter configuration
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.limiter = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> Limiter:
        """Initialize rate limiter for Flask app
        
        Args:
            app: Flask application instance
        
        Returns:
            Configured Limiter instance
        """
        # Get storage configuration
        storage_uri = self._get_storage_uri()
        
        # Create limiter instance
        self.limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=[self.DEFAULT_LIMIT],
            storage_uri=storage_uri,
            storage_options={"socket_connect_timeout": 30},
            strategy="moving-window",  # More accurate than fixed-window
            headers_enabled=True,
            swallow_errors=True  # Don't break app if Redis is down
        )
        
        # Register error handler
        @app.errorhandler(429)
        def ratelimit_handler(e):
            logger.warning(
                f"Rate limit exceeded: {request.method} {request.path} "
                f"from {request.remote_addr}"
            )
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please slow down.',
                'retry_after': getattr(e, 'retry_after', 60)
            }), 429
        
        # Exempt paths from rate limiting
        for path in self.EXEMPT_PATHS:
            self.limiter.exempt(lambda: request.path.startswith(path))
        
        logger.info(f"✅ Rate Limiter initialized with {storage_uri.split('://')[0]} storage")
        
        return self.limiter
    
    def _get_storage_uri(self) -> str:
        """Get rate limiter storage URI
        
        Tries Redis first, falls back to memory if unavailable.
        
        Returns:
            Storage URI string
        """
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = os.getenv('REDIS_PORT', '6379')
        
        # Try Redis connection
        try:
            import redis
            r = redis.Redis(
                host=redis_host,
                port=int(redis_port),
                socket_connect_timeout=1
            )
            r.ping()
            storage_uri = f"redis://{redis_host}:{redis_port}"
            logger.info(f"Using Redis for rate limiting: {storage_uri}")
            return storage_uri
        except Exception as e:
            logger.warning(
                f"Redis unavailable ({e}), using in-memory storage for rate limiting. "
                "Note: In-memory storage doesn't work across multiple processes."
            )
            return "memory://"
    
    def get_limiter(self) -> Optional[Limiter]:
        """Get the configured limiter instance
        
        Returns:
            Limiter instance or None if not initialized
        """
        return self.limiter


def init_rate_limiter(app: Flask) -> Limiter:
    """Initialize rate limiter for Flask app (convenience function)
    
    Args:
        app: Flask application instance
    
    Returns:
        Configured Limiter instance
    """
    config = RateLimiterConfig(app)
    return config.get_limiter()
