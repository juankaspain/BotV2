# -*- coding: utf-8 -*-
"""
Input Validator Module
Provides input validation functionality
"""

import re
from functools import wraps
from flask import request, abort, jsonify


class InputValidator:
    """Input validation class"""
    
    def __init__(self):
        self.rules = {}
    
    def add_rule(self, field, rule_func, error_msg=None):
        """Add validation rule for a field"""
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append((rule_func, error_msg))
    
    def validate(self, data):
        """Validate data against rules"""
        errors = []
        for field, rules in self.rules.items():
            value = data.get(field)
            for rule_func, error_msg in rules:
                if not rule_func(value):
                    errors.append(error_msg or f'Invalid value for {field}')
        return len(errors) == 0, errors
    
    @staticmethod
    def is_email(value):
        """Check if value is valid email"""
        if value is None:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(value)))
    
    @staticmethod
    def is_not_empty(value):
        """Check if value is not empty"""
        return value is not None and str(value).strip() != ''
    
    @staticmethod
    def is_numeric(value):
        """Check if value is numeric"""
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def min_length(length):
        """Return function to check minimum length"""
        def check(value):
            return value is not None and len(str(value)) >= length
        return check
    
    @staticmethod
    def max_length(length):
        """Return function to check maximum length"""
        def check(value):
            return value is None or len(str(value)) <= length
        return check


def validate_input(rules):
    """Decorator for input validation"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() or request.form.to_dict()
            validator = InputValidator()
            for field, rule_list in rules.items():
                for rule in rule_list:
                    validator.add_rule(field, rule['func'], rule.get('msg'))
            is_valid, errors = validator.validate(data)
            if not is_valid:
                return jsonify({'errors': errors}), 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator
