"""Security Audit Logger Module

Provides comprehensive security event logging for compliance and forensics.
Logs all authentication, authorization, and security-related events.
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from flask import request, session


class SecurityAuditLogger:
    """Professional security audit logger with JSON formatting"""
    
    def __init__(self, log_file: str = 'logs/security_audit.log', level: str = 'INFO'):
        """
        Initialize security audit logger
        
        Args:
            log_file: Path to log file
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.logger.propagate = False  # Don't propagate to root logger
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        
        # JSON formatter (one event per line)
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)
        
        # Console handler for critical events
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(
            logging.Formatter('[%(levelname)s] %(message)s')
        )
        self.logger.addHandler(console_handler)
    
    def log_event(
        self,
        event_type: str,
        severity: str = 'INFO',
        user: Optional[str] = None,
        ip: Optional[str] = None,
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log a security event
        
        Args:
            event_type: Type of event (e.g., 'login_success', 'csrf_failure')
            severity: Log severity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            user: Username associated with event
            ip: IP address
            session_id: Session identifier
            details: Additional event details
            **kwargs: Additional fields to log
        """
        # Auto-populate from Flask request context if available
        if ip is None:
            try:
                ip = request.remote_addr
            except RuntimeError:
                ip = 'N/A'
        
        if user is None:
            try:
                user = session.get('user', 'anonymous')
            except RuntimeError:
                user = 'anonymous'
        
        if session_id is None:
            try:
                session_id = session.get('session_id', 'N/A')
            except RuntimeError:
                session_id = 'N/A'
        
        # Build log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'severity': severity.upper(),
            'user': user,
            'ip_address': ip,
            'session_id': session_id,
        }
        
        # Add user agent if available
        try:
            log_entry['user_agent'] = request.headers.get('User-Agent', 'Unknown')
            log_entry['endpoint'] = request.endpoint
            log_entry['method'] = request.method
            log_entry['path'] = request.path
        except RuntimeError:
            pass
        
        # Add details
        if details:
            log_entry['details'] = details
        
        # Add kwargs
        log_entry.update(kwargs)
        
        # Log as JSON
        log_message = json.dumps(log_entry, ensure_ascii=False)
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(log_message)
    
    # ==================== AUTHENTICATION EVENTS ====================
    
    def log_login_success(self, username: str, **kwargs):
        """Log successful login"""
        self.log_event(
            'auth.login.success',
            severity='INFO',
            user=username,
            **kwargs
        )
    
    def log_login_failure(self, username: str, reason: str = 'invalid_credentials', **kwargs):
        """Log failed login attempt"""
        self.log_event(
            'auth.login.failed',
            severity='WARNING',
            user=username,
            details={'reason': reason},
            **kwargs
        )
    
    def log_logout(self, username: str, **kwargs):
        """Log logout event"""
        self.log_event(
            'auth.logout',
            severity='INFO',
            user=username,
            **kwargs
        )
    
    def log_account_locked(self, username: str, reason: str, **kwargs):
        """Log account lockout"""
        self.log_event(
            'auth.account.locked',
            severity='ERROR',
            user=username,
            details={'reason': reason},
            **kwargs
        )
    
    # ==================== SESSION EVENTS ====================
    
    def log_session_created(self, username: str, session_id: str, **kwargs):
        """Log session creation"""
        self.log_event(
            'session.created',
            severity='INFO',
            user=username,
            session_id=session_id,
            **kwargs
        )
    
    def log_session_destroyed(self, username: str, session_id: str, reason: str, **kwargs):
        """Log session destruction"""
        self.log_event(
            'session.destroyed',
            severity='INFO',
            user=username,
            session_id=session_id,
            details={'reason': reason},
            **kwargs
        )
    
    def log_session_timeout(self, username: str, session_id: str, timeout_type: str, **kwargs):
        """Log session timeout"""
        self.log_event(
            'session.timeout',
            severity='INFO',
            user=username,
            session_id=session_id,
            details={'timeout_type': timeout_type},
            **kwargs
        )
    
    # ==================== SECURITY VIOLATIONS ====================
    
    def log_csrf_failure(self, reason: str, **kwargs):
        """Log CSRF validation failure"""
        self.log_event(
            'security.csrf.failed',
            severity='WARNING',
            details={'reason': reason},
            **kwargs
        )
    
    def log_xss_attempt(self, field: str, value: str, **kwargs):
        """Log XSS attempt detection"""
        self.log_event(
            'security.xss.attempt',
            severity='CRITICAL',
            details={
                'field': field,
                'value': value[:100]  # Truncate for log
            },
            **kwargs
        )
    
    def log_sql_injection_attempt(self, query: str, **kwargs):
        """Log SQL injection attempt"""
        self.log_event(
            'security.sql_injection.attempt',
            severity='CRITICAL',
            details={'query': query[:200]},
            **kwargs
        )
    
    def log_rate_limit_exceeded(self, endpoint: str, limit: str, **kwargs):
        """Log rate limit violation"""
        self.log_event(
            'security.rate_limit.exceeded',
            severity='WARNING',
            details={'endpoint': endpoint, 'limit': limit},
            **kwargs
        )
    
    def log_invalid_input(self, field: str, error: str, **kwargs):
        """Log invalid input rejection"""
        self.log_event(
            'security.input.invalid',
            severity='WARNING',
            details={'field': field, 'error': error},
            **kwargs
        )
    
    # ==================== AUTHORIZATION EVENTS ====================
    
    def log_access_denied(self, resource: str, required_permission: str, **kwargs):
        """Log access denied event"""
        self.log_event(
            'authorization.access_denied',
            severity='WARNING',
            details={
                'resource': resource,
                'required_permission': required_permission
            },
            **kwargs
        )
    
    def log_privilege_escalation_attempt(self, attempted_action: str, **kwargs):
        """Log privilege escalation attempt"""
        self.log_event(
            'authorization.privilege_escalation.attempt',
            severity='CRITICAL',
            details={'attempted_action': attempted_action},
            **kwargs
        )
    
    # ==================== CONFIGURATION EVENTS ====================
    
    def log_config_change(self, setting: str, old_value: Any, new_value: Any, **kwargs):
        """Log configuration change"""
        self.log_event(
            'config.changed',
            severity='WARNING',
            details={
                'setting': setting,
                'old_value': str(old_value),
                'new_value': str(new_value)
            },
            **kwargs
        )
    
    def log_password_change(self, username: str, **kwargs):
        """Log password change"""
        self.log_event(
            'config.password.changed',
            severity='INFO',
            user=username,
            **kwargs
        )
    
    # ==================== SYSTEM EVENTS ====================
    
    def log_system_startup(self, version: str, environment: str, **kwargs):
        """Log system startup"""
        self.log_event(
            'system.startup',
            severity='INFO',
            user='system',
            details={'version': version, 'environment': environment},
            **kwargs
        )
    
    def log_system_shutdown(self, reason: str, **kwargs):
        """Log system shutdown"""
        self.log_event(
            'system.shutdown',
            severity='INFO',
            user='system',
            details={'reason': reason},
            **kwargs
        )
    
    def log_error(self, error_type: str, error_message: str, **kwargs):
        """Log system error"""
        self.log_event(
            'system.error',
            severity='ERROR',
            details={'error_type': error_type, 'message': error_message},
            **kwargs
        )


# Global instance
_audit_logger: Optional[SecurityAuditLogger] = None


def get_audit_logger() -> SecurityAuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger()
    return _audit_logger


def init_audit_logger(log_file: str = 'logs/security_audit.log', level: str = 'INFO') -> SecurityAuditLogger:
    """Initialize global audit logger
    
    Args:
        log_file: Path to log file
        level: Logging level
        
    Returns:
        SecurityAuditLogger instance
    """
    global _audit_logger
    _audit_logger = SecurityAuditLogger(log_file, level)
    return _audit_logger
