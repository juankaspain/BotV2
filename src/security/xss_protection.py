"""XSS Protection Module

Provides Cross-Site Scripting (XSS) protection through input sanitization.
Uses bleach for HTML sanitization and provides utilities for safe output.
"""

import logging
import re
from typing import Optional, List, Dict, Any
import html

try:
    import bleach
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False

logger = logging.getLogger(__name__)


class XSSProtection:
    """XSS Protection Manager
    
    Provides comprehensive XSS protection through:
    - HTML sanitization (removes dangerous tags/attributes)
    - URL validation
    - JavaScript escaping
    - Safe output encoding
    """
    
    # Safe HTML tags (whitelist)
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'span', 'div'
    ]
    
    # Safe HTML attributes (whitelist)
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target'],
        'span': ['class'],
        'div': ['class'],
        'code': ['class']
    }
    
    # Safe URL protocols
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'file:',
        r'<script',
        r'onerror=',
        r'onload=',
        r'onclick=',
        r'eval\(',
        r'expression\(',
    ]
    
    def __init__(self, allowed_tags: Optional[List[str]] = None,
                 allowed_attributes: Optional[Dict[str, List[str]]] = None):
        """
        Initialize XSS protection
        
        Args:
            allowed_tags: Custom list of allowed HTML tags
            allowed_attributes: Custom dict of allowed attributes per tag
        """
        self.allowed_tags = allowed_tags or self.ALLOWED_TAGS
        self.allowed_attributes = allowed_attributes or self.ALLOWED_ATTRIBUTES
        
        if not HAS_BLEACH:
            logger.warning(
                "⚠️ bleach not installed - XSS protection will use basic escaping only. "
                "Install with: pip install bleach"
            )
    
    def sanitize_html(self, text: str, strip: bool = False) -> str:
        """Sanitize HTML content to prevent XSS
        
        Args:
            text: HTML content to sanitize
            strip: If True, remove all HTML tags; if False, allow safe tags
        
        Returns:
            Sanitized HTML string
        """
        if not text:
            return ""
        
        if HAS_BLEACH:
            if strip:
                # Remove all HTML tags
                return bleach.clean(text, tags=[], strip=True)
            else:
                # Allow only safe tags and attributes
                return bleach.clean(
                    text,
                    tags=self.allowed_tags,
                    attributes=self.allowed_attributes,
                    protocols=self.ALLOWED_PROTOCOLS,
                    strip=True
                )
        else:
            # Fallback: HTML escape everything
            return html.escape(text)
    
    def sanitize_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize all string values in a JSON object
        
        Args:
            data: Dictionary to sanitize
        
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_html(value, strip=True)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_json(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_json(item) if isinstance(item, dict)
                    else self.sanitize_html(item, strip=True) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    def validate_url(self, url: str) -> bool:
        """Validate URL to prevent XSS through href attributes
        
        Args:
            url: URL to validate
        
        Returns:
            True if URL is safe, False otherwise
        """
        if not url:
            return False
        
        # Check for dangerous patterns
        url_lower = url.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, url_lower, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected in URL: {pattern}")
                return False
        
        # Check protocol
        if '://' in url:
            protocol = url.split('://')[0].lower()
            if protocol not in self.ALLOWED_PROTOCOLS:
                logger.warning(f"Disallowed protocol in URL: {protocol}")
                return False
        
        return True
    
    def escape_js(self, text: str) -> str:
        """Escape text for safe use in JavaScript context
        
        Args:
            text: Text to escape
        
        Returns:
            JavaScript-safe escaped string
        """
        if not text:
            return ""
        
        # Escape special characters for JavaScript
        replacements = {
            '\\': '\\\\',
            '"': '\\"',
            "'": "\\'",
            '\n': '\\n',
            '\r': '\\r',
            '\t': '\\t',
            '<': '\\x3C',  # Prevent </script> injection
            '>': '\\x3E',
            '&': '\\x26'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def safe_format(self, template: str, **kwargs) -> str:
        """Safely format a template string with sanitized values
        
        Args:
            template: Template string with {key} placeholders
            **kwargs: Values to substitute (will be sanitized)
        
        Returns:
            Formatted string with sanitized values
        """
        sanitized_kwargs = {
            key: self.sanitize_html(str(value), strip=True)
            for key, value in kwargs.items()
        }
        return template.format(**sanitized_kwargs)
    
    def check_input(self, text: str) -> bool:
        """Check if input contains potential XSS attacks
        
        Args:
            text: Input text to check
        
        Returns:
            True if input is safe, False if suspicious
        """
        if not text:
            return True
        
        text_lower = text.lower()
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Suspicious pattern detected: {pattern}")
                return False
        
        return True


# Singleton instance
_xss_protection = XSSProtection()


# Convenience functions
def sanitize_html(text: str, strip: bool = False) -> str:
    """Sanitize HTML content (convenience function)"""
    return _xss_protection.sanitize_html(text, strip)


def sanitize_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize JSON data (convenience function)"""
    return _xss_protection.sanitize_json(data)


def validate_url(url: str) -> bool:
    """Validate URL (convenience function)"""
    return _xss_protection.validate_url(url)


def escape_js(text: str) -> str:
    """Escape for JavaScript (convenience function)"""
    return _xss_protection.escape_js(text)


def safe_format(template: str, **kwargs) -> str:
    """Safe string formatting (convenience function)"""
    return _xss_protection.safe_format(template, **kwargs)
