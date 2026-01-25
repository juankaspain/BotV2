"""Rate Limiter Module

Provides rate limiting functionality for Flask applications.
Prevents brute force attacks and API abuse.
"""

import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request, jsonify
import os

logger = logging.getLogger(__name__)


class RateLimiterConfig:
    """Rate limiter configuration"""
    
    # Default rate limits
    DEFAULT_LIMIT = "10 per minute"
    API_LIMIT = "30 per minute"
    LOGIN_LIMIT = "5 per minute"
    EXPORT_LIMIT = "5 per minute"
    
    # Storage configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    # Strategy: fixed-window, moving-window
    STRATEGY = "moving-window"
    
    # Headers
    HEADERS_ENABLED = True
    
    @classmethod
    def get_storage_uri(cls) -> str:
        """Get Redis storage URI or fallback to memory"""
        try:
            import redis
            r = redis.Redis(
                host=cls.REDIS_HOST,
                port=cls.REDIS_PORT,
                password=cls.REDIS_PASSWORD,
                socket_connect_timeout=1
            )
            r.ping()
            
            if cls.REDIS_PASSWORD:
                storage_uri = f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}"
            else:
                storage_uri = f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}"
            
            logger.info(f"✅ Rate limiter using Redis: {cls.REDIS_HOST}:{cls.REDIS_PORT}")
            return storage_uri
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable ({e}), using memory storage for rate limiting")
            return "memory://"


def init_rate_limiter(app):
    """Initialize rate limiter for Flask application
    
    Args:
        app: Flask application instance
    
    Returns:
        Limiter instance
    """
    config = RateLimiterConfig()
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[config.DEFAULT_LIMIT],
        storage_uri=config.get_storage_uri(),
        storage_options={"socket_connect_timeout": 30},
        strategy=config.STRATEGY,
        headers_enabled=config.HEADERS_ENABLED,
        swallow_errors=True  # Don't break app if Redis fails
    )
    
    # Custom error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors"""
        from .audit_logger import log_security_event
        
        log_security_event(
            event_type='rate_limit.exceeded',
            level='WARNING',
            ip=request.remote_addr,
            path=request.path,
            method=request.method,
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            limit=str(e.description)
        )
        
        return jsonify({
            'success': False,
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please slow down.',
            'retry_after': getattr(e, 'retry_after', None)
        }), 429
    
    logger.info("✅ Rate limiter initialized")
    return limiter


# Predefined rate limit decorators for common use cases
class RateLimits:
    """Predefined rate limits for common endpoints"""
    
    STRICT = "5 per minute"      # For login, password reset
    NORMAL = "10 per minute"     # For general pages
    API = "30 per minute"        # For API endpoints
    EXPORT = "5 per minute"      # For export/download
    HEALTH = None                # No limit for health checks
