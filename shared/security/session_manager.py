# -*- coding: utf-8 -*-
"""
Session Manager Module
Provides secure session management
"""

import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, redirect, url_for


class SessionManager:
    """Secure session manager"""
    
    def __init__(self, app=None, session_lifetime=3600):
        self.app = app
        self.session_lifetime = session_lifetime
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.config.setdefault('SESSION_COOKIE_SECURE', True)
        app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
        app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
        app.config.setdefault('PERMANENT_SESSION_LIFETIME', timedelta(seconds=self.session_lifetime))
        
        if not app.config.get('SECRET_KEY'):
            app.config['SECRET_KEY'] = secrets.token_hex(32)
    
    def create_session(self, user_id, **kwargs):
        """Create a new session"""
        session.permanent = True
        session['user_id'] = user_id
        session['created_at'] = datetime.utcnow().isoformat()
        session['session_token'] = secrets.token_hex(16)
        
        for key, value in kwargs.items():
            session[key] = value
        
        return session['session_token']
    
    def destroy_session(self):
        """Destroy current session"""
        session.clear()
    
    def is_valid(self):
        """Check if current session is valid"""
        if 'user_id' not in session:
            return False
        
        if 'created_at' not in session:
            return False
        
        created = datetime.fromisoformat(session['created_at'])
        if datetime.utcnow() - created > timedelta(seconds=self.session_lifetime):
            self.destroy_session()
            return False
        
        return True
    
    def get_user_id(self):
        """Get current user ID"""
        return session.get('user_id')
    
    def refresh(self):
        """Refresh session timestamp"""
        session['created_at'] = datetime.utcnow().isoformat()


# Global session manager
_session_manager = None


def init_session(app=None, **kwargs):
    """Initialize session manager"""
    global _session_manager
    _session_manager = SessionManager(app, **kwargs)
    return _session_manager


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if _session_manager and not _session_manager.is_valid():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
