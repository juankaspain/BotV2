# -*- coding: utf-8 -*-
"""
XSS Protection Module
Provides protection against Cross-Site Scripting attacks
"""

import html
import re
from functools import wraps
from flask import request, abort


def sanitize_html(text):
    """Escape HTML entities to prevent XSS"""
    if text is None:
        return None
    return html.escape(str(text))


def sanitize_input(data):
    """Recursively sanitize input data"""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        return sanitize_html(data)
    return data


def strip_tags(text):
    """Remove all HTML tags from text"""
    if text is None:
        return None
    clean = re.compile('<.*?>')
    return re.sub(clean, '', str(text))


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
