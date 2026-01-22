"""BotV2 Professional Dashboard v4.0 - Enterprise Edition
Ultra-professional real-time trading dashboard with production-grade security

Security Features:
- Session-Based Authentication (no HTTP Basic popup)
- Rate Limiting (10 req/min per IP)
- HTTPS Enforcement (production only)
- Security Headers (HSTS, CSP, X-Frame-Options, etc.)
- Brute Force Protection with account lockout
- WebSocket Real-time Updates
- Professional Audit Logging (JSON structured)

Other Features:
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

# Dashboard version
__version__ = '4.2'

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
    """Ultra-professional trading dashboard v4.2 with enterprise security
    
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
        
        # ==================== REGISTER CONTROL PANEL BLUEPRINT ====================
        self.app.register_blueprint(control_bp)
        
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
            features=['session_auth', 'rate_limiting', 'audit_logging', 'account_lockout', 'spa_navigation', '3_themes', 'control_panel_v4.2']
        )
        
        # Consolidated startup banner
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"        BotV2 Professional Dashboard v{__version__} - Enterprise Edition")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📊 SYSTEM CONFIGURATION")
        logger.info(f"   Environment:           {self.env.upper()}")
        logger.info(f"   Version:               {__version__}")
        logger.info(f"   URL:                   http{'s' if self.is_production else ''}://{self.host}:{self.port}")
        logger.info(f"   Dashboard:             http://{self.host}:{self.port}/dashboard")
        logger.info(f"   Control Panel:         http://{self.host}:{self.port}/control")
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
        logger.info("   • 🎛️ Control Panel v4.2 (Bot management)")
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
        """Setup Flask routes with authentication"""
        
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
        
        # ==================== CONTROL PANEL ROUTE ====================
        
        @self.app.route('/control')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def control_panel():
            """Control panel page v4.2"""
            return render_template('control.html', user=session.get('user'))
        
        # ==================== API Routes ====================
        
        @self.app.route('/api/overview')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_overview():
            """Portfolio overview API"""
            return jsonify(self._get_portfolio_overview())
        
        @self.app.route('/api/equity')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_equity():
            """Equity curve data"""
            return jsonify(self._get_equity_data())
        
        @self.app.route('/api/trades')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_trades():
            """Recent trades"""
            limit = request.args.get('limit', 50, type=int)
            return jsonify(self._get_trades_data(limit))
        
        @self.app.route('/api/strategies')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_strategies():
            """Strategy performance"""
            return jsonify(self._get_strategies_data())
        
        @self.app.route('/api/risk')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_risk():
            """Risk metrics and analytics"""
            return jsonify(self._get_risk_analytics())
        
        @self.app.route('/api/correlation')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_correlation():
            """Correlation heatmap data"""
            return jsonify(self._get_correlation_matrix())
        
        @self.app.route('/api/attribution')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_attribution():
            """Performance attribution"""
            return jsonify(self._get_performance_attribution())
        
        @self.app.route('/api/alerts')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_alerts():
            """Active alerts"""
            return jsonify({'alerts': self.alerts})
        
        # ==================== Dynamic Section API ====================
        
        @self.app.route('/api/section/<section>')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def api_section(section):
            """Dynamic section data API with mock data for demo mode"""
            from src.dashboard.mock_data import (
                generate_dashboard_data,
                generate_portfolio_data,
                generate_strategies_data,
                generate_risk_data,
                generate_trades_data,
                generate_settings_data
            )
            
            # Route to appropriate generator
            generators = {
                'dashboard': generate_dashboard_data,
                'portfolio': generate_portfolio_data,
                'strategies': generate_strategies_data,
                'risk': generate_risk_data,
                'trades': generate_trades_data,
                'settings': generate_settings_data
            }
            
            generator = generators.get(section)
            if generator:
                logger.debug(f"📊 API: Section '{section}' data requested by {session.get('user')}")
                return jsonify(generator())
            
            logger.warning(f"⚠️ API: Invalid section '{section}' requested")
            return jsonify({'error': 'Section not found'}), 404
        
        # ==================== Export & Utilities ====================
        
        @self.app.route('/api/export/report')
        @self.limiter.limit("5 per minute")
        @self.login_required
        def api_export_report():
            """Export PDF/Excel report"""
            format_type = request.args.get('format', 'pdf')
            return self._export_report(format_type)
        
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
                    'control_panel': 'v4.2'
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
                'features': ['session_auth', 'rate_limiting', 'audit_logging', 'spa', '3_themes', 'control_panel_v4.2']
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.debug(f"❌ WEBSOCKET: Client disconnected - SID: {request.sid}")
        
        @self.socketio.on('request_update')
        def handle_update_request(data):
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
        return "Running"
    
    def _export_report(self, format_type: str):
        """Export performance report"""
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
        """Update dashboard data from trading system
        
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
        
        # Keep last 10000 points
        if len(self.portfolio_history) > 10000:
            self.portfolio_history = self.portfolio_history[-10000:]
        
        self.trades_history = trades
        self.strategy_performance = strategies
        self.risk_metrics = risk
        
        # Update cache
        self.cache['last_update'] = datetime.now().isoformat()
        
        # Emit WebSocket update
        self._emit_update('all')
        
        logger.debug("📊 DATA: Dashboard data updated via WebSocket")
    
    def add_alert(self, level: str, message: str, category: str = 'general'):
        """Add alert to dashboard
        
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
        
        logger.info(f"🚨 ALERT: [{level.upper()}] {message}")
    
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
