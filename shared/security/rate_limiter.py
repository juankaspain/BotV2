# -*- coding: utf-8 -*-
"""
Rate Limiter Module
Provides rate limiting functionality
"""

import time
from functools import wraps
from flask import request, jsonify
from collections import defaultdict
import threading


class RateLimiter:
    """Rate limiter class using token bucket algorithm"""
    
    def __init__(self, requests_per_minute=60, burst_size=10):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.tokens = defaultdict(lambda: burst_size)
        self.last_update = defaultdict(time.time)
        self.lock = threading.Lock()
    
    def _get_key(self, request):
        """Get rate limit key from request"""
        return request.remote_addr or 'unknown'
    
    def _update_tokens(self, key):
        """Update token count for key"""
        now = time.time()
        time_passed = now - self.last_update[key]
        self.last_update[key] = now
        
        # Add tokens based on time passed
        tokens_to_add = time_passed * (self.requests_per_minute / 60.0)
        self.tokens[key] = min(self.burst_size, self.tokens[key] + tokens_to_add)
    
    def is_allowed(self, request):
        """Check if request is allowed"""
        key = self._get_key(request)
        
        with self.lock:
            self._update_tokens(key)
            
            if self.tokens[key] >= 1:
                self.tokens[key] -= 1
                return True
            return False
    
    def get_wait_time(self, request):
        """Get time to wait until next request is allowed"""
        key = self._get_key(request)
        
        with self.lock:
            if self.tokens[key] >= 1:
                return 0
            return (1 - self.tokens[key]) * (60.0 / self.requests_per_minute)


# Global rate limiter instance
_rate_limiter = None


def init_rate_limiter(app=None, requests_per_minute=60, burst_size=10):
    """Initialize rate limiter"""
    global _rate_limiter
    _rate_limiter = RateLimiter(requests_per_minute, burst_size)
    return _rate_limiter


def rate_limit(requests_per_minute=60, burst_size=10):
    """Decorator for rate limiting"""
    limiter = RateLimiter(requests_per_minute, burst_size)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not limiter.is_allowed(request):
                wait_time = limiter.get_wait_time(request)
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': wait_time
                }), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator
