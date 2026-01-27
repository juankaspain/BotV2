"""CSRF Protection Module for BotV2.

Provides token-based CSRF protection for Flask applications.
"""

import secrets
import logging
from functools import wraps
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import Flask, request, session, g, abort

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
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Skip for API endpoints with proper auth
            if request.headers.get('X-API-Key'):
                return
            
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            
            if not self.validate_token(token):
                logger.warning(f"CSRF validation failed for {request.path}")
                abort(403, description='CSRF token validation failed')
    
    def _context_processor(self) -> Dict[str, Any]:
        """Add CSRF token to template context."""
        return {'csrf_token': self.generate_token}
    
    def generate_token(self) -> str:
        """Generate a new CSRF token."""
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(self.token_length)
            session['csrf_token_time'] = datetime.utcnow().isoformat()
        return session['csrf_token']
    
    def validate_token(self, token: Optional[str]) -> bool:
        """Validate a CSRF token."""
        if not token:
            return False
        
        session_token = session.get('csrf_token')
        if not session_token:
            return False
        
        # Check token expiry
        token_time = session.get('csrf_token_time')
        if token_time:
            created = datetime.fromisoformat(token_time)
            if datetime.utcnow() - created > timedelta(seconds=self.token_ttl):
                # Token expired, regenerate
                del session['csrf_token']
                del session['csrf_token_time']
                return False
        
        return secrets.compare_digest(token, session_token)
    
    def get_token(self) -> str:
        """Get current CSRF token."""
        return self.generate_token()


# Global CSRF instance
_csrf: Optional[CSRFProtection] = None


def init_csrf_protection(app: Flask, token_length: int = 32, token_ttl: int = 3600) -> CSRFProtection:
    """Initialize CSRF protection."""
    global _csrf
    _csrf = CSRFProtection(app, token_length, token_ttl)
    return _csrf


def get_csrf_token() -> str:
    """Get current CSRF token."""
    if _csrf:
        return _csrf.get_token()
    # Fallback if not initialized
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']


def init_csrf(app: Flask = None, **kwargs) -> CSRFProtection:
    """Alias for init_csrf_protection."""
    if app:
        return init_csrf_protection(app, **kwargs)
    return CSRFProtection(**kwargs)
