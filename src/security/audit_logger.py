"""Security Audit Logger Module

Provides comprehensive security event logging for compliance and forensics.
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from flask import request, session
import os

logger = logging.getLogger(__name__)


class SecurityAuditLogger:
    """Professional Security Audit Logger
    
    Logs all security-relevant events:
    - Authentication (login/logout)
    - Authorization failures
    - CSRF validation failures
    - Rate limit violations
    - XSS attempt detections
    - Session management events
    - Configuration changes
    - Suspicious activity
    """
    
    def __init__(self, log_file: str = 'logs/security_audit.log',
                 max_bytes: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 30):  # Keep 30 days
        """
        Initialize security audit logger
        
        Args:
            log_file: Path to security audit log file
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create dedicated logger for security events
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            # Rotating file handler
            handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            
            # JSON formatter for structured logging
            handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(handler)
        
        logger.info(f"✅ Security Audit Logger initialized: {log_file}")
    
    def log_event(self, event_type: str, severity: str = 'INFO', **kwargs):
        """Log a security event
        
        Args:
            event_type: Type of security event (e.g., 'auth.login.success')
            severity: Log level (INFO, WARNING, ERROR, CRITICAL)
            **kwargs: Additional event details
        """
        # Build log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'severity': severity.upper(),
            **self._get_request_context(),
            **kwargs
        }
        
        # Log at appropriate level
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(json.dumps(log_entry))
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Get context from current request
        
        Returns:
            Dictionary with request context (IP, user agent, session, etc.)
        """
        context = {}
        
        # Try to get request context (may not be available in all contexts)
        try:
            if request:
                context['ip_address'] = request.remote_addr
                context['user_agent'] = request.headers.get('User-Agent', 'Unknown')
                context['method'] = request.method
                context['path'] = request.path
                context['endpoint'] = request.endpoint
                
                # Add session info if available
                if session:
                    context['user'] = session.get('user', 'anonymous')
                    context['session_id'] = session.get('session_id', 'none')
        except RuntimeError:
            # Outside request context
            pass
        
        return context
    
    # ==================== Authentication Events ====================
    
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
            'auth.login.failure',
            severity='WARNING',
            user=username,
            reason=reason,
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
            reason=reason,
            **kwargs
        )
    
    # ==================== Session Events ====================
    
    def log_session_created(self, session_id: str, user: str, **kwargs):
        """Log session creation"""
        self.log_event(
            'session.created',
            severity='INFO',
            session_id=session_id,
            user=user,
            **kwargs
        )
    
    def log_session_destroyed(self, session_id: str, user: str, reason: str, **kwargs):
        """Log session destruction"""
        self.log_event(
            'session.destroyed',
            severity='INFO',
            session_id=session_id,
            user=user,
            reason=reason,
            **kwargs
        )
    
    def log_session_timeout(self, session_id: str, user: str, timeout_type: str, **kwargs):
        """Log session timeout"""
        self.log_event(
            'session.timeout',
            severity='INFO',
            session_id=session_id,
            user=user,
            timeout_type=timeout_type,
            **kwargs
        )
    
    # ==================== Security Violations ====================
    
    def log_csrf_failure(self, reason: str = 'invalid_token', **kwargs):
        """Log CSRF validation failure"""
        self.log_event(
            'security.csrf.failure',
            severity='WARNING',
            reason=reason,
            **kwargs
        )
    
    def log_xss_attempt(self, input_field: str, malicious_content: str, **kwargs):
        """Log XSS attempt detection"""
        self.log_event(
            'security.xss.attempt',
            severity='CRITICAL',
            input_field=input_field,
            malicious_content=malicious_content[:200],  # Truncate for log size
            **kwargs
        )
    
    def log_rate_limit_exceeded(self, limit: str, **kwargs):
        """Log rate limit violation"""
        self.log_event(
            'security.rate_limit.exceeded',
            severity='WARNING',
            limit=limit,
            **kwargs
        )
    
    def log_invalid_input(self, field: str, error: str, **kwargs):
        """Log invalid input rejection"""
        self.log_event(
            'security.input.invalid',
            severity='WARNING',
            field=field,
            error=error,
            **kwargs
        )
    
    # ==================== System Events ====================
    
    def log_config_change(self, key: str, old_value: Any, new_value: Any, **kwargs):
        """Log configuration change"""
        self.log_event(
            'system.config.change',
            severity='WARNING',
            key=key,
            old_value=str(old_value)[:100],
            new_value=str(new_value)[:100],
            **kwargs
        )
    
    def log_startup(self, version: str, environment: str, **kwargs):
        """Log system startup"""
        self.log_event(
            'system.startup',
            severity='INFO',
            version=version,
            environment=environment,
            **kwargs
        )
    
    def log_shutdown(self, reason: str = 'normal', **kwargs):
        """Log system shutdown"""
        self.log_event(
            'system.shutdown',
            severity='INFO',
            reason=reason,
            **kwargs
        )


# Singleton instance
_audit_logger: Optional[SecurityAuditLogger] = None


def get_audit_logger() -> SecurityAuditLogger:
    """Get the singleton audit logger instance
    
    Returns:
        SecurityAuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        log_file = os.getenv('SECURITY_AUDIT_LOG', 'logs/security_audit.log')
        _audit_logger = SecurityAuditLogger(log_file)
    return _audit_logger
