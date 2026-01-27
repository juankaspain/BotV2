# -*- coding: utf-8 -*-
"""
Validation Models Module
Provides Pydantic models for input validation
"""

from typing import Optional, Any
from pydantic import BaseModel, Field, validator
import re


class LoginRequest(BaseModel):
    """Login request validation model"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v.strip()


class AnnotationCreate(BaseModel):
    """Annotation creation validation model"""
    chart_id: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1, max_length=1000)
    x: Optional[float] = None
    y: Optional[float] = None
    type: str = Field(default='text', pattern=r'^(text|line|arrow|box)$')
    color: Optional[str] = Field(default='#000000', pattern=r'^#[0-9A-Fa-f]{6}$')
    
    @validator('text')
    def sanitize_text(cls, v):
        # Basic XSS prevention
        return v.replace('<', '&lt;').replace('>', '&gt;')


def validate_input(model_class: type, data: dict) -> Any:
    """Validate input data against a Pydantic model"""
    return model_class(**data)
