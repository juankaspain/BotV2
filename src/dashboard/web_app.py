"""BotV2 Professional Dashboard v6.0 - Metrics Monitoring Edition
Ultra-professional real-time trading dashboard with production-grade security and metrics

🆕 VERSION 6.0 - METRICS MONITORING INTEGRATED:
- Real-time metrics monitoring (RPM, errors, latency)
- P50, P95, P99 latency percentiles
- Active user tracking
- WebSocket connection monitoring
- System resource monitoring (CPU, Memory)
- Historical metrics (60 minutes)
- REST API for metrics access
- JSON/CSV export capabilities
- All v5.3 features maintained (GZIP compression, security, etc.)
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

# ✅ GZIP COMPRESSION IMPORT
try:
    from flask_compress import Compress
    HAS_COMPRESS = True
except ImportError:
    HAS_COMPRESS = False
    logging.getLogger(__name__).warning("⚠️ Flask-Compress not installed - install with: pip install flask-compress")

# ==================== METRICS MONITORING IMPORT ====================
try:
    from .metrics_monitor import get_metrics_monitor, MetricsMiddleware
    from .metrics_routes import metrics_bp
    HAS_METRICS = True
except ImportError:
    HAS_METRICS = False
    logging.getLogger(__name__).warning("⚠️ Metrics monitoring not available")

# ==================== MOCK DATA IMPORT ====================
try:
    from .mock_data import get_section_data
    HAS_MOCK_DATA = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Mock data module imported successfully")
except ImportError:
    HAS_MOCK_DATA = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Mock data module not found - using fallback data")

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

# ==================== BLUEPRINT IMPORTS ====================
from .control_routes import control_bp
from .monitoring_routes import monitoring_bp
from .strategy_routes import strategy_bp

# Dashboard version
__version__ = '6.0'

logger = logging.getLogger(__name__)
limiter_logger = logging.getLogger('flask-limiter')
limiter_logger.setLevel(logging.CRITICAL)


class SecurityAuditLogger:
    """Professional security audit logger"""
    
    def __init__(self, log_file: str = 'logs/security_audit.log'):
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('security_audit')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=10
        )
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, level: str, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': level,
            'event_type': event_type,
            **kwargs
        }
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(json.dumps(log_entry))


class DashboardAuth:
    """Session-Based Authentication"""
    
    def __init__(self, audit_logger: SecurityAuditLogger):
        self.username = os.getenv('DASHBOARD_USERNAME', 'admin')
        self.password_hash = self._get_password_hash()
        self.audit_logger = audit_logger
        self.failed_attempts = defaultdict(lambda: {'count': 0, 'last_attempt': None, 'locked_until': None})
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=5)
        
        if not self.password_hash:
            temp_password = secrets.token_urlsafe(16)
            logger.warning(f"SECURITY: Temporary password: {temp_password}")
            self.password_hash = self._hash_password(temp_password)
    
    def _get_password_hash(self) -> str:
        password = os.getenv('DASHBOARD_PASSWORD')
        return self._hash_password(password) if password else None
    
    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def is_locked_out(self, ip: str) -> bool:
        attempt_info = self.failed_attempts[ip]
        if attempt_info['locked_until']:
            if datetime.now() < attempt_info['locked_until']:
                return True
            else:
                attempt_info['count'] = 0
                attempt_info['locked_until'] = None
        return False
    
    def record_failed_attempt(self, ip: str, username: str):
        attempt_info = self.failed_attempts[ip]
        attempt_info['count'] += 1
        attempt_info['last_attempt'] = datetime.now()
        
        self.audit_logger.log_event(
            'auth.login.failed', 'WARNING',
            user=username, ip=ip, failed_attempts=attempt_info['count'],
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
        
        if attempt_info['count'] >= self.max_attempts:
            attempt_info['locked_until'] = datetime.now() + self.lockout_duration
            self.audit_logger.log_event(
                'auth.account.locked', 'ERROR',
                user=username, ip=ip, reason='too_many_failed_attempts',
                locked_until=attempt_info['locked_until'].isoformat()
            )
    
    def record_successful_login(self, ip: str, username: str):
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
        
        self.audit_logger.log_event(
            'auth.login.success', 'INFO',
            user=username, ip=ip,
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
    
    def check_credentials(self, username: str, password: str) -> bool:
        if not self.password_hash:
            return True
        
        username_match = secrets.compare_digest(username, self.username)
        password_match = secrets.compare_digest(
            self._hash_password(password), self.password_hash
        )
        return username_match and password_match


class ProfessionalDashboard:
    """Ultra-professional trading dashboard v6.0 with metrics monitoring"""
    
    def __init__(self, config):
        self.config = config
        dash_config = config.get('dashboard', {})
        
        self.host = dash_config.get('host', '0.0.0.0')
        self.port = dash_config.get('port', 8050)
        self.debug = dash_config.get('debug', False)
        
        self.env = os.getenv('FLASK_ENV', 'development')
        self.is_production = self.env == 'production'
        
        self.audit_logger = SecurityAuditLogger()
        self.auth = DashboardAuth(self.audit_logger)
        
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / 'templates'),
            static_folder=str(Path(__file__).parent / 'static')
        )
        
        # ✅ GZIP COMPRESSION CONFIGURATION
        self._setup_compression()
        
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
        self.app.config['SESSION_COOKIE_SECURE'] = self.is_production
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
        
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.rate_limiter_storage = self._setup_rate_limiting()
        self._setup_https_enforcement()
        self._setup_database()
        
        # ✅ METRICS MONITORING SETUP
        self._setup_metrics()
        
        # Register blueprints
        self.app.register_blueprint(control_bp)
        self.app.register_blueprint(monitoring_bp)
        self.app.register_blueprint(strategy_bp)
        
        # Register metrics blueprint if available
        if HAS_METRICS:
            self.app.register_blueprint(metrics_bp)
            logger.info("✅ Metrics API registered at /api/metrics")
        
        self.alerts = []
        self.annotations = []
        
        self._setup_routes()
        self._setup_websocket_handlers()
        
        self._log_startup_banner()
    
    def _setup_compression(self):
        """✅ Setup GZIP compression for all responses"""
        if HAS_COMPRESS:
            self.app.config['COMPRESS_MIMETYPES'] = [
                'text/html', 'text/css', 'text/javascript',
                'application/javascript', 'application/json',
                'text/xml', 'application/xml', 'text/plain'
            ]
            self.app.config['COMPRESS_LEVEL'] = 6
            self.app.config['COMPRESS_MIN_SIZE'] = 500
            
            self.compress = Compress(self.app)
            logger.info("✅ GZIP compression enabled (level 6, min 500 bytes)")
        else:
            self.compress = None
            logger.warning("⚠️ GZIP compression disabled")
    
    def _setup_metrics(self):
        """✅ Setup metrics monitoring system"""
        if HAS_METRICS:
            # Initialize metrics monitor (5 minute rolling window)
            self.metrics_monitor = get_metrics_monitor(window_seconds=300)
            
            # Register middleware for automatic request tracking
            MetricsMiddleware(self.app, self.metrics_monitor)
            
            logger.info("✅ Metrics monitoring enabled (5min window)")
            logger.info("📊 Tracking: RPM, errors, latency (P50/P95/P99), users, resources")
        else:
            self.metrics_monitor = None
            logger.warning("⚠️ Metrics monitoring disabled")
    
    def _setup_database(self):
        self.db_session = None
        
        if not HAS_DATABASE:
            return
        
        try:
            DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/dashboard.db')
            
            if DATABASE_URL.startswith('sqlite:///'):
                db_path = DATABASE_URL.replace('sqlite:///', '')
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
            Session = scoped_session(sessionmaker(bind=engine))
            Base.metadata.create_all(engine)
            
            self.db_session = Session
            logger.info(f"✅ Database connected: {DATABASE_URL}")
        except Exception as e:
            logger.warning(f"⚠️ Database failed: {e} - using mock data")
            self.db_session = None
    
    def _setup_rate_limiting(self) -> str:
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
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
                'security.rate_limit.exceeded', 'WARNING',
                ip=request.remote_addr, path=request.path,
                user_agent=request.headers.get('User-Agent', 'Unknown')
            )
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please slow down.'
            }), 429
        
        return storage_type
    
    def _setup_https_enforcement(self):
        if self.is_production:
            Talisman(
                self.app, force_https=True,
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
        self.audit_logger.log_event(
            'system.startup', 'INFO',
            environment=self.env, version=__version__,
            database=HAS_DATABASE and self.db_session is not None,
            mock_data=HAS_MOCK_DATA,
            gzip_compression=HAS_COMPRESS,
            metrics_monitoring=HAS_METRICS
        )
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"   BotV2 Dashboard v{__version__} - Metrics Monitoring Edition")
        logger.info("=" * 80)
        logger.info(f"Environment: {self.env.upper()}")
        logger.info(f"URL: http://{self.host}:{self.port}")
        logger.info(f"Mock Data: {'✅ Loaded' if HAS_MOCK_DATA else '⚠️ Fallback'}")
        logger.info(f"Database: {'✅ Connected' if self.db_session else '⚠️ Mock Mode'}")
        logger.info(f"GZIP: {'✅ Enabled (60-85% reduction)' if HAS_COMPRESS else '⚠️ Disabled'}")
        logger.info(f"Metrics: {'✅ Monitoring Active' if HAS_METRICS else '⚠️ Disabled'}")
        logger.info(f"Auth: {self.auth.username} / {'✓' if self.auth.password_hash else '✗'}")
        logger.info("=" * 80)
        logger.info("")
    
    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def _get_db(self):
        if self.db_session:
            return self.db_session()
        return None
    
    def _setup_routes(self):
        # ==================== AUTH ====================
        
        @self.app.route('/login', methods=['GET', 'POST'])
        @self.limiter.limit("10 per minute")
        def login():
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
                return jsonify({'error': 'Account locked', 'message': f'Try again in {remaining}s'}), 429
            
            if self.auth.check_credentials(username, password):
                session.permanent = True
                session['user'] = username
                session['login_time'] = datetime.now().isoformat()
                self.auth.record_successful_login(ip, username)
                
                # ✅ Track user activity in metrics
                if HAS_METRICS and self.metrics_monitor:
                    self.metrics_monitor.record_user_activity(username)
                
                return jsonify({'success': True, 'redirect': '/'}), 200
            else:
                self.auth.record_failed_attempt(ip, username)
                return jsonify({'error': 'Invalid credentials'}), 401
        
        @self.app.route('/logout')
        def logout():
            session.clear()
            return redirect(url_for('login'))
        
        # ==================== DASHBOARD ====================
        
        @self.app.route('/')
        @self.limiter.limit("20 per minute")
        @self.login_required
        def index():
            # ✅ Track user activity
            if HAS_METRICS and self.metrics_monitor:
                user = session.get('user')
                if user:
                    self.metrics_monitor.record_user_activity(user)
            
            return render_template('dashboard.html', user=session.get('user'))
        
        # ==================== API - SECTION DATA ====================
        
        @self.app.route('/api/section/<section>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_section_data_route(section):
            """Get section data from mock_data module (with GZIP compression)"""
            try:
                if HAS_MOCK_DATA:
                    data = get_section_data(section)
                    if data:
                        logger.info(f"✅ Section '{section}' loaded from mock_data.py")
                        return jsonify(data)
                    else:
                        logger.warning(f"⚠️ Section '{section}' returned empty data")
                        return jsonify({'error': 'Section not found'}), 404
                else:
                    logger.warning(f"⚠️ Using fallback data for section '{section}'")
                    return jsonify(self._get_fallback_data(section))
                
            except Exception as e:
                logger.error(f"❌ Error in section {section}: {e}")
                return jsonify({'error': str(e)}), 500
        
        # ==================== API - MARKET DATA ====================
        
        @self.app.route('/api/market/<symbol>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_market_price(symbol):
            base_prices = {
                'AAPL': 175.0, 'GOOGL': 2850.0, 'MSFT': 295.0,
                'TSLA': 185.0, 'NVDA': 480.0, 'AMZN': 152.0,
                'BTC/USD': 43500.0, 'ETH/USD': 2300.0,
                'EUR/USD': 1.085, 'GBP/USD': 1.265
            }
            
            base_price = base_prices.get(symbol.upper(), 100.0)
            current_price = base_price * (1 + np.random.normal(0, 0.02))
            change = current_price - base_price
            change_pct = (change / base_price) * 100
            
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
            timeframe = request.args.get('timeframe', '1h')
            limit = min(int(request.args.get('limit', 100)), 500)
            
            timeframe_minutes = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '4h': 240, '1d': 1440
            }
            
            minutes = timeframe_minutes.get(timeframe, 60)
            base_prices = {
                'AAPL': 175.0, 'GOOGL': 2850.0, 'MSFT': 295.0,
                'BTC/USD': 43500.0, 'ETH/USD': 2300.0
            }
            
            base_price = base_prices.get(symbol.upper(), 100.0)
            ohlcv_data = []
            current_time = datetime.now()
            current_price = base_price
            
            for i in range(limit):
                timestamp = current_time - timedelta(minutes=minutes * (limit - i))
                open_price = current_price
                price_change = np.random.normal(0, base_price * 0.005)
                close_price = open_price + price_change
                high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.002)))
                low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.002)))
                volume = int(np.random.randint(500000, 2000000))
                
                ohlcv_data.append({
                    'timestamp': timestamp.isoformat() + 'Z',
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
                
                current_price = close_price
            
            return jsonify({
                'success': True,
                'symbol': symbol.upper(),
                'timeframe': timeframe,
                'data': ohlcv_data,
                'count': len(ohlcv_data)
            })
        
        # ==================== API - ANNOTATIONS ====================
        
        @self.app.route('/api/annotations/<chart_id>')
        @self.limiter.limit("30 per minute")
        @self.login_required
        def get_annotations(chart_id):
            chart_annotations = [
                ann for ann in self.annotations if ann.get('chart_id') == chart_id
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
            try:
                data = request.get_json()
                required_fields = ['chart_id', 'type', 'x', 'y', 'text']
                missing_fields = [f for f in required_fields if f not in data]
                
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'error': f'Missing fields: {missing_fields}'
                    }), 400
                
                annotation_id = len(self.annotations) + 1
                
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
                
                self.annotations.append(annotation)
                self.socketio.emit('annotation_created', annotation, broadcast=True)
                
                return jsonify({
                    'success': True,
                    'annotation': annotation,
                    'message': 'Annotation created successfully'
                }), 201
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/annotations/<int:annotation_id>', methods=['DELETE'])
        @self.limiter.limit("30 per minute")
        @self.login_required
        def delete_annotation(annotation_id):
            annotation = next(
                (ann for ann in self.annotations if ann['id'] == annotation_id),
                None
            )
            
            if not annotation:
                return jsonify({'success': False, 'error': 'Annotation not found'}), 404
            
            self.annotations.remove(annotation)
            self.socketio.emit('annotation_deleted', {'id': annotation_id}, broadcast=True)
            
            return jsonify({'success': True, 'message': 'Annotation deleted'})
        
        # ==================== HEALTH ====================
        
        @self.app.route('/health')
        def health():
            health_data = {
                'status': 'healthy',
                'version': __version__,
                'mock_data': HAS_MOCK_DATA,
                'database': self.db_session is not None,
                'gzip': HAS_COMPRESS,
                'metrics': HAS_METRICS
            }
            
            # ✅ Add metrics snapshot if available
            if HAS_METRICS and self.metrics_monitor:
                try:
                    snapshot = self.metrics_monitor.get_current_snapshot()
                    health_data['metrics_snapshot'] = {
                        'request_rate_rpm': snapshot.request_rate_rpm,
                        'error_rate_pct': snapshot.error_rate_pct,
                        'active_users': snapshot.active_users,
                        'websocket_connections': snapshot.websocket_connections
                    }
                except Exception as e:
                    logger.error(f"Error getting metrics snapshot: {e}")
            
            return jsonify(health_data)
    
    def _get_fallback_data(self, section: str) -> Dict:
        """Fallback data if mock_data.py not available"""
        fallback = {
            'dashboard': {'overview': {'equity': '€10,000', 'total_pnl': '+€500'}, 'equity': {'timestamps': [], 'equity': []}},
            'portfolio': {'summary': {'total_value': 10000}, 'positions': []},
            'strategies': {'summary': {'active': 0}, 'strategies': []},
            'risk': {'metrics': {'var_95': 0, 'max_drawdown': 0}},
            'trades': {'summary': {'total': 0}, 'trades': []},
            'settings': {'settings': {}, 'system': {'version': __version__}}
        }
        return fallback.get(section, {'error': 'Section not found'})
    
    def _setup_websocket_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            # ✅ Track WebSocket connection
            if HAS_METRICS and self.metrics_monitor:
                self.metrics_monitor.increment_websocket_connections()
                logger.debug(f"WebSocket connected (total: {self.metrics_monitor.get_websocket_connections()})")
            
            emit('connected', {'message': f'Connected to BotV2 v{__version__}', 'version': __version__})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            # ✅ Track WebSocket disconnection
            if HAS_METRICS and self.metrics_monitor:
                self.metrics_monitor.decrement_websocket_connections()
                logger.debug(f"WebSocket disconnected (total: {self.metrics_monitor.get_websocket_connections()})")
    
    def run(self):
        logger.info("🚀 Starting dashboard server...")
        
        if HAS_METRICS and self.metrics_monitor:
            logger.info("📊 Metrics monitoring active - access at /api/metrics")
        
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
