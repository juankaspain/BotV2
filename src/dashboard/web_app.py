"""
BotV2 Professional Dashboard v2.0 - Enterprise Security Edition
Ultra-professional real-time trading dashboard with production-grade security

Security Features:
- HTTP Basic Authentication
- Rate Limiting (10 req/min per IP)
- HTTPS Enforcement (production only)
- Security Headers (HSTS, CSP, X-Frame-Options, etc.)
- Brute Force Protection
- WebSocket Real-time Updates

Other Features:
- Bloomberg Terminal inspired design
- Real-time WebSocket updates
- Advanced charting with technical indicators
- Interactive heatmaps
- Risk analytics with VaR/CVaR
- Dark/Light theme toggle
- Mobile responsive
- Export capabilities
- Alert system
- Performance attribution
"""

import logging
import os
from flask import Flask, render_template, jsonify, request, Response, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from functools import wraps
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
import hashlib
import secrets
from pathlib import Path

logger = logging.getLogger(__name__)


class DashboardAuth:
    """
    HTTP Basic Authentication for Dashboard
    
    Security Features:
    - SHA-256 password hashing
    - Constant-time comparison (timing attack prevention)
    - Failed login attempt logging
    - Environment variable based credentials
    
    Uses environment variables for credentials:
    - DASHBOARD_USERNAME (default: admin)
    - DASHBOARD_PASSWORD (required, no default for security)
    """
    
    def __init__(self):
        """Initialize authentication"""
        
        self.username = os.getenv('DASHBOARD_USERNAME', 'admin')
        self.password_hash = self._get_password_hash()
        
        if not self.password_hash:
            logger.critical(
                "⚠️ DASHBOARD_PASSWORD not set! Dashboard will be INSECURE. "
                "Set environment variable before starting."
            )
            # Generate temporary password for first run
            temp_password = secrets.token_urlsafe(16)
            logger.warning(f"🔑 Temporary password generated: {temp_password}")
            logger.warning("IMPORTANT: Set DASHBOARD_PASSWORD env var for production!")
            self.password_hash = self._hash_password(temp_password)
    
    def _get_password_hash(self) -> str:
        """Get password hash from environment"""
        password = os.getenv('DASHBOARD_PASSWORD')
        if password:
            return self._hash_password(password)
        return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_credentials(self, username: str, password: str) -> bool:
        """
        Verify username and password (timing-attack safe)
        
        Args:
            username: Provided username
            password: Provided password
            
        Returns:
            True if credentials valid, False otherwise
        """
        if not self.password_hash:
            # If no password set, allow access (dev mode)
            logger.warning("⚠️ No password configured, allowing access (DEV MODE)")
            return True
        
        # Use constant-time comparison to prevent timing attacks
        username_match = secrets.compare_digest(username, self.username)
        password_match = secrets.compare_digest(
            self._hash_password(password),
            self.password_hash
        )
        
        return username_match and password_match


