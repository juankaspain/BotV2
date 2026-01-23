"""BotV2 Professional Dashboard v4.4 - Strategy Editor Edition
Ultra-professional real-time trading dashboard with production-grade security

Security Features:
- Session-Based Authentication (no HTTP Basic popup)
- Rate Limiting (10 req/min per IP)
- HTTPS Enforcement (production only)
- Security Headers (HSTS, CSP, X-Frame-Options, etc.)
- Brute Force Protection with account lockout
- WebSocket Real-time Updates
- Professional Audit Logging (JSON structured)

Features:
- Enterprise-grade design (Bloomberg Terminal + TradingView inspired)
- Real-time WebSocket updates
- Advanced charting with Plotly themes
- Interactive analytics dashboard
- Risk analytics with VaR/CVaR
- 3 Professional themes (Dark, Light, Bloomberg)
- Mobile responsive
- Export capabilities
- Alert system
- Performance attribution
- Control Panel v4.2 (Bot management)
- 📊 Live Monitoring v4.3 (Real-time visibility)
- ✏️ Strategy Editor v4.4 (Parameter tuning without code)
"""

import logging
import logging.handlers
import os
import json
from flask import Flask, render_template, jsonify, request, Response, send_file, session, redirect, url_for
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
import hashlib
import secrets
from pathlib import Path
from collections import defaultdict

# ==================== CONTROL PANEL IMPORT ====================
from .control_routes import control_bp

# ==================== LIVE MONITORING IMPORT ====================
from .monitoring_routes import monitoring_bp

# ==================== STRATEGY EDITOR IMPORT ====================
from .strategy_routes import strategy_bp

# Dashboard version
__version__ = '4.4'

# Setup structured logging
logger = logging.getLogger(__name__)


# Suppress verbose flask-limiter error logging
limiter_logger = logging.getLogger('flask-limiter')
limiter_logger.setLevel(logging.CRITICAL)


class SecurityAuditLogger:
    """Professional security audit logger with JSON structured output
    
    Features:
    - JSON structured logs for SIEM integration
    - Automatic log rotation
    - Separate security audit trail
    - Compatible with Splunk, ELK, Datadog
    """
    
    def __init__(self, log_file: str = 'logs/security_audit.log'):
        """Initialize security audit logger"""
        
        # Create logs directory
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Setup rotating file handler (10MB per file, keep 10 backups)
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        )
        
        # JSON formatter
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, level: str, **kwargs):
        """Log security event in JSON format
        
        Args:
            event_type: Event type (e.g., 'auth.login.success')
            level: Log level (INFO, WARNING, ERROR)
            **kwargs: Additional fields
        """
        
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'event_type': event_type,
            **kwargs
        }
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(log_entry))


