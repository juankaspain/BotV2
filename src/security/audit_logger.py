"""Security Audit Logger Module

Provides comprehensive security event logging for compliance and forensics.
Logs all security-relevant events in structured JSON format.
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from flask import request, session


class SecurityAuditLogger:
    """Professional security audit logger
    
    Features:
    - JSON-formatted logs for easy parsing
    - Automatic log rotation (daily, keep 30 days)
    - Contextual information (IP, user, session, etc.)
    - Severity levels (INFO, WARNING, ERROR, CRITICAL)
    - Integration with Flask request context
    """
    
    # Event severity levels
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'
    
    def __init__(self, log_file: str = 'logs/security_audit.log'):
        """
        Initialize security audit logger
        
        Args:
            log_file: Path to log file
        """
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Rotating file handler (daily rotation, keep 30 days)
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        
        # Simple formatter (we format as JSON ourselves)
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        
        # Also log to console in development
        if os.getenv('FLASK_ENV') == 'development':
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(console_handler)
    
    def log_event(self, event_type: str, level: str = INFO, **kwargs):
        """
        Log a security event
        
        Args:
            event_type: Type of event (e.g., 'auth.login.success')
            level: Severity level (INFO, WARNING, ERROR, CRITICAL)
            **kwargs: Additional event data
        """
        # Build log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'event_type': event_type,
        }
        
        # Add Flask request context if available
        try:
            if request:
                log_entry.update({
                    'ip': kwargs.get('ip', request.remote_addr),
                    'method': kwargs.get('method', request.method),
                    'path': kwargs.get('path', request.path),
                    'user_agent': kwargs.get('user_agent', request.headers.get('User-Agent', 'Unknown'))
                })
                
                # Add session info if available
                if session:
                    log_entry['user'] = kwargs.get('user', session.get('user', 'anonymous'))
                    log_entry['session_id'] = session.get('session_id')
        except RuntimeError:
            # Outside request context
            pass
        
        # Add custom kwargs
        for key, value in kwargs.items():
            if key not in log_entry:
                log_entry[key] = value
        
        # Log as JSON
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(log_entry, default=str))
    
    # Convenience methods for common event types
    
    def log_login_success(self, username: str, ip: Optional[str] = None):
        """Log successful login"""
        self.log_event(
            'auth.login.success',
            level=self.INFO,
            user=username,
            ip=ip or (request.remote_addr if request else 'unknown')
        )
    
    def log_login_failure(self, username: str, reason: str = 'invalid_credentials',
                          ip: Optional[str] = None):
        """Log failed login attempt"""
        self.log_event(
            'auth.login.failed',
            level=self.WARNING,
            user=username,
            reason=reason,
            ip=ip or (request.remote_addr if request else 'unknown')
        )
    
    def log_logout(self, username: str, ip: Optional[str] = None):
        """Log logout"""
        self.log_event(
            'auth.logout',
            level=self.INFO,
            user=username,
            ip=ip or (request.remote_addr if request else 'unknown')
        )
    
    def log_session_created(self, username: str, session_id: str):
        """Log session creation"""
        self.log_event(
            'session.created',
            level=self.INFO,
            user=username,
            session_id=session_id
        )
    
    def log_session_destroyed(self, username: str, session_id: str, reason: str):
        """Log session destruction"""
        self.log_event(
            'session.destroyed',
            level=self.INFO,
            user=username,
            session_id=session_id,
            reason=reason
        )
    
    def log_csrf_failure(self, path: str, ip: Optional[str] = None):
        """Log CSRF validation failure"""
        self.log_event(
            'security.csrf.failed',
            level=self.WARNING,
            path=path,
            ip=ip or (request.remote_addr if request else 'unknown')
        )
    
    def log_xss_attempt(self, field: str, value: str, ip: Optional[str] = None):
        """Log potential XSS attempt"""
        self.log_event(
            'security.xss.attempt',
            level=self.CRITICAL,
            field=field,
            value=value[:100],  # Truncate to 100 chars
            ip=ip or (request.remote_addr if request else 'unknown')
        )
    
    def log_rate_limit_exceeded(self, path: str, limit: str, ip: Optional[str] = None):
        """Log rate limit violation"""
        self.log_event(
            'security.rate_limit.exceeded',
            level=self.WARNING,
            path=path,
            limit=limit,
            ip=ip or (request.remote_addr if request else 'unknown')
        )
    
    def log_config_change(self, setting: str, old_value: Any, new_value: Any,
                          user: Optional[str] = None):
        """Log configuration change"""
        self.log_event(
            'config.changed',
            level=self.WARNING,
            setting=setting,
            old_value=str(old_value),
            new_value=str(new_value),
            user=user or (session.get('user') if session else 'unknown')
        )
    
    def log_password_change(self, username: str, ip: Optional[str] = None):
        """Log password change"""
        self.log_event(
            'auth.password.changed',
            level=self.INFO,
            user=username,
            ip=ip or (request.remote_addr if request else 'unknown')
        )
    
    def log_account_locked(self, username: str, reason: str, locked_until: str,
                           ip: Optional[str] = None):
        """Log account lockout"""
        self.log_event(
            'auth.account.locked',
            level=self.ERROR,
            user=username,
            reason=reason,
            locked_until=locked_until,
            ip=ip or (request.remote_addr if request else 'unknown')
        )


# Singleton instance
_audit_logger = None


def get_audit_logger() -> SecurityAuditLogger:
    """Get singleton audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger()
    return _audit_logger


# Convenience function
def log_security_event(event_type: str, level: str = SecurityAuditLogger.INFO, **kwargs):
    """Log a security event (convenience function)"""
    logger = get_audit_logger()
    logger.log_event(event_type, level, **kwargs)
