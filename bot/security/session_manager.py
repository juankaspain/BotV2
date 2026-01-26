"""Session Management Module

Provides secure session management with:
- Session timeouts
- Session rotation
- Activity tracking
- Secure cookie configuration
"""

import logging
from datetime import datetime, timedelta
from flask import session, request
from typing import Optional, Dict, Any
import secrets

logger = logging.getLogger(__name__)


class SessionManager:
    """Secure Session Manager
    
    Manages user sessions with:
    - Automatic session expiration
    - Session rotation on privilege changes
    - Activity tracking
    - Secure cookie settings
    """
    
    def __init__(self, app=None, config: Optional[Dict] = None):
        """
        Initialize session manager
        
        Args:
            app: Flask application instance
            config: Session configuration
        """
        self.config = config or {}
        self.session_timeout = timedelta(
            minutes=self.config.get('session_timeout_minutes', 30)
        )
        self.max_session_lifetime = timedelta(
            hours=self.config.get('max_session_hours', 12)
        )
        self.activity_timeout = timedelta(
            minutes=self.config.get('activity_timeout_minutes', 15)
        )
        
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize session manager for Flask app"""
        self.app = app
        
        # Configure secure session cookies
        app.config['SESSION_COOKIE_SECURE'] = self.config.get(
            'secure_cookies', app.config.get('ENV') == 'production'
        )
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = self.session_timeout
        
        # Generate strong secret key if not set
        if not app.config.get('SECRET_KEY'):
            app.config['SECRET_KEY'] = secrets.token_urlsafe(32)
            logger.warning("SECRET_KEY not set - generated temporary key")
        
        @app.before_request
        def check_session():
            """Check and update session on each request"""
            if 'user' in session:
                # Check session expiration
                if not self._is_session_valid():
                    logger.info(f"Session expired for user {session.get('user')}")
                    self.clear_session()
                    return {'error': 'Session expired', 'redirect': '/login'}, 401
                
                # Update activity timestamp
                self._update_activity()
                
                # Rotate session ID periodically for security
                if self._should_rotate_session():
                    self._rotate_session()
        
        logger.info(
            f"✅ Session Manager enabled "
            f"(timeout: {self.session_timeout.total_seconds() // 60}min, "
            f"max: {self.max_session_lifetime.total_seconds() // 3600}h)"
        )
    
    def create_session(self, user: str, **extra_data):
        """Create a new session for user
        
        Args:
            user: Username
            **extra_data: Additional session data
        """
        session.permanent = True
        session['user'] = user
        session['created_at'] = datetime.utcnow().isoformat()
        session['last_activity'] = datetime.utcnow().isoformat()
        session['session_id'] = secrets.token_urlsafe(32)
        session['ip_address'] = request.remote_addr
        session['user_agent'] = request.headers.get('User-Agent', 'Unknown')
        
        # Add extra data
        for key, value in extra_data.items():
            session[key] = value
        
        logger.info(
            f"Session created for user '{user}' from {request.remote_addr}"
        )
    
    def clear_session(self):
        """Clear current session"""
        user = session.get('user', 'unknown')
        session.clear()
        logger.info(f"Session cleared for user '{user}'")
    
    def _is_session_valid(self) -> bool:
        """Check if current session is valid
        
        Returns:
            True if session is valid, False otherwise
        """
        # Check if session has required fields
        if not all(key in session for key in ['created_at', 'last_activity']):
            return False
        
        try:
            created_at = datetime.fromisoformat(session['created_at'])
            last_activity = datetime.fromisoformat(session['last_activity'])
            now = datetime.utcnow()
            
            # Check maximum session lifetime
            if now - created_at > self.max_session_lifetime:
                logger.debug("Session exceeded maximum lifetime")
                return False
            
            # Check activity timeout
            if now - last_activity > self.activity_timeout:
                logger.debug("Session exceeded activity timeout")
                return False
            
            # Check if IP address changed (potential session hijacking)
            if session.get('ip_address') != request.remote_addr:
                logger.warning(
                    f"Session IP changed from {session.get('ip_address')} "
                    f"to {request.remote_addr}"
                )
                return False
            
            return True
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error validating session: {e}")
            return False
    
    def _update_activity(self):
        """Update last activity timestamp"""
        session['last_activity'] = datetime.utcnow().isoformat()
    
    def _should_rotate_session(self) -> bool:
        """Check if session ID should be rotated
        
        Returns:
            True if session should be rotated
        """
        # Rotate session every 15 minutes
        if 'last_rotation' not in session:
            return True
        
        try:
            last_rotation = datetime.fromisoformat(session['last_rotation'])
            return datetime.utcnow() - last_rotation > timedelta(minutes=15)
        except (ValueError, TypeError):
            return True
    
    def _rotate_session(self):
        """Rotate session ID (prevent session fixation attacks)"""
        # Generate new session ID
        old_session_id = session.get('session_id')
        new_session_id = secrets.token_urlsafe(32)
        
        session['session_id'] = new_session_id
        session['last_rotation'] = datetime.utcnow().isoformat()
        
        logger.debug(f"Session ID rotated for user {session.get('user')}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information
        
        Returns:
            Dictionary with session info
        """
        if 'user' not in session:
            return {'authenticated': False}
        
        try:
            created_at = datetime.fromisoformat(session['created_at'])
            last_activity = datetime.fromisoformat(session['last_activity'])
            now = datetime.utcnow()
            
            return {
                'authenticated': True,
                'user': session.get('user'),
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'session_age_seconds': (now - created_at).total_seconds(),
                'time_since_activity_seconds': (now - last_activity).total_seconds(),
                'expires_in_seconds': (
                    self.activity_timeout.total_seconds() - 
                    (now - last_activity).total_seconds()
                ),
                'ip_address': session.get('ip_address'),
                'user_agent': session.get('user_agent')
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Error getting session info: {e}")
            return {'authenticated': True, 'user': session.get('user'), 'error': str(e)}


# Singleton instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get session manager singleton
    
    Returns:
        SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def init_session_manager(app, config: Optional[Dict] = None) -> SessionManager:
    """Initialize session manager with Flask app
    
    Args:
        app: Flask application instance
        config: Session configuration
    
    Returns:
        Initialized SessionManager instance
    """
    global _session_manager
    _session_manager = SessionManager(app, config)
    return _session_manager
