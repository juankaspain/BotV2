"""Security Audit Logger Module

Centralized security event logging for BotV2.
Logs authentication, CSRF, XSS, rate limiting, and other security events.
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from flask import request, session
import os


class SecurityAuditLogger:
    """Security Audit Logger
    
    Logs security events in structured JSON format with automatic rotation.
    """
    
    def __init__(self, log_file: str = 'logs/security_audit.log'):
        """Initialize security audit logger
        
        Args:
            log_file: Path to log file (default: logs/security_audit.log)
        """
        # Ensure logs directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Rotating file handler (10MB per file, keep 10 backups)
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=10
            )
            
            # JSON formatter (one line per event)
            handler.setFormatter(logging.Formatter('%(message)s'))
            
            self.logger.addHandler(handler)
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Get current request context information
        
        Returns:
            Dictionary with IP, user agent, user, session ID
        """
        context = {}
        
        try:
            # Get IP address
            context['ip_address'] = request.remote_addr if request else None
            
            # Get user agent
            context['user_agent'] = request.headers.get('User-Agent', 'Unknown') if request else None
            
            # Get current user
            context['user'] = session.get('user') if session else None
            
            # Get session ID
            context['session_id'] = session.get('session_id') if session else None
            
            # Get request path
            context['path'] = request.path if request else None
            
            # Get request method
            context['method'] = request.method if request else None
        except RuntimeError:
            # Outside request context
            pass
        
        return context
    
    def _log_event(self, event_type: str, severity: str, **kwargs):
        """Log security event
        
        Args:
            event_type: Type of event (e.g., 'login_success', 'csrf_failure')
            severity: Log level (INFO, WARNING, ERROR, CRITICAL)
            **kwargs: Additional event data
        """
        # Build log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'severity': severity.upper(),
            **self._get_request_context(),
            **kwargs
        }
        
        # Remove None values
        log_entry = {k: v for k, v in log_entry.items() if v is not None}
        
        # Log as JSON
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(json.dumps(log_entry))
    
    # ==================== AUTHENTICATION EVENTS ====================
    
    def log_login_success(self, username: str, **kwargs):
        """Log successful login"""
        self._log_event('auth.login.success', 'INFO', user=username, **kwargs)
    
    def log_login_failure(self, username: str, reason: str = 'invalid_credentials', **kwargs):
        """Log failed login attempt"""
        self._log_event(
            'auth.login.failed',
            'WARNING',
            user=username,
            reason=reason,
            **kwargs
        )
    
    def log_logout(self, username: str, **kwargs):
        """Log logout"""
        self._log_event('auth.logout', 'INFO', user=username, **kwargs)
    
    def log_account_locked(self, username: str, reason: str, **kwargs):
        """Log account lockout"""
        self._log_event(
            'auth.account.locked',
            'ERROR',
            user=username,
            reason=reason,
            **kwargs
        )
    
    # ==================== SESSION EVENTS ====================
    
    def log_session_created(self, session_id: str, **kwargs):
        """Log session creation"""
        self._log_event(
            'session.created',
            'INFO',
            session_id=session_id,
            **kwargs
        )
    
    def log_session_destroyed(self, session_id: str, reason: str = 'logout', **kwargs):
        """Log session destruction"""
        self._log_event(
            'session.destroyed',
            'INFO',
            session_id=session_id,
            reason=reason,
            **kwargs
        )
    
    def log_session_timeout(self, session_id: str, timeout_type: str = 'idle', **kwargs):
        """Log session timeout"""
        self._log_event(
            'session.timeout',
            'INFO',
            session_id=session_id,
            timeout_type=timeout_type,
            **kwargs
        )
    
    # ==================== CSRF EVENTS ====================
    
    def log_csrf_failure(self, reason: str = 'invalid_token', **kwargs):
        """Log CSRF validation failure"""
        self._log_event(
            'security.csrf.validation_failed',
            'WARNING',
            reason=reason,
            **kwargs
        )
    
    # ==================== XSS EVENTS ====================
    
    def log_xss_attempt(self, field: str, value: str, **kwargs):
        """Log XSS attempt detection"""
        self._log_event(
            'security.xss.attempt_detected',
            'CRITICAL',
            field=field,
            value_preview=value[:100],  # First 100 chars
            **kwargs
        )
    
    # ==================== RATE LIMIT EVENTS ====================
    
    def log_rate_limit_exceeded(self, endpoint: str, limit: str, **kwargs):
        """Log rate limit violation"""
        self._log_event(
            'security.rate_limit.exceeded',
            'WARNING',
            endpoint=endpoint,
            limit=limit,
            **kwargs
        )
    
    # ==================== CONFIGURATION EVENTS ====================
    
    def log_config_change(self, key: str, old_value: Any, new_value: Any, **kwargs):
        """Log configuration change"""
        self._log_event(
            'config.changed',
            'WARNING',
            config_key=key,
            old_value=str(old_value),
            new_value=str(new_value),
            **kwargs
        )
    
    # ==================== SYSTEM EVENTS ====================
    
    def log_system_startup(self, version: str, environment: str, **kwargs):
        """Log system startup"""
        self._log_event(
            'system.startup',
            'INFO',
            version=version,
            environment=environment,
            **kwargs
        )
    
    def log_system_shutdown(self, **kwargs):
        """Log system shutdown"""
        self._log_event('system.shutdown', 'INFO', **kwargs)


# ==================== GLOBAL INSTANCE ====================

_audit_logger: Optional[SecurityAuditLogger] = None


def get_audit_logger() -> SecurityAuditLogger:
    """Get global audit logger instance (singleton)
    
    Returns:
        SecurityAuditLogger instance
    """
    global _audit_logger
    
    if _audit_logger is None:
        log_file = os.getenv('SECURITY_AUDIT_LOG', 'logs/security_audit.log')
        _audit_logger = SecurityAuditLogger(log_file)
    
    return _audit_logger


def init_audit_logger(log_file: str = 'logs/security_audit.log') -> SecurityAuditLogger:
    """Initialize global audit logger
    
    Args:
        log_file: Path to log file
        
    Returns:
        SecurityAuditLogger instance
    """
    global _audit_logger
    _audit_logger = SecurityAuditLogger(log_file)
    return _audit_logger
