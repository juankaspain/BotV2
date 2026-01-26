"""
Sensitive Data Formatter - Redacts sensitive information from logs
Prevents credentials, API keys, passwords from being logged
"""

import re
import logging
from typing import List, Pattern


class SensitiveFormatter(logging.Formatter):
    """
    Custom log formatter that redacts sensitive information
    
    Automatically detects and redacts:
    - Passwords
    - API keys
    - Secrets
    - Tokens
    - Authorization headers
    - Database connection strings
    """
    
    # Patterns to detect sensitive data
    SENSITIVE_PATTERNS: List[Pattern] = [
        # password=something, password: something, password="something"
        re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)(["\'}\s]?)', re.IGNORECASE),
        
        # api_key=something, apiKey: something
        re.compile(r'(api[-_]?key["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)(["\'}\s]?)', re.IGNORECASE),
        
        # secret=something
        re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)(["\'}\s]?)', re.IGNORECASE),
        
        # token=something, bearer token
        re.compile(r'(token["\']?\s*[:=]\s*["\']?)([^"\'}\s]+)(["\'}\s]?)', re.IGNORECASE),
        re.compile(r'(bearer\s+)([a-zA-Z0-9\-._~+/]+=*)', re.IGNORECASE),
        
        # Authorization: Bearer/Basic ...
        re.compile(r'(authorization["\']?\s*[:=]\s*["\']?(?:bearer|basic)\s+)([^"\'}\s]+)', re.IGNORECASE),
        
        # Database URLs: postgresql://user:password@host/db
        re.compile(r'(postgresql://[^:]+:)([^@]+)(@)', re.IGNORECASE),
        re.compile(r'(mysql://[^:]+:)([^@]+)(@)', re.IGNORECASE),
        
        # Private keys (PEM format)
        re.compile(r'(-----BEGIN (?:RSA |EC )?PRIVATE KEY-----)([\s\S]+?)(-----END (?:RSA |EC )?PRIVATE KEY-----)', re.IGNORECASE),
        
        # AWS keys
        re.compile(r'(aws_access_key_id["\']?\s*[:=]\s*["\']?)([A-Z0-9]{20})(["\'}\s]?)', re.IGNORECASE),
        re.compile(r'(aws_secret_access_key["\']?\s*[:=]\s*["\']?)([A-Za-z0-9/+=]{40})(["\'}\s]?)', re.IGNORECASE),
    ]
    
    REDACTED_TEXT = "***REDACTED***"
    
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record and redact sensitive information
        
        Args:
            record: LogRecord to format
            
        Returns:
            Formatted and sanitized log message
        """
        # Format the message first
        original_message = super().format(record)
        
        # Redact sensitive information
        sanitized_message = self._redact_sensitive_data(original_message)
        
        return sanitized_message
    
    def _redact_sensitive_data(self, message: str) -> str:
        """
        Redact sensitive data from message
        
        Args:
            message: Original message
            
        Returns:
            Sanitized message
        """
        sanitized = message
        
        for pattern in self.SENSITIVE_PATTERNS:
            # Replace sensitive part with REDACTED
            # Keep prefix and suffix for context
            sanitized = pattern.sub(r'\1' + self.REDACTED_TEXT + r'\3', sanitized)
        
        return sanitized


def setup_sanitized_logger(name: str, log_level: str = 'INFO') -> logging.Logger:
    """
    Setup logger with sensitive data sanitization
    
    Args:
        name: Logger name
        log_level: Logging level
        
    Returns:
        Configured logger with sanitized formatter
    """
    import sys
    from pathlib import Path
    from logging.handlers import RotatingFileHandler
    from datetime import datetime
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Console handler with sanitization
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    console_formatter = SensitiveFormatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler with sanitization and rotation
    log_file = log_dir / f"botv2_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    file_formatter = SensitiveFormatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
