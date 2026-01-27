"""
Routes Module for Dashboard

Provides all route blueprints for the dashboard web application.
"""

from .additional_endpoints import additional_bp
from .ai_routes import ai_bp
from .api_v7_4_routes import api_v7_4_bp
from .control_routes import control_bp
from .metrics_routes import metrics_bp
from .monitoring_routes import monitoring_bp
from .strategy_routes import strategy_bp

__all__ = [
    'additional_bp',
    'ai_bp',
    'api_v7_4_bp',
    'control_bp',
    'metrics_bp',
    'monitoring_bp',
    'strategy_bp',
]
