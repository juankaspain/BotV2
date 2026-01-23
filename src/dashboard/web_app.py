"""BotV2 Professional Dashboard v5.1 - Market Data & Annotations Edition
Ultra-professional real-time trading dashboard with production-grade security

🆕 VERSION 5.1 - MARKET DATA & ANNOTATIONS:
- Added OHLCV candlestick endpoint with timeframe support
- Added chart annotations CRUD endpoints
- Real-time WebSocket sync for annotations
- Complete API integration from api.py
- Merged all functionality from dashboard_standalone.py
- Complete WebSocket broadcast system
- Full SQLAlchemy database support with fallback to mock data

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
- 🗄️ Database Integration v5.0 (SQLAlchemy + Mock fallback)
- 📈 Market Data v5.1 (OHLCV candlesticks)
- 📌 Annotations v5.1 (Chart annotations CRUD)
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
from typing import Dict, List, Optional, Tuple
import hashlib
import secrets
from pathlib import Path
from collections import defaultdict

# ==================== OPTIONAL DATABASE IMPORTS ====================
try:
    from sqlalchemy import create_engine, and_, or_, desc
    from sqlalchemy.orm import sessionmaker, scoped_session
    from .models import (
        Base, Portfolio, Trade, Strategy, StrategyPerformance,
        RiskMetrics, MarketData, Annotation, Alert
    )
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logger.warning("⚠️ SQLAlchemy not available - using mock data only")

# ==================== CONTROL PANEL IMPORT ====================
from .control_routes import control_bp

# ==================== LIVE MONITORING IMPORT ====================
from .monitoring_routes import monitoring_bp

# ==================== STRATEGY EDITOR IMPORT ====================
from .strategy_routes import strategy_bp

# Dashboard version
__version__ = '5.1'

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
        """Check if IP is locked out"""
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
        """Record failed login attempt"""
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
        """Record successful login and reset failed attempts"""
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
        """Verify username and password (timing-attack safe)"""
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
    """Ultra-professional trading dashboard v5.1 - Market Data & Annotations
    
    Architecture:
    - Flask + SocketIO for real-time updates
    - SQLAlchemy for database (optional, fallback to mock)
    - Flask-Limiter for rate limiting
    - Flask-Talisman for HTTPS enforcement (production only)
    - Session-based authentication
    - Plotly for interactive charts
    - WebSocket push for instant updates
    - Modular component design
    - Professional audit logging
    - Control Panel v4.2
    - Live Monitoring v4.3
    - Strategy Editor v4.4
    - Database Integration v5.0
    - Market Data v5.1 (OHLCV)
    - Annotations v5.1 (CRUD)
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
        self.app.config['SESSION_COOKIE_SECURE'] = self.is_production
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
        
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Setup security middleware
        self.rate_limiter_storage = self._setup_rate_limiting()
        self._setup_https_enforcement()
        
        # ==================== DATABASE SETUP ====================
        self._setup_database()
        
        # ==================== REGISTER BLUEPRINTS ====================
        self.app.register_blueprint(control_bp)
        self.app.register_blueprint(monitoring_bp)
        self.app.register_blueprint(strategy_bp)
        
        # Data stores (in-memory fallback)
        self.portfolio_history = []
        self.trades_history = []
        self.strategy_performance = {}
        self.risk_metrics = {}
        self.market_data = {}
        self.alerts = []
        self.annotations = []
        
        # Performance cache
        self.cache = {
            'last_update': None,
            'computed_metrics': {}
        }
        
        # Setup routes and auth
        self._setup_routes()
        self._setup_websocket_handlers()
        
        # Generate demo data if database not available
        if not HAS_DATABASE or not self.db_session:
            self._generate_demo_data()
        
        # Consolidated startup logging
        self._log_startup_banner()
    
    def _setup_database(self):
        """Setup database connection (optional)"""
        self.db_session = None
        
        if not HAS_DATABASE:
            logger.warning("⚠️ Database models not available - using mock data mode")
            return
        
        try:
            DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/dashboard.db')
            
            # Create data directory if needed
            if DATABASE_URL.startswith('sqlite:///'):
                db_path = DATABASE_URL.replace('sqlite:///', '')
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
            Session = scoped_session(sessionmaker(bind=engine))
            
            # Initialize database
            Base.metadata.create_all(engine)
            
            self.db_session = Session
            logger.info(f"✅ Database connected: {DATABASE_URL}")
            
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e} - using mock data mode")
            self.db_session = None
    
    def _generate_demo_data(self):
        """Generate realistic demo trading data"""
        logger.info("📊 Generating demo data...")
        
        # Portfolio history (90 days)
        days = 90
        initial_capital = 3000.0
        current_equity = initial_capital
        
        for i in range(days):
            date = datetime.now() - timedelta(days=(days - i))
            daily_return = np.random.normal(0.001, 0.02)
            current_equity = current_equity * (1 + daily_return)
            
            self.portfolio_history.append({
                'timestamp': date,
                'equity': max(2000, current_equity),
                'cash': max(500, current_equity * 0.3),
                'positions': {
                    'BTC/USD': {'size': 0.05, 'value': current_equity * 0.3},
                    'ETH/USD': {'size': 1.2, 'value': current_equity * 0.25},
                    'AAPL': {'size': 15, 'value': current_equity * 0.15}
                } if i > 10 else {}
            })
        
        # Trades history
        strategies = ['Momentum', 'Mean Reversion', 'Breakout', 'Pairs Trading', 'ML Model']
        symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL', 'TSLA', 'NVDA']
        
        for i in range(125):
            is_win = np.random.rand() < 0.685
            pnl = np.random.uniform(5, 50) if is_win else -np.random.uniform(3, 30)
            
            self.trades_history.append({
                'timestamp': datetime.now() - timedelta(days=np.random.randint(0, 90)),
                'strategy': np.random.choice(strategies),
                'symbol': np.random.choice(symbols),
                'action': np.random.choice(['BUY', 'SELL']),
                'size': np.random.uniform(0.01, 0.1),
                'entry_price': np.random.uniform(100, 50000),
                'exit_price': np.random.uniform(100, 50000),
                'pnl': pnl,
                'pnl_pct': (pnl / np.random.uniform(100, 1000)) * 100,
                'confidence': np.random.uniform(0.5, 0.95)
            })
        
        # Strategy performance
        self.strategy_performance = {
            'Momentum': {'return': 0.125, 'sharpe': 2.1, 'win_rate': 0.72, 'trades': 35},
            'Mean Reversion': {'return': 0.083, 'sharpe': 1.8, 'win_rate': 0.65, 'trades': 42},
            'Breakout': {'return': 0.157, 'sharpe': 2.5, 'win_rate': 0.68, 'trades': 28},
            'Pairs Trading': {'return': 0.062, 'sharpe': 1.5, 'win_rate': 0.71, 'trades': 15},
            'ML Model': {'return': 0.098, 'sharpe': 1.9, 'win_rate': 0.66, 'trades': 5}
        }
        
        logger.info("✅ Demo data generated")
    
    def _setup_rate_limiting(self) -> str:
        """Setup rate limiting middleware"""
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        storage_type = "memory"
        
        try:
            import redis
            r = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=1)
            r.ping()
            storage_uri = f"redis://{redis_host}:{redis_port}"
            storage_type = "redis"
        except Exception:
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
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please slow down.'
            }), 429
        
        return storage_type
    
    def _setup_https_enforcement(self):
        """Setup HTTPS enforcement (production only)"""
        if self.is_production:
            Talisman(
                self.app,
                force_https=True,
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,
                content_security_policy={
                    'default-src': "'self'",
                    'script-src': ["'self'", "'unsafe-inline'", "https://cdn.socket.io", "https://cdn.plot.ly"],
                    'style-src': ["'self'", "'unsafe-inline'"],
                    'img-src': ["'self'", "data:", "https:"],
                    'connect-src': ["'self'", "wss:", "ws:"]
                }
            )
    
    def _log_startup_banner(self):
        """Log consolidated startup banner"""
        self.audit_logger.log_event(
            'system.startup',
            'INFO',
            environment=self.env,
            version=__version__,
            database=HAS_DATABASE and self.db_session is not None
        )
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"   BotV2 Professional Dashboard v{__version__} - Market Data & Annotations")
        logger.info("=" * 80)
        logger.info(f"Environment: {self.env.upper()}")
        logger.info(f"URL: http://{self.host}:{self.port}")
        logger.info(f"Database: {'✅ Connected' if self.db_session else '⚠️ Mock Data Mode'}")
        logger.info(f"Auth: {self.auth.username} / {'✓' if self.auth.password_hash else '✗'}")
        logger.info("=" * 80)
        logger.info("")
    
    def login_required(self, f):
        """Decorator to require login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def _get_db(self):
        """Get database session"""
        if self.db_session:
            return self.db_session()
        return None
    
    def _parse_date_param(self, date_str, default=None):
        """Parse date parameter"""
        if not date_str:
            return default
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return default
    
    def _setup_routes(self):
        """Setup Flask routes - COMPLETE INTEGRATION v5.1"""
        
        # ==================== Authentication ====================
        
        @self.app.route('/login', methods=['GET', 'POST'])
        @self.limiter.limit("10 per minute")
        def login():
            """Login endpoint"""
            if request.method == 'GET':
                if 'user' in session:
                    return redirect(url_for('index'))
                return render_template('login.html')
            
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            ip = request.remote_addr
            
            if self.auth.is_locked_out(ip):
                lockout_info = self.auth.failed_attempts[ip]
                remaining = (lockout_info['locked_until'] - datetime.now()).seconds
                return jsonify({
                    'error': 'Account locked',
                    'message': f'Try again in {remaining}s'
                }), 429
            
            if self.auth.check_credentials(username, password):
                session.permanent = True
                session['user'] = username
                session['login_time'] = datetime.now().isoformat()
                self.auth.record_successful_login(ip, username)
                return jsonify({'success': True, 'redirect': '/'}), 200
            else:
                self.auth.record_failed_attempt(ip, username)
                return jsonify({'error': 'Invalid credentials'}), 401
        
        @self.app.route('/logout')
        def logout():
            """Logout endpoint"""
            session.clear()
            return redirect(url_for('login'))
        
        # ==================== Dashboard Pages ====================
        
        @self.app.route('/')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def index():
            """Main dashboard"""
            return render_template('dashboard.html', user=session.get('user'))
        
        # ==================== API - SECTION DATA ====================
        
        @self.app.route('/api/section/<section>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_section_data(section):
            """Get section data (mock)"""
            try:
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
                    return jsonify({'error': 'Unknown section'}), 404
                
                return jsonify(data)
            except Exception as e:
                logger.error(f"Error in section {section}: {e}")
                return jsonify({'error': str(e)}), 500
        
        # ==================== API - PORTFOLIO (DATABASE) ====================
        
        @self.app.route('/api/portfolio/history')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_portfolio_history():
            """Get portfolio history from database"""
            db = self._get_db()
            
            if not db:
                # Fallback to mock data
                return jsonify({
                    'success': True,
                    'snapshots': self.portfolio_history,
                    'count': len(self.portfolio_history)
                })
            
            try:
                start = self._parse_date_param(request.args.get('start'), datetime.now() - timedelta(days=30))
                end = self._parse_date_param(request.args.get('end'), datetime.now())
                limit = int(request.args.get('limit', 100))
                
                query = db.query(Portfolio).filter(
                    and_(Portfolio.timestamp >= start, Portfolio.timestamp <= end)
                ).order_by(Portfolio.timestamp).limit(limit)
                
                snapshots = [p.to_dict() for p in query.all()]
                
                return jsonify({
                    'success': True,
                    'snapshots': snapshots,
                    'count': len(snapshots)
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
            finally:
                if db:
                    db.close()
        
        @self.app.route('/api/portfolio/equity')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_equity_curve():
            """Get equity curve"""
            db = self._get_db()
            
            if not db:
                # Fallback to mock
                timestamps = [p['timestamp'].isoformat() for p in self.portfolio_history]
                values = [p['equity'] for p in self.portfolio_history]
                
                return jsonify({
                    'success': True,
                    'timestamps': timestamps,
                    'equity': values
                })
            
            try:
                days = int(request.args.get('days', 30))
                start = datetime.now() - timedelta(days=days)
                
                portfolios = db.query(Portfolio).filter(
                    Portfolio.timestamp >= start
                ).order_by(Portfolio.timestamp).all()
                
                timestamps = [p.timestamp.isoformat() for p in portfolios]
                values = [p.total_value for p in portfolios]
                
                return jsonify({
                    'success': True,
                    'timestamps': timestamps,
                    'equity': values
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
            finally:
                if db:
                    db.close()
        
        # ==================== API - TRADES (DATABASE) ====================
        
        @self.app.route('/api/trades')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_trades():
            """Get trades with filters"""
            db = self._get_db()
            
            if not db:
                # Fallback to mock
                return jsonify({
                    'success': True,
                    'trades': self.trades_history[:20],
                    'total': len(self.trades_history)
                })
            
            try:
                query = db.query(Trade)
                
                # Apply filters
                if symbol := request.args.get('symbol'):
                    query = query.filter(Trade.symbol == symbol)
                
                if status := request.args.get('status'):
                    query = query.filter(Trade.status == status)
                
                limit = int(request.args.get('limit', 100))
                offset = int(request.args.get('offset', 0))
                
                total = query.count()
                trades = query.order_by(desc(Trade.entry_time)).limit(limit).offset(offset).all()
                
                return jsonify({
                    'success': True,
                    'trades': [t.to_dict() for t in trades],
                    'total': total,
                    'has_more': (offset + limit) < total
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
            finally:
                if db:
                    db.close()
        
        @self.app.route('/api/trades/stats')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_trade_stats():
            """Get trade statistics"""
            if not self.trades_history:
                return jsonify({
                    'success': True,
                    'total_trades': 0,
                    'win_rate': 0
                })
            
            winning = [t for t in self.trades_history if t.get('pnl', 0) > 0]
            
            return jsonify({
                'success': True,
                'total_trades': len(self.trades_history),
                'winning_trades': len(winning),
                'win_rate': (len(winning) / len(self.trades_history)) * 100
            })
        
        # ==================== API - STRATEGIES ====================
        
        @self.app.route('/api/strategies/comparison')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def compare_strategies():
            """Compare strategies"""
            return jsonify({
                'success': True,
                'strategies': self.strategy_performance
            })
        
        # ==================== API - RISK ====================
        
        @self.app.route('/api/risk/correlation')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_correlation_matrix():
            """Get correlation matrix"""
            strategies = list(self.strategy_performance.keys())
            n = len(strategies)
            correlation = np.eye(n).tolist()
            
            for i in range(n):
                for j in range(i+1, n):
                    corr = np.random.uniform(0.3, 0.8)
                    correlation[i][j] = corr
                    correlation[j][i] = corr
            
            return jsonify({
                'success': True,
                'strategies': strategies,
                'correlations': correlation
            })
        
        # ==================== API - ALERTS ====================
        
        @self.app.route('/api/alerts')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_alerts():
            """Get active alerts"""
            return jsonify({
                'success': True,
                'alerts': self.alerts,
                'count': len(self.alerts)
            })
        
        # ==================== API - MARKET DATA (v5.1) ====================
        
        @self.app.route('/api/market/<symbol>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_market_price(symbol):
            """Get latest price for symbol
            
            Args:
                symbol: Trading symbol (AAPL, BTC/USD, etc.)
            
            Returns:
                JSON with current price, change, volume
            
            Example:
                GET /api/market/AAPL
            """
            # Base prices for mock data
            base_prices = {
                'AAPL': 175.0,
                'GOOGL': 2850.0,
                'MSFT': 295.0,
                'TSLA': 185.0,
                'NVDA': 480.0,
                'AMZN': 152.0,
                'BTC/USD': 43500.0,
                'ETH/USD': 2300.0,
                'EUR/USD': 1.085,
                'GBP/USD': 1.265
            }
            
            base_price = base_prices.get(symbol.upper(), 100.0)
            current_price = base_price * (1 + np.random.normal(0, 0.02))
            previous_close = base_price
            
            change = current_price - previous_close
            change_pct = (change / previous_close) * 100
            
            return jsonify({
                'success': True,
                'symbol': symbol.upper(),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'volume': int(np.random.randint(1000000, 100000000)),
                'timestamp': datetime.now().isoformat() + 'Z'
            })
        
        @self.app.route('/api/market/<symbol>/ohlcv')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_ohlcv_data(symbol):
            """Get OHLCV candlestick data for symbol
            
            Query Parameters:
                timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d) - default: 1h
                limit: Number of candles (1-500) - default: 100
            
            Returns:
                JSON with OHLCV array
            
            Example:
                GET /api/market/AAPL/ohlcv?timeframe=1h&limit=50
            """
            # Parse query parameters
            timeframe = request.args.get('timeframe', '1h')
            limit = min(int(request.args.get('limit', 100)), 500)
            
            # Timeframe to minutes mapping
            timeframe_minutes = {
                '1m': 1,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '1h': 60,
                '4h': 240,
                '1d': 1440
            }
            
            minutes = timeframe_minutes.get(timeframe, 60)
            
            # Base prices per symbol
            base_prices = {
                'AAPL': 175.0,
                'GOOGL': 2850.0,
                'MSFT': 295.0,
                'TSLA': 185.0,
                'NVDA': 480.0,
                'AMZN': 152.0,
                'BTC/USD': 43500.0,
                'ETH/USD': 2300.0,
                'EUR/USD': 1.085,
                'GBP/USD': 1.265
            }
            
            base_price = base_prices.get(symbol.upper(), 100.0)
            
            # Generate OHLCV data
            ohlcv_data = []
            current_time = datetime.now()
            current_price = base_price
            
            for i in range(limit):
                # Calculate timestamp (going backwards)
                timestamp = current_time - timedelta(minutes=minutes * (limit - i))
                
                # Generate realistic OHLC
                open_price = current_price
                
                # Price movement for this candle (random walk)
                price_change = np.random.normal(0, base_price * 0.005)
                close_price = open_price + price_change
                
                # High/Low around open/close
                high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.002)))
                low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.002)))
                
                # Volume (more volume when price moves more)
                base_volume = int(np.random.randint(500000, 2000000))
                volume_multiplier = 1 + abs(price_change / base_price) * 10
                volume = int(base_volume * volume_multiplier)
                
                ohlcv_data.append({
                    'timestamp': timestamp.isoformat() + 'Z',
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
                
                # Update current price for next candle
                current_price = close_price
            
            return jsonify({
                'success': True,
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'data': ohlcv_data,
                'count': len(ohlcv_data)
            })
        
        # ==================== API - ANNOTATIONS (v5.1) ====================
        
        @self.app.route('/api/annotations/<chart_id>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_annotations(chart_id):
            """Get annotations for specific chart
            
            Args:
                chart_id: Chart identifier (equity, trades, risk, etc.)
            
            Returns:
                JSON with annotations array
            
            Example:
                GET /api/annotations/equity
            """
            # Filter annotations for this chart
            chart_annotations = [
                ann for ann in self.annotations 
                if ann.get('chart_id') == chart_id
            ]
            
            return jsonify({
                'success': True,
                'chart_id': chart_id,
                'annotations': chart_annotations,
                'count': len(chart_annotations)
            })
        
        @self.app.route('/api/annotations', methods=['POST'])
        @self.limiter.limit("30 per minute")
        @self.login_required
        def create_annotation():
            """Create new chart annotation
            
            Request Body:
                {
                    'chart_id': 'equity',
                    'type': 'text',
                    'x': '2026-01-23',
                    'y': 10500,
                    'text': 'Important note',
                    'color': '#00ff00'
                }
            
            Returns:
                JSON with created annotation
            
            Example:
                POST /api/annotations
            """
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['chart_id', 'type', 'x', 'y', 'text']
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'error': f'Missing fields: {missing_fields}'
                    }), 400
                
                # Generate ID
                annotation_id = len(self.annotations) + 1
                
                # Create annotation
                annotation = {
                    'id': annotation_id,
                    'chart_id': data['chart_id'],
                    'type': data['type'],
                    'x': data['x'],
                    'y': data['y'],
                    'text': data['text'],
                    'color': data.get('color', '#ffffff'),
                    'created_at': datetime.now().isoformat() + 'Z'
                }
                
                # Store annotation
                self.annotations.append(annotation)
                
                # Broadcast via WebSocket
                self.socketio.emit('annotation_created', annotation, broadcast=True)
                
                logger.info(f"📌 Annotation created: {annotation_id} on {data['chart_id']}")
                
                return jsonify({
                    'success': True,
                    'annotation': annotation,
                    'message': 'Annotation created successfully'
                }), 201
                
            except Exception as e:
                logger.error(f"Error creating annotation: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/annotations/<int:annotation_id>', methods=['DELETE'])
        @self.limiter.limit("30 per minute")
        @self.login_required
        def delete_annotation(annotation_id):
            """Delete chart annotation
            
            Args:
                annotation_id: Annotation ID to delete
            
            Returns:
                JSON with success message
            
            Example:
                DELETE /api/annotations/1
            """
            # Find annotation
            annotation = next(
                (ann for ann in self.annotations if ann['id'] == annotation_id),
                None
            )
            
            if not annotation:
                return jsonify({
                    'success': False,
                    'error': 'Annotation not found'
                }), 404
            
            # Remove annotation
            self.annotations.remove(annotation)
            
            # Broadcast via WebSocket
            self.socketio.emit('annotation_deleted', {'id': annotation_id}, broadcast=True)
            
            logger.info(f"🗑️ Annotation deleted: {annotation_id}")
            
            return jsonify({
                'success': True,
                'message': 'Annotation deleted successfully'
            })
        
        # ==================== HEALTH CHECK ====================
        
        @self.app.route('/health')
        def health():
            """Health check"""
            return jsonify({
                'status': 'healthy',
                'version': __version__,
                'database': self.db_session is not None
            })
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            emit('connected', {
                'message': f'Connected to BotV2 Dashboard v{__version__}',
                'version': __version__
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            pass
        
        @self.socketio.on('subscribe_portfolio')
        def handle_subscribe_portfolio():
            """Subscribe to portfolio updates"""
            emit('subscribed', {'message': 'Subscribed to portfolio updates'})
    
    def broadcast_portfolio_update(self, portfolio_data):
        """Broadcast portfolio update"""
        self.socketio.emit('portfolio_update', portfolio_data, broadcast=True)
    
    def broadcast_trade_execution(self, trade_data):
        """Broadcast trade execution"""
        self.socketio.emit('trade_executed', trade_data, broadcast=True)
    
    # ==================== DATA GENERATORS ====================
    
    def _get_dashboard_data(self) -> Dict:
        """Generate dashboard data"""
        now = datetime.now()
        timestamps = [(now - timedelta(days=30-i)).strftime('%Y-%m-%d') for i in range(30)]
        
        initial_equity = 10000
        equity = [initial_equity]
        for _ in range(29):
            change = np.random.normal(0.002, 0.015)
            equity.append(equity[-1] * (1 + change))
        
        return {
            'overview': {
                'equity': f'€{equity[-1]:,.2f}',
                'daily_change': equity[-1] - equity[-2],
                'total_return': f'{((equity[-1] / initial_equity) - 1) * 100:.2f}',
                'win_rate': '65.4',
                'total_trades': 127
            },
            'equity': {
                'timestamps': timestamps,
                'equity': equity
            }
        }
    
    def _get_portfolio_data(self) -> Dict:
        """Generate portfolio data"""
        positions = [
            {'symbol': 'AAPL', 'quantity': 50, 'pnl': 375.00, 'value': 7640.00},
            {'symbol': 'GOOGL', 'quantity': 25, 'pnl': -1132.50, 'value': 69880.00}
        ]
        
        return {
            'summary': {
                'total_value': sum(p['value'] for p in positions),
                'total_pnl': sum(p['pnl'] for p in positions)
            },
            'positions': positions
        }
    
    def _get_strategies_data(self) -> Dict:
        """Generate strategies data"""
        return {
            'summary': {'active': 4},
            'strategies': self.strategy_performance
        }
    
    def _get_risk_data(self) -> Dict:
        """Generate risk data"""
        return {
            'metrics': {
                'var_95': 523.40,
                'max_drawdown': 8.3,
                'sharpe': 1.85
            }
        }
    
    def _get_trades_data(self) -> Dict:
        """Generate trades data"""
        return {
            'summary': {'total': len(self.trades_history)},
            'trades': self.trades_history[:20]
        }
    
    def _get_settings_data(self) -> Dict:
        """Generate settings data"""
        return {
            'settings': {'mode': 'paper'},
            'system': {'version': __version__}
        }
    
    def _get_uptime(self) -> str:
        """Get uptime"""
        return "Running"
    
    def run(self):
        """Start server"""
        logger.info("🚀 Starting dashboard server...")
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