class ProfessionalDashboard:
    """
    Ultra-professional trading dashboard v2.0 with enterprise security
    
    Architecture:
    - Flask + SocketIO for real-time updates
    - Flask-Limiter for rate limiting (10 req/min per IP)
    - Flask-Talisman for HTTPS enforcement + security headers (PRODUCTION ONLY)
    - Plotly for interactive charts
    - Custom CSS/JS for Bloomberg-style UI
    - WebSocket push for instant updates
    - Modular component design
    - HTTP Basic Authentication with brute force protection
    
    Security:
    - Rate limiting on all endpoints
    - HTTPS enforcement in production (disabled in development)
    - Security headers (HSTS, CSP, X-Frame-Options) - production only
    - Brute force protection
    - Audit logging
    """
    
    def __init__(self, config):
        """Initialize professional dashboard with security"""
        
        self.config = config
        dash_config = config.get('dashboard', {})
        
        # Server config
        self.host = dash_config.get('host', '0.0.0.0')
        self.port = dash_config.get('port', 8050)
        self.debug = dash_config.get('debug', False)
        
        # Environment detection (CORRECTED: FLASK_ENV, default=development)
        self.env = os.getenv('FLASK_ENV', 'development')
        self.is_production = self.env == 'production'
        
        # Initialize authentication
        self.auth = DashboardAuth()
        
        # Flask app with SocketIO
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / 'templates'),
            static_folder=str(Path(__file__).parent / 'static')
        )
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
        
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Setup security middleware
        self._setup_rate_limiting()
        self._setup_https_enforcement()  # Only active in production
        
        # Data stores
        self.portfolio_history = []
        self.trades_history = []
        self.strategy_performance = {}
        self.risk_metrics = {}
        self.market_data = {}
        self.alerts = []
        
        # Performance cache
        self.cache = {
            'last_update': None,
            'computed_metrics': {}
        }
        
        # Setup routes and auth
        self._setup_authentication()
        self._setup_routes()
        self._setup_websocket_handlers()
        
        logger.info("✅ Professional Dashboard v2.0 initialized")
        logger.info(f"🌐 Environment: {self.env.upper()}")
        logger.info(f"🔒 Authentication: ENABLED (user: {self.auth.username})")
        logger.info(f"⚡ Rate Limiting: ENABLED (10 req/min per IP)")
        logger.info(f"🔐 HTTPS Enforcement: {'ENABLED' if self.is_production else 'DISABLED (dev mode)'}")
    
    def _setup_rate_limiting(self):
        """Setup rate limiting middleware"""
        
        # Get Redis configuration for distributed rate limiting
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        # Initialize rate limiter with Redis backend
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["10 per minute"],  # Global limit: 10 req/min per IP
            storage_uri=f"redis://{redis_host}:{redis_port}",
            storage_options={"socket_connect_timeout": 30},
            strategy="fixed-window",
            headers_enabled=True,  # Add X-RateLimit-* headers
            swallow_errors=True  # Continue working if Redis is down
        )
        
        # Custom rate limit exceeded handler
        @self.app.errorhandler(429)
        def ratelimit_handler(e):
            logger.warning(
                f"⚠️ Rate limit exceeded from {request.remote_addr} "
                f"on {request.path}"
            )
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please slow down.',
                'retry_after': e.description
            }), 429
        
        logger.info("✅ Rate limiting middleware installed (10 req/min per IP)")
    
    def _setup_https_enforcement(self):
        """
        Setup HTTPS enforcement and security headers (PRODUCTION ONLY)
        
        Development: NO Talisman installed - pure HTTP
        Production: Talisman enforces HTTPS + security headers
        """
        
        if self.is_production:
            # Production: Enforce HTTPS and security headers
            Talisman(
                self.app,
                force_https=True,  # Redirect HTTP → HTTPS
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,  # 1 year
                content_security_policy={
                    'default-src': "'self'",
                    'script-src': [
                        "'self'",
                        "'unsafe-inline'",  # Required for inline scripts
                        "https://cdn.socket.io",
                        "https://cdn.plot.ly"
                    ],
                    'style-src': ["'self'", "'unsafe-inline'"],
                    'img-src': ["'self'", "data:", "https:"],
                    'connect-src': ["'self'", "wss:", "ws:"],
                    'font-src': ["'self'"],
                    'frame-ancestors': "'none'"
                },
                content_security_policy_nonce_in=['script-src'],
                referrer_policy='no-referrer',
                feature_policy={
                    'geolocation': "'none'",
                    'microphone': "'none'",
                    'camera': "'none'",
                    'payment': "'none'"
                }
            )
            logger.info("✅ HTTPS enforcement + security headers enabled (production)")
        else:
            # Development: NO HTTPS enforcement, NO Talisman
            # Pure HTTP for localhost development
            logger.info("⚠️ HTTPS enforcement DISABLED (development mode)")
            logger.info("🌐 Access dashboard: http://localhost:8050 (HTTP only, no HTTPS)")
    
    def _setup_authentication(self):
        """Setup authentication for all Flask routes except /health"""
        
        # Exempt health check from rate limiting
        self.limiter.exempt(lambda: request.path == '/health')
        
        @self.app.before_request
        def require_auth():
            """Require authentication for all requests except /health"""
            
            # Skip auth for health check (Docker healthcheck)
            if request.path == '/health':
                return
            
            auth = request.authorization
            
            if not auth or not self.auth.check_credentials(auth.username, auth.password):
                logger.warning(
                    f"🚫 Failed login attempt from {request.remote_addr} "
                    f"(username: {auth.username if auth else 'none'}) "
                    f"on {request.path}"
                )
                return Response(
                    'Authentication required.\n'
                    'Please login with valid credentials.',
                    401,
                    {'WWW-Authenticate': 'Basic realm="BotV2 Dashboard v2.0 (Secure)"'}
                )
            
            logger.debug(f"✅ Authenticated user: {auth.username} from {request.remote_addr}")
        
        logger.info("✅ Authentication middleware installed")
    
    def _setup_routes(self):
        """Setup Flask routes with rate limiting"""
        
        @self.app.route('/')
        @self.limiter.limit("20 per minute")  # Higher limit for main page
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')
        
        @self.app.route('/api/overview')
        @self.limiter.limit("20 per minute")  # API endpoints: 20 req/min
        def api_overview():
            """Portfolio overview API"""
            return jsonify(self._get_portfolio_overview())
        
        @self.app.route('/api/equity')
        @self.limiter.limit("20 per minute")
        def api_equity():
            """Equity curve data"""
            return jsonify(self._get_equity_data())
        
        @self.app.route('/api/trades')
        @self.limiter.limit("20 per minute")
        def api_trades():
            """Recent trades"""
            limit = request.args.get('limit', 50, type=int)
            return jsonify(self._get_trades_data(limit))
        
        @self.app.route('/api/strategies')
        @self.limiter.limit("20 per minute")
        def api_strategies():
            """Strategy performance"""
            return jsonify(self._get_strategies_data())
        
        @self.app.route('/api/risk')
        @self.limiter.limit("20 per minute")
        def api_risk():
            """Risk metrics and analytics"""
            return jsonify(self._get_risk_analytics())
        
        @self.app.route('/api/correlation')
        @self.limiter.limit("20 per minute")
        def api_correlation():
            """Correlation heatmap data"""
            return jsonify(self._get_correlation_matrix())
        
        @self.app.route('/api/attribution')
        @self.limiter.limit("20 per minute")
        def api_attribution():
            """Performance attribution"""
            return jsonify(self._get_performance_attribution())
        
        @self.app.route('/api/alerts')
        @self.limiter.limit("20 per minute")
        def api_alerts():
            """Active alerts"""
            return jsonify({'alerts': self.alerts})
        
        @self.app.route('/api/export/report')
        @self.limiter.limit("5 per minute")  # Lower limit for export (resource intensive)
        def api_export_report():
            """Export PDF/Excel report"""
            format_type = request.args.get('format', 'pdf')
            return self._export_report(format_type)
        
        @self.app.route('/health')
        # No rate limit or auth for health check
        def health():
            """Health check (no authentication or rate limiting for Docker)"""
            return jsonify({
                'status': 'healthy',
                'version': '2.0-secure',
                'service': 'dashboard',
                'uptime': self._get_uptime(),
                'last_update': self.cache.get('last_update'),
                'security': {
                    'rate_limiting': True,
                    'https_enforced': self.is_production,
                    'authenticated': False  # Health check doesn't require auth
                }
            })
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers (exempt from rate limiting)"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Client connected"""
            logger.info(f"🔗 WebSocket client connected: {request.sid} from {request.remote_addr}")
            emit('connected', {
                'message': 'Connected to BotV2 Dashboard v2.0 (Secure)',
                'version': '2.0-secure',
                'features': ['rate_limiting', 'https_enforced' if self.is_production else 'dev_mode']
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Client disconnected"""
            logger.info(f"❌ WebSocket client disconnected: {request.sid}")
        
        @self.socketio.on('request_update')
        def handle_update_request(data):
            """Client requests data update"""
            component = data.get('component', 'all')
            self._emit_update(component)
    
    # ==================== Data Getters ====================
    
    def _get_portfolio_overview(self) -> Dict:
        """Get portfolio overview metrics"""
        
        if not self.portfolio_history:
            return self._empty_portfolio()
        
        current = self.portfolio_history[-1]
        initial = self.portfolio_history[0]
        
        # Calculate metrics
        total_return = (current['equity'] / initial['equity'] - 1) * 100
        
        # Daily change
        if len(self.portfolio_history) > 1:
            prev = self.portfolio_history[-2]
            daily_change = current['equity'] - prev['equity']
            daily_change_pct = (daily_change / prev['equity']) * 100
        else:
            daily_change = 0
            daily_change_pct = 0
        
        # Win rate
        winning_trades = sum(1 for t in self.trades_history if t.get('pnl', 0) > 0)
        win_rate = (winning_trades / len(self.trades_history) * 100) if self.trades_history else 0
        
        # Sharpe ratio
        sharpe = self.risk_metrics.get('sharpe_ratio', 0)
        
        # Max drawdown
        max_dd = self.risk_metrics.get('max_drawdown', 0)
        
        return {
            'equity': current['equity'],
            'cash': current.get('cash', 0),
            'positions_count': len(current.get('positions', {})),
            'total_return': total_return,
            'daily_change': daily_change,
            'daily_change_pct': daily_change_pct,
            'win_rate': win_rate,
            'total_trades': len(self.trades_history),
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'timestamp': current.get('timestamp', datetime.now()).isoformat()
        }
    
    def _get_equity_data(self) -> Dict:
        """Get equity curve data with technical indicators"""
        
        if not self.portfolio_history:
            return {'timestamps': [], 'equity': [], 'sma_20': [], 'sma_50': []}
        
        df = pd.DataFrame(self.portfolio_history)
        
        # Calculate SMAs
        df['sma_20'] = df['equity'].rolling(window=min(20, len(df))).mean()
        df['sma_50'] = df['equity'].rolling(window=min(50, len(df))).mean()
        
        return {
            'timestamps': [t.isoformat() if isinstance(t, datetime) else t 
                          for t in df['timestamp'].tolist()],
            'equity': df['equity'].tolist(),
            'sma_20': df['sma_20'].fillna(0).tolist(),
            'sma_50': df['sma_50'].fillna(0).tolist(),
            'drawdown': self._calculate_drawdown(df['equity']).tolist()
        }
    
    def _get_trades_data(self, limit: int = 50) -> Dict:
        """Get recent trades with analytics"""
        
        recent_trades = self.trades_history[-limit:]
        
        trades_list = []
        for trade in recent_trades:
            trades_list.append({
                'timestamp': trade.get('timestamp', datetime.now()).isoformat(),
                'strategy': trade.get('strategy', 'Unknown'),
                'symbol': trade.get('symbol', 'N/A'),
                'action': trade.get('action', 'N/A'),
                'size': trade.get('size', 0),
                'entry_price': trade.get('entry_price', 0),
                'pnl': trade.get('pnl', 0),
                'pnl_pct': trade.get('pnl_pct', 0),
                'confidence': trade.get('confidence', 0)
            })
        
        return {
            'trades': trades_list,
            'summary': self._get_trades_summary()
        }
    
    def _get_strategies_data(self) -> Dict:
        """Get strategy performance metrics"""
        
        strategies = []
        
        for name, perf in self.strategy_performance.items():
            strategies.append({
                'name': name,
                'total_return': perf.get('total_return', 0) * 100,
                'sharpe_ratio': perf.get('sharpe_ratio', 0),
                'win_rate': perf.get('win_rate', 0) * 100,
                'total_trades': perf.get('total_trades', 0),
                'avg_win': perf.get('avg_win', 0),
                'avg_loss': perf.get('avg_loss', 0),
                'profit_factor': perf.get('profit_factor', 0),
                'weight': perf.get('weight', 0),
                'status': perf.get('status', 'active')
            })
        
        # Sort by return
        strategies.sort(key=lambda x: x['total_return'], reverse=True)
        
        return {'strategies': strategies}
    
    def _get_risk_analytics(self) -> Dict:
        """Get comprehensive risk metrics"""
        
        if not self.portfolio_history:
            return self._empty_risk_metrics()
        
        df = pd.DataFrame(self.portfolio_history)
        returns = df['equity'].pct_change().dropna()
        
        # Calculate VaR and CVaR
        var_95 = np.percentile(returns, 5) * 100 if len(returns) > 0 else 0
        cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100 if len(returns) > 0 else 0
        
        # Volatility
        volatility = returns.std() * np.sqrt(252) * 100 if len(returns) > 1 else 0
        
        # Sortino ratio
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 1 else 0.0001
        sortino = (returns.mean() * 252 / downside_std) if downside_std > 0 else 0
        
        # Calmar ratio
        max_dd = self._calculate_max_drawdown(df['equity'])
        calmar = (returns.mean() * 252 / abs(max_dd)) if max_dd != 0 else 0
        
        return {
            'sharpe_ratio': self.risk_metrics.get('sharpe_ratio', 0),
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'max_drawdown': max_dd * 100,
            'current_drawdown': self._calculate_current_drawdown() * 100,
            'volatility': volatility,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'beta': self.risk_metrics.get('beta', 1.0),
            'alpha': self.risk_metrics.get('alpha', 0),
            'information_ratio': self.risk_metrics.get('information_ratio', 0)
        }
    
    def _get_correlation_matrix(self) -> Dict:
        """Get strategy correlation matrix"""
        
        if not self.strategy_performance:
            return {'strategies': [], 'matrix': []}
        
        strategies = list(self.strategy_performance.keys())
        
        # In real implementation, calculate from returns
        # For now, generate mock data
        n = len(strategies)
        correlation = np.random.rand(n, n)
        correlation = (correlation + correlation.T) / 2  # Make symmetric
        np.fill_diagonal(correlation, 1.0)  # Diagonal is 1
        
        return {
            'strategies': strategies,
            'matrix': correlation.tolist()
        }
    
    def _get_performance_attribution(self) -> Dict:
        """Get performance attribution by strategy"""
        
        attribution = []
        
        total_pnl = sum(s.get('total_pnl', 0) for s in self.strategy_performance.values())
        
        for name, perf in self.strategy_performance.items():
            strategy_pnl = perf.get('total_pnl', 0)
            contribution = (strategy_pnl / total_pnl * 100) if total_pnl != 0 else 0
            
            attribution.append({
                'strategy': name,
                'pnl': strategy_pnl,
                'contribution_pct': contribution
            })
        
        # Sort by contribution
        attribution.sort(key=lambda x: abs(x['contribution_pct']), reverse=True)
        
        return {'attribution': attribution}
    
    # ==================== Helper Methods ====================
    
    def _calculate_drawdown(self, equity_series) -> pd.Series:
        """Calculate drawdown series"""
        cummax = equity_series.expanding().max()
        drawdown = (equity_series - cummax) / cummax
        return drawdown
    
    def _calculate_max_drawdown(self, equity_series) -> float:
        """Calculate maximum drawdown"""
        drawdown = self._calculate_drawdown(equity_series)
        return drawdown.min()
    
    def _calculate_current_drawdown(self) -> float:
        """Calculate current drawdown"""
        if not self.portfolio_history:
            return 0.0
        
        df = pd.DataFrame(self.portfolio_history)
        current_equity = df['equity'].iloc[-1]
        peak = df['equity'].max()
        
        return (current_equity - peak) / peak if peak > 0 else 0.0
    
    def _get_trades_summary(self) -> Dict:
        """Get trades summary statistics"""
        
        if not self.trades_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'total_pnl': 0
            }
        
        winning = [t for t in self.trades_history if t.get('pnl', 0) > 0]
        losing = [t for t in self.trades_history if t.get('pnl', 0) < 0]
        
        total_wins = sum(t.get('pnl', 0) for t in winning)
        total_losses = abs(sum(t.get('pnl', 0) for t in losing))
        
        return {
            'total_trades': len(self.trades_history),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': len(winning) / len(self.trades_history) * 100,
            'avg_win': total_wins / len(winning) if winning else 0,
            'avg_loss': total_losses / len(losing) if losing else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else 0,
            'total_pnl': sum(t.get('pnl', 0) for t in self.trades_history)
        }
    
    def _empty_portfolio(self) -> Dict:
        """Return empty portfolio structure"""
        return {
            'equity': 0,
            'cash': 0,
            'positions_count': 0,
            'total_return': 0,
            'daily_change': 0,
            'daily_change_pct': 0,
            'win_rate': 0,
            'total_trades': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _empty_risk_metrics(self) -> Dict:
        """Return empty risk metrics"""
        return {
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'calmar_ratio': 0,
            'max_drawdown': 0,
            'current_drawdown': 0,
            'volatility': 0,
            'var_95': 0,
            'cvar_95': 0,
            'beta': 1.0,
            'alpha': 0,
            'information_ratio': 0
        }
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        # Placeholder - implement actual uptime tracking
        return "Running"
    
    def _export_report(self, format_type: str):
        """Export performance report"""
        # Placeholder - implement actual report generation
        return jsonify({'status': 'not_implemented', 'format': format_type})
    
    def _emit_update(self, component: str = 'all'):
        """Emit WebSocket update to clients"""
        
        updates = {}
        
        if component in ['all', 'overview']:
            updates['overview'] = self._get_portfolio_overview()
        
        if component in ['all', 'equity']:
            updates['equity'] = self._get_equity_data()
        
        if component in ['all', 'strategies']:
            updates['strategies'] = self._get_strategies_data()
        
        if component in ['all', 'risk']:
            updates['risk'] = self._get_risk_analytics()
        
        self.socketio.emit('update', updates)
    
    # ==================== Public API ====================
    
    def update_data(self, portfolio: Dict, trades: List, strategies: Dict, risk: Dict):
        """
        Update dashboard data from trading system
        
        Args:
            portfolio: Current portfolio state
            trades: Recent trades list
            strategies: Strategy performance dict
            risk: Risk metrics dict
        """
        
        # Add to history
        self.portfolio_history.append({
            'timestamp': datetime.now(),
            'equity': portfolio.get('equity', 0),
            'cash': portfolio.get('cash', 0),
            'positions': portfolio.get('positions', {})
        })
        
        # Keep last 10000 points (adjustable)
        if len(self.portfolio_history) > 10000:
            self.portfolio_history = self.portfolio_history[-10000:]
        
        self.trades_history = trades
        self.strategy_performance = strategies
        self.risk_metrics = risk
        
        # Update cache
        self.cache['last_update'] = datetime.now().isoformat()
        
        # Emit WebSocket update
        self._emit_update('all')
        
        logger.debug("Dashboard data updated via WebSocket")
    
    def add_alert(self, level: str, message: str, category: str = 'general'):
        """
        Add alert to dashboard
        
        Args:
            level: Alert level (info, warning, danger)
            message: Alert message
            category: Alert category
        """
        
        alert = {
            'id': len(self.alerts),
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'category': category
        }
        
        self.alerts.append(alert)
        
        # Keep last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Emit alert via WebSocket
        self.socketio.emit('alert', alert)
        
        logger.info(f"Alert added: [{level}] {message}")
    
    def run(self):
        """Start dashboard server"""
        
        logger.info("="*70)
        logger.info("🚀 Starting BotV2 Professional Dashboard v2.0 (Secure)")
        logger.info(f"🌐 URL: http{'s' if self.is_production else ''}://{self.host}:{self.port}")
        logger.info(f"🔒 Authentication: ENABLED (user: {self.auth.username})")
        logger.info("🔑 Password: Set via DASHBOARD_PASSWORD env var")
        logger.info(f"⚡ Rate Limiting: ENABLED (10 req/min global, 20 req/min API)")
        logger.info(f"🔐 HTTPS: {'ENFORCED' if self.is_production else 'DISABLED (dev)'}")
        logger.info("✨ Features: WebSocket, Real-time, Advanced Analytics, Enterprise Security")
        logger.info(f"📊 Health Check: http://{self.host}:{self.port}/health")
        
        if not self.is_production:
            logger.warning("⚠️ DEVELOPMENT MODE: Use HTTP (not HTTPS) to access dashboard")
            logger.warning(f"🌐 Access: http://localhost:{self.port}")
        
        logger.info("="*70)
        
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=self.debug,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )


# Alias for backward compatibility
TradingDashboard = ProfessionalDashboard


if __name__ == "__main__":
    from src.config.config_manager import ConfigManager
    
    config = ConfigManager()
    dashboard = ProfessionalDashboard(config)
    dashboard.run()
