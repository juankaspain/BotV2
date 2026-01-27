# -*- coding: utf-8 -*-
"""
Audit Logger Module
Provides security audit logging
"""

import logging
import json
from datetime import datetime
from functools import wraps
from typing import Optional, Dict, Any
from flask import request, g, Flask


class SecurityAuditLogger:
    """Security audit logger"""
    
    def __init__(self, app: Optional[Flask] = None, logger_name='security_audit'):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        self.app = app
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize with Flask app"""
        self.app = app
    
    def log_event(self, event_type, details=None, user_id=None, severity='INFO'):
        """Log a security event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'severity': severity,
            'user_id': user_id,
            'ip_address': self._get_client_ip(),
            'details': details or {}
        }
        
        log_level = getattr(logging, severity.upper(), logging.INFO)
        self.logger.log(log_level, json.dumps(event))
        
        return event
    
    def log_login_attempt(self, user_id, success, details=None):
        """Log login attempt"""
        return self.log_event(
            'LOGIN_ATTEMPT',
            {'success': success, **(details or {})},
            user_id,
            'INFO' if success else 'WARNING'
        )
    
    def log_login_success(self, username: str):
        """Log successful login"""
        return self.log_event('LOGIN_SUCCESS', {'username': username}, username, 'INFO')
    
    def log_login_failure(self, username: str, reason: str = None, failed_attempts: int = 0):
        """Log failed login attempt"""
        return self.log_event(
            'LOGIN_FAILURE',
            {'username': username, 'reason': reason, 'failed_attempts': failed_attempts},
            username,
            'WARNING'
        )
    
    def log_logout(self, username: str):
        """Log user logout"""
        return self.log_event('LOGOUT', {'username': username}, username, 'INFO')
    
    def log_session_timeout(self, username: str, session_id: str, reason: str = None):
        """Log session timeout"""
        return self.log_event(
            'SESSION_TIMEOUT',
            {'username': username, 'session_id': session_id, 'reason': reason},
            username,
            'INFO'
        )
    
    def log_account_locked(self, username: str, reason: str = None, locked_until: str = None):
        """Log account lockout"""
        return self.log_event(
            'ACCOUNT_LOCKED',
            {'username': username, 'reason': reason, 'locked_until': locked_until},
            username,
            'WARNING'
        )
    
    def log_invalid_input(self, field: str, error: str):
        """Log invalid input attempt"""
        return self.log_event(
            'INVALID_INPUT',
            {'field': field, 'error': error},
            severity='WARNING'
        )
    
    def log_system_startup(self, version: str, environment: str):
        """Log system startup"""
        return self.log_event(
            'SYSTEM_STARTUP',
            {'version': version, 'environment': environment},
            severity='INFO'
        )
    
    def log_access(self, resource, action, user_id=None):
        """Log resource access"""
        return self.log_event(
            'RESOURCE_ACCESS',
            {'resource': resource, 'action': action},
            user_id
        )
    
    def log_security_violation(self, violation_type, details=None, user_id=None):
        """Log security violation"""
        return self.log_event(
            'SECURITY_VIOLATION',
            {'violation_type': violation_type, **(details or {})},
            user_id,
            'CRITICAL'
        )
    
    @staticmethod
    def _get_client_ip():
        """Get client IP address"""
        try:
            if request:
                return request.headers.get('X-Forwarded-For', request.remote_addr)
        except RuntimeError:
            pass
        return None


# Global audit logger
_audit_logger: Optional[SecurityAuditLogger] = None


def init_audit_logger(app: Flask = None) -> SecurityAuditLogger:
    """Initialize and return audit logger"""
    global _audit_logger
    _audit_logger = SecurityAuditLogger(app)
    return _audit_logger


def get_audit_logger() -> SecurityAuditLogger:
    """Get or create audit logger"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger()
    return _audit_logger


def audit_log(event_type, severity='INFO'):
    """Decorator for audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = getattr(g, 'user_id', None)
            get_audit_logger().log_event(
                event_type,
                {'endpoint': request.endpoint, 'method': request.method},
                user_id,
                severity
            )
            return f(*args, **kwargs)
        return decorated_function
    return decorator
