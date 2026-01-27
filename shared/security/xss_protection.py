# -*- coding: utf-8 -*-
"""
XSS Protection Module
Provides protection against Cross-Site Scripting attacks
"""

import html
import re
import logging
from functools import wraps
from typing import Any, Dict, Optional
from flask import Flask, request, abort

logger = logging.getLogger(__name__)


def sanitize_html(text, strip: bool = False) -> Optional[str]:
    """Escape HTML entities to prevent XSS"""
    if text is None:
        return None
    
    text_str = str(text)
    
    if strip:
        # Remove all HTML tags
        clean = re.compile('<.*?>')
        text_str = re.sub(clean, '', text_str)
    
    return html.escape(text_str)


def sanitize_input(data) -> Any:
    """Recursively sanitize input data"""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        return sanitize_html(data)
    return data


def sanitize_dict(data: Dict, strip: bool = False) -> Dict:
    """Sanitize all string values in a dictionary"""
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = sanitize_html(value, strip=strip)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value, strip=strip)
        elif isinstance(value, list):
            result[key] = [sanitize_dict(v, strip=strip) if isinstance(v, dict) else sanitize_html(v, strip=strip) if isinstance(v, str) else v for v in value]
        else:
            result[key] = value
    return result


def strip_tags(text) -> Optional[str]:
    """Remove all HTML tags from text"""
    if text is None:
        return None
    clean = re.compile('<.*?>')
    return re.sub(clean, '', str(text))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    if not filename:
        return 'unnamed'
    
    # Remove path separators and dangerous characters
    sanitized = re.sub(r'[\\/:*?"<>|]', '_', filename)
    sanitized = sanitized.strip('. ')
    
    # Prevent path traversal
    sanitized = sanitized.replace('..', '_')
    
    return sanitized or 'unnamed'


def xss_protect(f):
    """Decorator to sanitize request inputs"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Sanitize query parameters
        if request.args:
            sanitized_args = sanitize_input(request.args.to_dict())
            request.sanitized_args = sanitized_args
        
        # Sanitize form data
        if request.form:
            sanitized_form = sanitize_input(request.form.to_dict())
            request.sanitized_form = sanitized_form
        
        return f(*args, **kwargs)
    return decorated_function


def xss_protection_middleware(app: Flask, strip: bool = True, detect_only: bool = False):
    """Flask middleware for XSS protection"""
    
    @app.before_request
    def check_xss():
        # Check for XSS patterns in request
        xss_patterns = [
            r'<script[^>]*>',
            r'javascript:',
            r'on\w+\s*=',
            r'data:text/html',
            r'<iframe',
            r'<embed',
            r'<object'
        ]
        
        # Check query string
        query_string = request.query_string.decode('utf-8', errors='ignore')
        for pattern in xss_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                logger.warning(f"XSS pattern detected in query: {pattern}")
                if not detect_only:
                    abort(400, description='Potentially malicious input detected')
                break
        
        # Check form data
        if request.form:
            form_str = str(request.form.to_dict())
            for pattern in xss_patterns:
                if re.search(pattern, form_str, re.IGNORECASE):
                    logger.warning(f"XSS pattern detected in form: {pattern}")
                    if not detect_only:
                        abort(400, description='Potentially malicious input detected')
                    break
    
    logger.info("XSS Protection middleware initialized")


def validate_content_type(allowed_types=None):
    """Decorator to validate content type"""
    if allowed_types is None:
        allowed_types = ['application/json', 'application/x-www-form-urlencoded']
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_type = request.content_type
            if content_type:
                # Extract base content type without parameters
                base_type = content_type.split(';')[0].strip()
                if base_type not in allowed_types:
                    abort(415)  # Unsupported Media Type
            return f(*args, **kwargs)
        return decorated_function
    return decorator
