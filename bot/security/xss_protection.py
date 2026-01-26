"""XSS Protection Module

Provides Cross-Site Scripting (XSS) protection through HTML sanitization.
Uses bleach library for whitelist-based sanitization.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Callable
from functools import wraps
from flask import request, Flask

logger = logging.getLogger(__name__)

# Try to import bleach
try:
    import bleach
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False
    logger.warning("⚠️ bleach not installed - XSS protection limited to basic escaping")


# Whitelist configuration
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'code', 'pre', 'blockquote',
    'span', 'div'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'span': ['class'],
    'div': ['class']
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

# Dangerous patterns to detect
XSS_PATTERNS = [
    re.compile(r'<script', re.IGNORECASE),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # onerror=, onclick=, etc.
    re.compile(r'<iframe', re.IGNORECASE),
    re.compile(r'<embed', re.IGNORECASE),
    re.compile(r'<object', re.IGNORECASE),
    re.compile(r'eval\(', re.IGNORECASE),
    re.compile(r'expression\(', re.IGNORECASE),
]


def sanitize_html(html: str, strip: bool = False) -> str:
    """Sanitize HTML input to prevent XSS
    
    Args:
        html: HTML string to sanitize
        strip: If True, strip tags instead of escaping (default: False)
        
    Returns:
        Sanitized HTML string
    """
    if not html:
        return ''
    
    if HAS_BLEACH:
        return bleach.clean(
            html,
            tags=ALLOWED_TAGS if not strip else [],
            attributes=ALLOWED_ATTRIBUTES,
            protocols=ALLOWED_PROTOCOLS,
            strip=strip
        )
    else:
        # Fallback: basic HTML escaping
        import html as html_lib
        return html_lib.escape(html)


def sanitize_dict(data: Dict[str, Any], strip: bool = False) -> Dict[str, Any]:
    """Recursively sanitize dictionary values
    
    Args:
        data: Dictionary to sanitize
        strip: If True, strip HTML tags
        
    Returns:
        Sanitized dictionary
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html(value, strip=strip)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, strip=strip)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_html(v, strip=strip) if isinstance(v, str)
                else sanitize_dict(v, strip=strip) if isinstance(v, dict)
                else v
                for v in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def contains_xss(text: str) -> bool:
    """Check if string contains potential XSS patterns
    
    Args:
        text: String to check
        
    Returns:
        True if XSS patterns detected, False otherwise
    """
    if not text:
        return False
    
    return any(pattern.search(text) for pattern in XSS_PATTERNS)


def detect_xss_attempt(data: Any) -> Optional[str]:
    """Detect XSS attempts in data
    
    Args:
        data: Data to check (string, dict, or list)
        
    Returns:
        Field name where XSS was detected, or None
    """
    if isinstance(data, str):
        if contains_xss(data):
            return 'value'
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and contains_xss(value):
                return key
            elif isinstance(value, (dict, list)):
                nested = detect_xss_attempt(value)
                if nested:
                    return f"{key}.{nested}"
    elif isinstance(data, list):
        for i, value in enumerate(data):
            if isinstance(value, str) and contains_xss(value):
                return f"[{i}]"
            elif isinstance(value, (dict, list)):
                nested = detect_xss_attempt(value)
                if nested:
                    return f"[{i}].{nested}"
    
    return None


def sanitize_request_data(strip: bool = False):
    """Decorator to automatically sanitize request data
    
    Args:
        strip: If True, strip HTML tags completely
        
    Example:
        @app.route('/api/create', methods=['POST'])
        @sanitize_request_data(strip=True)
        def create_item():
            data = request.get_json()
            # data is now sanitized
            return jsonify(data)
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Sanitize form data
            if request.form:
                request.form = sanitize_dict(request.form.to_dict(), strip=strip)
            
            # Sanitize JSON data
            if request.is_json:
                try:
                    json_data = request.get_json(silent=True)
                    if json_data:
                        if isinstance(json_data, dict):
                            request._sanitized_json = sanitize_dict(json_data, strip=strip)
                        elif isinstance(json_data, list):
                            request._sanitized_json = [
                                sanitize_dict(item, strip=strip) if isinstance(item, dict)
                                else sanitize_html(item, strip=strip) if isinstance(item, str)
                                else item
                                for item in json_data
                            ]
                except Exception as e:
                    logger.error(f"Error sanitizing JSON: {e}")
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator


def xss_protection_middleware(app: Flask, strip: bool = False, detect_only: bool = False):
    """Add XSS protection middleware to Flask app
    
    Args:
        app: Flask application instance
        strip: If True, strip HTML tags completely
        detect_only: If True, only detect and log XSS attempts without sanitizing
    """
    @app.before_request
    def check_xss():
        # Skip for safe methods
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return
        
        # Check JSON data
        if request.is_json:
            try:
                json_data = request.get_json(silent=True)
                if json_data:
                    xss_field = detect_xss_attempt(json_data)
                    if xss_field:
                        logger.warning(
                            f"XSS attempt detected in field '{xss_field}' "
                            f"from {request.remote_addr} on {request.path}"
                        )
                        
                        # Log to security audit if available
                        try:
                            from .audit_logger import get_audit_logger
                            audit_logger = get_audit_logger()
                            audit_logger.log_xss_attempt(
                                field=xss_field,
                                value=str(json_data.get(xss_field, ''))[:100]
                            )
                        except Exception:
                            pass
                        
                        if detect_only:
                            # Just log, don't block
                            pass
                        else:
                            # Sanitize the data
                            if isinstance(json_data, dict):
                                request._sanitized_json = sanitize_dict(json_data, strip=strip)
                            elif isinstance(json_data, list):
                                request._sanitized_json = [
                                    sanitize_dict(item, strip=strip) if isinstance(item, dict) else item
                                    for item in json_data
                                ]
            except Exception as e:
                logger.error(f"Error checking XSS: {e}")
        
        # Check form data
        if request.form:
            form_dict = request.form.to_dict()
            xss_field = detect_xss_attempt(form_dict)
            if xss_field:
                logger.warning(
                    f"XSS attempt detected in form field '{xss_field}' "
                    f"from {request.remote_addr} on {request.path}"
                )
                
                if not detect_only:
                    # Sanitize form data
                    request.form = sanitize_dict(form_dict, strip=strip)
    
    logger.info(f"✅ XSS Protection middleware enabled (strip={strip}, detect_only={detect_only})")


def escape_html(text: str) -> str:
    """Escape HTML entities in text
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    import html as html_lib
    return html_lib.escape(text)


def strip_tags(html: str) -> str:
    """Strip all HTML tags from string
    
    Args:
        html: HTML string
        
    Returns:
        Plain text without HTML tags
    """
    if HAS_BLEACH:
        return bleach.clean(html, tags=[], strip=True)
    else:
        # Basic tag stripping with regex
        return re.sub(r'<[^>]+>', '', html)