class DashboardAuth:
    """Session-Based Authentication for Dashboard
    
    Security Features:
    - SHA-256 password hashing
    - Constant-time comparison (timing attack prevention)
    - Failed login attempt tracking
    - Account lockout after 5 failed attempts
    - Lockout duration: 5 minutes
    - Session management with secure cookies
    - Professional audit logging
    
    Uses environment variables for credentials:
    - DASHBOARD_USERNAME (default: admin)
    - DASHBOARD_PASSWORD (required, no default for security)
    """
    
    def __init__(self, audit_logger: SecurityAuditLogger):
        """Initialize authentication"""
        
        self.username = os.getenv('DASHBOARD_USERNAME', 'admin')
        self.password_hash = self._get_password_hash()
        self.audit_logger = audit_logger
        
        # Failed login attempts tracking (IP -> count, last_attempt)
        self.failed_attempts = defaultdict(lambda: {'count': 0, 'last_attempt': None, 'locked_until': None})
        
        # Lockout configuration
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=5)
        
        if not self.password_hash:
            logger.critical(
                "SECURITY: DASHBOARD_PASSWORD not set! Dashboard will be INSECURE. "
                "Set environment variable before starting."
            )
            self.audit_logger.log_event(
                'auth.config.missing_password',
                'CRITICAL',
                message='DASHBOARD_PASSWORD not configured'
            )
            
            # Generate temporary password for first run
            temp_password = secrets.token_urlsafe(16)
            logger.warning(f"SECURITY: Temporary password generated: {temp_password}")
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
    
    def is_locked_out(self, ip: str) -> bool:
        """Check if IP is locked out
        
        Args:
            ip: Client IP address
            
        Returns:
            True if locked out, False otherwise
        """
        attempt_info = self.failed_attempts[ip]
        
        if attempt_info['locked_until']:
            if datetime.now() < attempt_info['locked_until']:
                return True
            else:
                # Lockout expired, reset
                attempt_info['count'] = 0
                attempt_info['locked_until'] = None
        
        return False
    
    def record_failed_attempt(self, ip: str, username: str):
        """Record failed login attempt
        
        Args:
            ip: Client IP address
            username: Attempted username
        """
        attempt_info = self.failed_attempts[ip]
        attempt_info['count'] += 1
        attempt_info['last_attempt'] = datetime.now()
        
        # Log failed attempt
        self.audit_logger.log_event(
            'auth.login.failed',
            'WARNING',
            user=username,
            ip=ip,
            failed_attempts=attempt_info['count'],
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
        
        # Check if should lock out
        if attempt_info['count'] >= self.max_attempts:
            attempt_info['locked_until'] = datetime.now() + self.lockout_duration
            
            self.audit_logger.log_event(
                'auth.account.locked',
                'ERROR',
                user=username,
                ip=ip,
                reason='too_many_failed_attempts',
                locked_until=attempt_info['locked_until'].isoformat(),
                total_attempts=attempt_info['count']
            )
            
            logger.error(
                f"SECURITY: Account locked for IP {ip} (user: {username}) "
                f"after {attempt_info['count']} failed attempts. "
                f"Locked until {attempt_info['locked_until'].isoformat()}"
            )
    
    def record_successful_login(self, ip: str, username: str):
        """Record successful login and reset failed attempts
        
        Args:
            ip: Client IP address
            username: Authenticated username
        """
        # Reset failed attempts
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
        
        # Log successful login
        self.audit_logger.log_event(
            'auth.login.success',
            'INFO',
            user=username,
            ip=ip,
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
        
        logger.info(f"✅ AUTH: Login successful - User: {username}, IP: {ip}")
    
    def check_credentials(self, username: str, password: str) -> bool:
        """Verify username and password (timing-attack safe)
        
        Args:
            username: Provided username
            password: Provided password
            
        Returns:
            True if credentials valid, False otherwise
        """
        if not self.password_hash:
            # If no password set, allow access (dev mode)
            logger.warning("SECURITY: No password configured, allowing access (DEV MODE)")
            return True
        
        # Use constant-time comparison to prevent timing attacks
        username_match = secrets.compare_digest(username, self.username)
        password_match = secrets.compare_digest(
            self._hash_password(password),
            self.password_hash
        )
        
        return username_match and password_match


class ProfessionalDashboard:
    """Ultra-professional trading dashboard v4.4 with Strategy Editor
    
    Architecture:
    - Flask + SocketIO for real-time updates
    - Flask-Limiter for rate limiting (10 req/min per IP)
    - Flask-Talisman for HTTPS enforcement + security headers (PRODUCTION ONLY)
    - Session-based authentication (no HTTP Basic popup)
    - Plotly for interactive charts with professional themes
    - Custom CSS/JS for enterprise-grade UI
    - WebSocket push for instant updates
    - Modular component design
    - Professional audit logging (JSON structured)
    - Control Panel v4.2 for bot management
    - Live Monitoring v4.3 for real-time visibility
    - Strategy Editor v4.4 for parameter tuning
    
    Security:
    - Rate limiting on all endpoints
    - HTTPS enforcement in production (disabled in development)
    - Security headers (HSTS, CSP, X-Frame-Options) - production only
    - Brute force protection with account lockout
    - Comprehensive audit logging
    - Session management with secure cookies
    """
    
    def __init__(self, config):
        """Initialize professional dashboard with security"""
        
        self.config = config
        dash_config = config.get('dashboard', {})
        
        # Server config
        self.host = dash_config.get('host', '0.0.0.0')
        self.port = dash_config.get('port', 8050)
        self.debug = dash_config.get('debug', False)
        
        # Environment detection
        self.env = os.getenv('FLASK_ENV', 'development')
        self.is_production = self.env == 'production'
        
        # Initialize security audit logger
        self.audit_logger = SecurityAuditLogger()
        
        # Initialize authentication
        self.auth = DashboardAuth(self.audit_logger)
        
        # Flask app with SocketIO
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / 'templates'),
            static_folder=str(Path(__file__).parent / 'static')
        )
        
        # Session configuration
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
        self.app.config['SESSION_COOKIE_SECURE'] = self.is_production  # HTTPS only in production
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # 30 min timeout
        
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Setup security middleware
        self.rate_limiter_storage = self._setup_rate_limiting()
        self._setup_https_enforcement()  # Only active in production
        
        # ==================== REGISTER BLUEPRINTS ====================
        self.app.register_blueprint(control_bp)
        self.app.register_blueprint(monitoring_bp)
        self.app.register_blueprint(strategy_bp)
        
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
        self._setup_routes()
        self._setup_websocket_handlers()
        
        # Consolidated startup logging
        self._log_startup_banner()
    
    def _setup_rate_limiting(self) -> str:
        """Setup rate limiting middleware with automatic fallback to memory"""
        
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_uri = f"redis://{redis_host}:{redis_port}"
        storage_type = "redis"
        
        # Try Redis first, fallback to memory if unavailable
        try:
            # Test Redis connection
            import redis
            r = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=1)
            r.ping()
            storage_uri = redis_uri
            storage_type = "redis"
        except Exception:
            # Redis not available, use memory storage
            storage_uri = "memory://"
            storage_type = "memory"
        
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["10 per minute"],
            storage_uri=storage_uri,
            storage_options={"socket_connect_timeout": 30},
            strategy="fixed-window",
            headers_enabled=True,
            swallow_errors=True
        )
        
        @self.app.errorhandler(429)
        def ratelimit_handler(e):
            self.audit_logger.log_event(
                'security.rate_limit.exceeded',
                'WARNING',
                ip=request.remote_addr,
                path=request.path,
                user_agent=request.headers.get('User-Agent', 'Unknown')
            )
            logger.warning(f"⚠️ SECURITY: Rate limit exceeded - IP: {request.remote_addr}, Path: {request.path}")
            
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please slow down.',
                'retry_after': e.description
            }), 429
        
        return storage_type
    
    def _setup_https_enforcement(self):
        """Setup HTTPS enforcement and security headers (PRODUCTION ONLY)"""
        
        if self.is_production:
            Talisman(
                self.app,
                force_https=True,
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,
                content_security_policy={
                    'default-src': "'self'",
                    'script-src': ["'self'", "'unsafe-inline'", "https://cdn.socket.io", "https://cdn.plot.ly", "https://fonts.googleapis.com"],
                    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
                    'img-src': ["'self'", "data:", "https:"],
                    'connect-src': ["'self'", "wss:", "ws:"],
                    'font-src': ["'self'", "https://fonts.gstatic.com"],
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
    
    def _log_startup_banner(self):
        """Log consolidated startup banner with all configuration"""
        
        # Log startup event to audit log
        self.audit_logger.log_event(
            'system.startup',
            'INFO',
            environment=self.env,
            version=__version__,
            features=['session_auth', 'rate_limiting', 'audit_logging', 'account_lockout', 'spa_navigation', '3_themes', 'control_panel_v4.2', 'live_monitoring_v4.3', 'strategy_editor_v4.4']
        )
        
        # Consolidated startup banner
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"        BotV2 Professional Dashboard v{__version__} - Strategy Editor Edition")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📊 SYSTEM CONFIGURATION")
        logger.info(f"   Environment:           {self.env.upper()}")
        logger.info(f"   Version:               {__version__}")
        logger.info(f"   URL:                   http{'s' if self.is_production else ''}://{self.host}:{self.port}")
        logger.info(f"   Dashboard:             http://{self.host}:{self.port}/dashboard")
        logger.info(f"   Control Panel:         http://{self.host}:{self.port}/control")
        logger.info(f"   Live Monitor:          http://{self.host}:{self.port}/monitoring")
        logger.info(f"   Strategy Editor:       http://{self.host}:{self.port}/api/strategies/")
        logger.info(f"   Health Check:          http://{self.host}:{self.port}/health")
        logger.info("")
        logger.info("🔒 SECURITY FEATURES")
        logger.info(f"   Authentication:        SESSION-BASED (user: {self.auth.username})")
        logger.info(f"   Password:              {'✓ Configured' if self.auth.password_hash else '✗ NOT SET'}")
        logger.info(f"   Rate Limiting:         ENABLED (storage: {self.rate_limiter_storage})")
        logger.info(f"   HTTPS Enforcement:     {'ENABLED' if self.is_production else 'DISABLED (dev)'}")
        logger.info(f"   Audit Logging:         ENABLED (logs/security_audit.log)")
        logger.info(f"   Account Lockout:       {self.auth.max_attempts} attempts / {self.auth.lockout_duration.seconds//60} min")
        logger.info("")
        logger.info("✨ FEATURES")
        logger.info("   • Enterprise-grade design (Bloomberg + TradingView inspired)")
        logger.info("   • Real-time WebSocket updates")
        logger.info("   • Advanced Plotly charts with professional themes")
        logger.info("   • Risk metrics (VaR, Sharpe, Sortino, Calmar)")
        logger.info("   • Strategy performance tracking")
        logger.info("   • 3 Professional themes (Dark, Light, Bloomberg)")
        logger.info("   • Single Page Application (SPA) navigation")
        logger.info("   • Glassmorphism UI effects")
        logger.info("   • Mobile responsive design")
        logger.info("   • 🏛️ Control Panel v4.2 (Bot management)")
        logger.info("   • 📊 Live Monitoring v4.3 (Real-time visibility)")
        logger.info("   • ✏️ Strategy Editor v4.4 (Parameter tuning without code)")
        logger.info("")
        
        if not self.is_production:
            logger.info("=" * 80)
            logger.info("                      ACCESS INFORMATION")
            logger.info("-" * 80)
            logger.info(f"  Login:    http://localhost:{self.port}/login")
            logger.info(f"  Username: {self.auth.username}")
            logger.info(f"  Password: {'(set via DASHBOARD_PASSWORD)' if self.auth.password_hash else 'NOT SET'}")
            logger.info("=" * 80)
            logger.info("")
    
    def login_required(self, f):
        """Decorator to require login for routes"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                self.audit_logger.log_event(
                    'auth.access.denied',
                    'WARNING',
                    ip=request.remote_addr,
                    path=request.path,
                    reason='no_session'
                )
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def _setup_routes(self):
        """Setup Flask routes with authentication and ALL API endpoints"""
        
        # ==================== Authentication Routes ====================
        
        @self.app.route('/login', methods=['GET', 'POST'])
        @self.limiter.limit("10 per minute")
        def login():
            """Login page and authentication endpoint"""
            
            if request.method == 'GET':
                # Show login page
                if 'user' in session:
                    return redirect(url_for('index'))
                return render_template('login.html')
            
            # POST: Process login
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            ip = request.remote_addr
            
            # Check if locked out
            if self.auth.is_locked_out(ip):
                lockout_info = self.auth.failed_attempts[ip]
                remaining = (lockout_info['locked_until'] - datetime.now()).seconds
                
                logger.warning(f"⚠️ SECURITY: Login attempt from locked IP: {ip}, User: {username}")
                return jsonify({
                    'error': 'Account locked',
                    'message': f'Too many failed attempts. Try again in {remaining} seconds.'
                }), 429
            
            # Verify credentials
            if self.auth.check_credentials(username, password):
                # Success
                session.permanent = True
                session['user'] = username
                session['login_time'] = datetime.now().isoformat()
                session['ip'] = ip
                
                self.auth.record_successful_login(ip, username)
                return jsonify({'success': True, 'redirect': '/'}), 200
            else:
                # Failed
                self.auth.record_failed_attempt(ip, username)
                return jsonify({
                    'error': 'Invalid credentials',
                    'message': 'Invalid username or password. Please try again.'
                }), 401
        
        @self.app.route('/logout')
        def logout():
            """Logout endpoint"""
            user = session.get('user', 'unknown')
            ip = request.remote_addr
            
            self.audit_logger.log_event(
                'auth.logout',
                'INFO',
                user=user,
                ip=ip
            )
            
            logger.info(f"👋 AUTH: User logged out - User: {user}, IP: {ip}")
            session.clear()
            return redirect(url_for('login'))
        
        # ==================== Dashboard Routes ====================
        
        @self.app.route('/')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html', user=session.get('user'))
        
        @self.app.route('/control')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def control_panel():
            """Control panel page v4.2"""
            return render_template('control.html', user=session.get('user'))
        
        # ==================== API ENDPOINTS - COMPLETE IMPLEMENTATION ====================
        
        @self.app.route('/api/section/<section>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_section_data(section):
            """Get data for specific dashboard section
            
            Sections:
            - dashboard: Overview with KPIs and main charts
            - portfolio: Portfolio positions and allocation
            - strategies: Strategy performance and statistics
            - risk: Risk metrics and analysis
            - trades: Trade history and statistics
            - settings: System settings and configuration
            """
            
            try:
                logger.debug(f"📊 API: Section data requested - {section}")
                
                if section == 'dashboard':
                    data = self._get_dashboard_data()
                elif section == 'portfolio':
                    data = self._get_portfolio_data()
                elif section == 'strategies':
                    data = self._get_strategies_data()
                elif section == 'risk':
                    data = self._get_risk_data()
                elif section == 'trades':
                    data = self._get_trades_data()
                elif section == 'settings':
                    data = self._get_settings_data()
                else:
                    return jsonify({'error': 'Unknown section', 'section': section}), 404
                
                return jsonify(data)
                
            except Exception as e:
                logger.error(f"❌ API Error in section {section}: {str(e)}")
                return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
        
        @self.app.route('/health')
        def health():
            """Health check (no authentication required for Docker)"""
            return jsonify({
                'status': 'healthy',
                'version': __version__,
                'service': 'dashboard',
                'uptime': self._get_uptime(),
                'last_update': self.cache.get('last_update'),
                'security': {
                    'auth_type': 'session',
                    'rate_limiting': True,
                    'rate_limiter_storage': self.rate_limiter_storage,
                    'https_enforced': self.is_production,
                    'audit_logging': True
                },
                'features': {
                    'spa_navigation': True,
                    'themes': ['dark', 'light', 'bloomberg'],
                    'charts': 'plotly',
                    'websocket': True,
                    'control_panel': 'v4.2',
                    'live_monitoring': 'v4.3',
                    'strategy_editor': 'v4.4'
                }
            })
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.debug(f"🔗 WEBSOCKET: Client connected - SID: {request.sid}, IP: {request.remote_addr}")
            emit('connected', {
                'message': f'Connected to BotV2 Dashboard v{__version__}',
                'version': __version__,
                'features': ['session_auth', 'rate_limiting', 'audit_logging', 'spa', '3_themes', 'control_panel_v4.2', 'live_monitoring_v4.3', 'strategy_editor_v4.4']
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.debug(f"❌ WEBSOCKET: Client disconnected - SID: {request.sid}")
        
        @self.socketio.on('request_update')
        def handle_update_request(data):
            component = data.get('component', 'all')
            self._emit_update(component)
    
    # ==================== DATA GENERATORS - MOCK DATA FOR DEVELOPMENT ====================
    
    def _get_dashboard_data(self) -> Dict:
        """Generate dashboard overview data"""
        
        # Generate timestamps for last 30 days
        now = datetime.now()
        timestamps = [(now - timedelta(days=30-i)).strftime('%Y-%m-%d') for i in range(30)]
        
        # Generate equity curve (simulated)
        initial_equity = 10000
        equity = [initial_equity]
        for _ in range(29):
            change = np.random.normal(0.002, 0.015)  # 0.2% mean, 1.5% std
            equity.append(equity[-1] * (1 + change))
        
        return {
            'overview': {
                'equity': f'€{equity[-1]:,.2f}',
                'daily_change': equity[-1] - equity[-2],
                'daily_change_pct': f'{((equity[-1] / equity[-2]) - 1) * 100:.2f}',
                'total_pnl': f'€{equity[-1] - initial_equity:,.2f}',
                'total_return': f'{((equity[-1] / initial_equity) - 1) * 100:.2f}',
                'win_rate': '65.4',
                'total_trades': 127,
                'sharpe_ratio': '1.85',
                'max_drawdown': '-8.3'
            },
            'equity': {
                'timestamps': timestamps,
                'equity': equity
            },
            'strategies': {
                'names': ['Momentum', 'Mean Reversion', 'Breakout', 'Trend Following'],
                'returns': [12.5, -3.2, 8.7, 15.3]
            },
            'risk': {
                'metrics': ['Sharpe', 'Sortino', 'Calmar', 'VaR', 'Volatility'],
                'values': [1.85, 2.12, 1.67, 4.2, 12.5]
            }
        }
    
    def _get_portfolio_data(self) -> Dict:
        """Generate portfolio positions data"""
        
        positions = [
            {
                'symbol': 'AAPL',
                'quantity': 50,
                'entry_price': 145.30,
                'current_price': 152.80,
                'pnl': 375.00,
                'pnl_pct': 5.16,
                'value': 7640.00
            },
            {
                'symbol': 'GOOGL',
                'quantity': 25,
                'entry_price': 2840.50,
                'current_price': 2795.20,
                'pnl': -1132.50,
                'pnl_pct': -1.59,
                'value': 69880.00
            },
            {
                'symbol': 'MSFT',
                'quantity': 100,
                'entry_price': 280.40,
                'current_price': 295.60,
                'pnl': 1520.00,
                'pnl_pct': 5.42,
                'value': 29560.00
            }
        ]
        
        total_value = sum(p['value'] for p in positions)
        total_pnl = sum(p['pnl'] for p in positions)
        
        return {
            'summary': {
                'total_value': total_value,
                'cash': 5000.00,
                'total_pnl': total_pnl,
                'open_positions': len(positions)
            },
            'positions': positions
        }
    
    def _get_strategies_data(self) -> Dict:
        """Generate strategies performance data"""
        
        strategies = [
            {
                'name': 'Momentum Strategy',
                'return': 12.5,
                'sharpe': 1.85,
                'win_rate': 65.4,
                'trades': 45,
                'status': 'active'
            },
            {
                'name': 'Mean Reversion',
                'return': -3.2,
                'sharpe': 0.92,
                'win_rate': 58.3,
                'trades': 38,
                'status': 'active'
            },
            {
                'name': 'Breakout Trading',
                'return': 8.7,
                'sharpe': 1.54,
                'win_rate': 62.1,
                'trades': 29,
                'status': 'paused'
            },
            {
                'name': 'Trend Following',
                'return': 15.3,
                'sharpe': 2.15,
                'win_rate': 68.9,
                'trades': 15,
                'status': 'active'
            }
        ]
        
        active = sum(1 for s in strategies if s['status'] == 'active')
        best = max(strategies, key=lambda x: x['return'])
        
        return {
            'summary': {
                'active': active,
                'best_strategy': best['name'],
                'best_return': best['return'],
                'avg_sharpe': np.mean([s['sharpe'] for s in strategies]),
                'total_trades': sum(s['trades'] for s in strategies)
            },
            'strategies': strategies
        }
    
    def _get_risk_data(self) -> Dict:
        """Generate risk metrics data"""
        
        # Generate timestamps for last 30 days
        now = datetime.now()
        timestamps = [(now - timedelta(days=30-i)).strftime('%Y-%m-%d') for i in range(30)]
        
        # Generate drawdown data (negative values)
        drawdown = [0]
        for _ in range(29):
            dd = drawdown[-1] + np.random.normal(-0.2, 0.5)
            drawdown.append(max(dd, -15))  # Cap at -15%
        
        # Generate volatility data
        volatility = [10 + np.random.normal(0, 2) for _ in range(30)]
        
        return {
            'metrics': {
                'var_95': 523.40,
                'max_drawdown': 8.3,
                'volatility': 12.5,
                'sharpe': 1.85
            },
            'drawdown': {
                'timestamps': timestamps,
                'drawdown': drawdown
            },
            'volatility': {
                'timestamps': timestamps,
                'volatility': volatility
            }
        }
    
    def _get_trades_data(self) -> Dict:
        """Generate trades history data"""
        
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        strategies = ['Momentum', 'Mean Reversion', 'Breakout', 'Trend Following']
        
        trades = []
        now = datetime.now()
        
        for i in range(20):
            timestamp = now - timedelta(days=i, hours=np.random.randint(0, 24))
            action = 'BUY' if np.random.random() > 0.5 else 'SELL'
            pnl = np.random.normal(50, 100)
            
            trades.append({
                'timestamp': timestamp.isoformat(),
                'strategy': np.random.choice(strategies),
                'symbol': np.random.choice(symbols),
                'action': action,
                'quantity': np.random.randint(10, 100),
                'price': np.random.uniform(100, 300),
                'pnl': pnl
            })
        
        winning = sum(1 for t in trades if t['pnl'] > 0)
        total = len(trades)
        win_rate = (winning / total) * 100 if total > 0 else 0
        
        total_wins = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        total_losses = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        return {
            'summary': {
                'total': total,
                'winning': winning,
                'win_rate': win_rate,
                'profit_factor': profit_factor
            },
            'trades': trades
        }
    
    def _get_settings_data(self) -> Dict:
        """Generate settings data"""
        
        return {
            'settings': {
                'mode': 'paper',
                'initial_capital': 10000,
                'max_position_size': 10,
                'stop_loss': 2,
                'risk_per_trade': 1,
                'auto_refresh': True
            },
            'system': {
                'version': __version__,
                'environment': self.env,
                'uptime': self._get_uptime(),
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    
    # ==================== HELPER METHODS ====================
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        return "Running"
    
    def _emit_update(self, component: str = 'all'):
        """Emit WebSocket update to clients"""
        self.socketio.emit('update', {'component': component})
    
    def run(self):
        """Start dashboard server"""
        
        logger.info("🚀 Starting Flask server...")
        logger.info("")
        
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=self.debug,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )


TradingDashboard = ProfessionalDashboard


if __name__ == "__main__":
    from src.config.config_manager import ConfigManager
    config = ConfigManager()
    dashboard = ProfessionalDashboard(config)
    dashboard.run()
