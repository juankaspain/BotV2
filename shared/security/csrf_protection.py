"""CSRF Protection Module for BotV2.

Provides token-based CSRF protection for Flask applications.
"""
import secrets
import logging
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import Flask, request, session, g

logger = logging.getLogger(__name__)


class CSRFProtection:
    """CSRF Protection implementation with token management."""
    
    def __init__(self, app: Optional[Flask] = None, token_length: int = 32, token_ttl: int = 3600):
        self.token_length = token_length
        self.token_ttl = token_ttl
        self._tokens: Dict[str, datetime] = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize CSRF protection for Flask app."""
        app.before_request(self._before_request)
        app.context_processor(self._context_processor)
        logger.info("CSRF Protection initialized")
    
    def _before_request(self):
        """Validate CSRF token on state-changing requests."""
        if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not self.validate_token(token):
                from flask import abort
                abort(403, 'CSRF token invalid or missing')
    
    def _context_processor(self):
        """Add csrf_token to template context."""
        return {'csrf_token': self.generate_token}
    
    def generate_token(self) -> str:
        """Generate a new CSRF token."""
        token = secrets.token_urlsafe(self.token_length)
        self._tokens[token] = datetime.now()
        self._cleanup_expired_tokens()
        return token
    
    def validate_token(self, token: Optional[str]) -> bool:
        """Validate a CSRF token."""
        if not token:
            return False
        
        if token not in self._tokens:
            return False
        
        created_at = self._tokens[token]
        if datetime.now() - created_at > timedelta(seconds=self.token_ttl):
            del self._tokens[token]
            return False
        
        return True
    
    def _cleanup_expired_tokens(self):
        """Remove expired tokens."""
        now = datetime.now()
        expired = [
            t for t, created in self._tokens.items()
            if now - created > timedelta(seconds=self.token_ttl)
        ]
        for token in expired:
            del self._tokens[token]


def init_csrf_protection(app: Flask, token_length: int = 32, token_ttl: int = 3600) -> CSRFProtection:
    """Initialize CSRF protection for the application."""
    csrf = CSRFProtection(app, token_length, token_ttl)
    return csrf


def get_csrf_token() -> str:
    """Get current CSRF token from request context."""
    if hasattr(g, 'csrf_token'):
        return g.csrf_token
    return secrets.token_urlsafe(32)
