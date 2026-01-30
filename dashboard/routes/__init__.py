"""
Routes Module for Dashboard

Provides all route blueprints for the dashboard web application.
Uses safe imports with fallback to avoid startup failures.
"""

import logging

logger = logging.getLogger(__name__)

# Safe imports with fallbacks
__all__ = []

# Dashboard API
try:
    from .dashboard_api import dashboard_api_bp
    __all__.append('dashboard_api_bp')
except ImportError as e:
    logger.warning(f"Could not import dashboard_api: {e}")
    dashboard_api_bp = None

# Additional endpoints
try:
    from .additional_endpoints import additional_bp
    __all__.append('additional_bp')
except ImportError as e:
    logger.warning(f"Could not import additional_endpoints: {e}")
    additional_bp = None

# AI routes
try:
    from .ai_routes import ai_bp
    __all__.append('ai_bp')
except ImportError as e:
    logger.warning(f"Could not import ai_routes: {e}")
    ai_bp = None

# API v7.4 routes
try:
    from .api_v7_4_routes import api_v7_4_bp
    __all__.append('api_v7_4_bp')
except ImportError as e:
    logger.warning(f"Could not import api_v7_4_routes: {e}")
    api_v7_4_bp = None

# Control routes
try:
    from .control_routes import control_bp
    __all__.append('control_bp')
except ImportError as e:
    logger.warning(f"Could not import control_routes: {e}")
    control_bp = None

# Metrics routes
try:
    from .metrics_routes import metrics_bp
    __all__.append('metrics_bp')
except ImportError as e:
    logger.warning(f"Could not import metrics_routes: {e}")
    metrics_bp = None

# Monitoring routes
try:
    from .monitoring_routes import monitoring_bp
    __all__.append('monitoring_bp')
except ImportError as e:
    logger.warning(f"Could not import monitoring_routes: {e}")
    monitoring_bp = None

# Strategy routes
try:
    from .strategy_routes import strategy_bp
    __all__.append('strategy_bp')
except ImportError as e:
    logger.warning(f"Could not import strategy_routes: {e}")
    strategy_bp = None

# Portfolio routes (NEW v7.7)
try:
    from .portfolio_routes import portfolio_bp
    __all__.append('portfolio_bp')
except ImportError as e:
    logger.warning(f"Could not import portfolio_routes: {e}")
    portfolio_bp = None

# Trade History routes (NEW v7.7)
try:
    from .trade_history_routes import trade_history_bp
    __all__.append('trade_history_bp')
except ImportError as e:
    logger.warning(f"Could not import trade_history_routes: {e}")
    trade_history_bp = None

# Performance routes (NEW v7.7)
try:
    from .performance_routes import performance_bp
    __all__.append('performance_bp')
except ImportError as e:
    logger.warning(f"Could not import performance_routes: {e}")
    performance_bp = None


def get_available_blueprints():
    """Get list of successfully loaded blueprints"""
    blueprints = []
    
    if dashboard_api_bp is not None:
        blueprints.append(('dashboard_api', dashboard_api_bp))
    if additional_bp is not None:
        blueprints.append(('additional', additional_bp))
    if ai_bp is not None:
        blueprints.append(('ai', ai_bp))
    if api_v7_4_bp is not None:
        blueprints.append(('api_v7_4', api_v7_4_bp))
    if control_bp is not None:
        blueprints.append(('control', control_bp))
    if metrics_bp is not None:
        blueprints.append(('metrics', metrics_bp))
    if monitoring_bp is not None:
        blueprints.append(('monitoring', monitoring_bp))
    if strategy_bp is not None:
        blueprints.append(('strategy', strategy_bp))
    if portfolio_bp is not None:
        blueprints.append(('portfolio', portfolio_bp))
    if trade_history_bp is not None:
        blueprints.append(('trade_history', trade_history_bp))
    if performance_bp is not None:
        blueprints.append(('performance', performance_bp))
    
    return blueprints


def register_all_blueprints(app):
    """Register all available blueprints with Flask app"""
    blueprints = get_available_blueprints()
    
    for name, bp in blueprints:
        try:
            app.register_blueprint(bp)
            logger.info(f"✓ Registered blueprint: {name}")
        except Exception as e:
            logger.error(f"✗ Failed to register {name}: {e}")
    
    logger.info(f"Registered {len(blueprints)} route blueprints")
    return len(blueprints)
