"""Rate Limiter Module

Provides modular rate limiting configuration for Flask applications.
Supports Redis backend for distributed rate limiting.
"""

import logging
from typing import Optional
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

logger = logging.getLogger(__name__)


class RateLimiterConfig:
    """Rate limiter configuration"""
    
    # Default limits - AUMENTADOS PARA DESARROLLO
    DEFAULT_LIMIT = "100 per minute"  # Antes: 10 per minute
    API_LIMIT = "200 per minute"      # Antes: 30 per minute
    LOGIN_LIMIT = "20 per minute"     # Antes: 5 per minute  <- CRÍTICO
    EXPORT_LIMIT = "20 per minute"    # Antes: 5 per minute
    HEAVY_LIMIT = "10 per minute"     # Antes: 2 per minute
    
    # Storage
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    @classmethod
    def get_storage_uri(cls) -> str:
        """Get Redis storage URI or fallback to memory
        
        Returns:
            Storage URI string
        """
        try:
            import redis
            
            # Build Redis URI
            if cls.REDIS_PASSWORD:
                uri = f"redis://:{cls.REDIS_PASSWORD}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
            else:
                uri = f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
            
            # Test connection
            r = redis.Redis(
                host=cls.REDIS_HOST,
                port=cls.REDIS_PORT,
                password=cls.REDIS_PASSWORD if cls.REDIS_PASSWORD else None,
                db=cls.REDIS_DB,
                socket_connect_timeout=2
            )
            r.ping()
            
            logger.info(f"✅ Rate limiter using Redis: {cls.REDIS_HOST}:{cls.REDIS_PORT}")
            return uri
            
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable ({e}), using memory storage for rate limiting")
            return "memory://"


def init_rate_limiter(
    app: Flask,
    enabled: bool = True,
    storage_uri: Optional[str] = None,
    default_limits: Optional[list] = None
) -> Optional[Limiter]:
    """Initialize rate limiter for Flask app
    
    Args:
        app: Flask application instance
        enabled: Whether rate limiting is enabled
        storage_uri: Custom storage URI (defaults to auto-detect)
        default_limits: Default rate limits (defaults to 100 per minute)
        
    Returns:
        Limiter instance or None if disabled
    """
    if not enabled:
        logger.warning("⚠️ Rate limiting DISABLED")
        return None
    
    # Get storage URI
    if storage_uri is None:
        storage_uri = RateLimiterConfig.get_storage_uri()
    
    # Default limits
    if default_limits is None:
        default_limits = [RateLimiterConfig.DEFAULT_LIMIT]
    
    # Create limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=default_limits,
        storage_uri=storage_uri,
        storage_options={"socket_connect_timeout": 30},
        strategy="fixed-window",
        headers_enabled=True,
        swallow_errors=True  # Don't crash if Redis is down
    )
    
    # Custom error handler
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors"""
        # Log to security audit if available
        try:
            from .audit_logger import get_audit_logger
            audit_logger = get_audit_logger()
            audit_logger.log_rate_limit_exceeded(
                endpoint=request.endpoint or request.path,
                limit=str(e.description)
            )
        except Exception:
            pass
        
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please slow down.',
            'retry_after': getattr(e, 'retry_after', None)
        }), 429
    
    logger.info(f"✅ Rate limiter initialized (storage: {storage_uri.split('://')[0]})")
    return limiter


def get_rate_limits() -> dict:
    """Get configured rate limits
    
    Returns:
        Dictionary of rate limit configurations
    """
    return {
        'default': RateLimiterConfig.DEFAULT_LIMIT,
        'api': RateLimiterConfig.API_LIMIT,
        'login': RateLimiterConfig.LOGIN_LIMIT,
        'export': RateLimiterConfig.EXPORT_LIMIT,
        'heavy': RateLimiterConfig.HEAVY_LIMIT
    }
