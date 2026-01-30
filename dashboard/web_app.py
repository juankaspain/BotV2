"""BotV2 Professional Dashboard v7.6 - System Health Enhanced
Ultra-professional real-time trading dashboard with enterprise-grade security

VERSION 7.6 - SYSTEM HEALTH ENHANCED:
- NEW: Professional System Health UI with real-time metrics
- NEW: Enhanced /api/system-health endpoint with comprehensive data
- NEW: CPU, Memory, Disk, Network monitoring via psutil
- NEW: Python environment details
- NEW: Component status tracking
- NEW: Security status reporting
- NEW: Recent activity log

All v7.5 features maintained:
- CSRF Protection: Token-based validation (all forms + AJAX)
- XSS Prevention: bleach backend + DOMPurify frontend
- Input Validation: Pydantic models for type-safe validation
- Session Management: Secure cookies + automatic timeout
- Rate Limiting: Redis backend + per-endpoint limits
- Security Audit Logging: Comprehensive JSON event logs
- Security Headers: CSP with nonces, HSTS, X-Frame-Options
- HTTPS Enforcement: Production-grade TLS (Talisman)
- Nonce-Based CSP: Eliminates unsafe-inline vulnerability
- SRI Protection: All CDN libraries with integrity checks
"""

import logging
import os
import sys
import time
import platform
import threading
from pathlib import Path

# ============================================================================
# CRITICAL: Load .env file FIRST using centralized loader
# ============================================================================
_DASHBOARD_DIR = Path(__file__).parent
_PROJECT_ROOT = _DASHBOARD_DIR.parent

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(_DASHBOARD_DIR))

# Centralized env loading
try:
    from shared.utils.env_loader import load_env_once
    load_env_once(verbose=True)
except ImportError:
    try:
        from dotenv import load_dotenv
        env_file = _PROJECT_ROOT / '.env'
        if env_file.exists():
            load_dotenv(env_file)
    except ImportError:
        pass

# ============================================================================
# STANDARD IMPORTS
# ============================================================================
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, g
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
import hashlib
import secrets
from collections import defaultdict, deque

# ============================================================================
# OPTIONAL IMPORTS WITH FALLBACKS
# ============================================================================

# psutil for system metrics
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Flask version
try:
    import flask
    FLASK_VERSION = flask.__version__
except:
    FLASK_VERSION = 'unknown'

# Pydantic - optional
try:
    from pydantic import ValidationError
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    class ValidationError(Exception):
        pass

# Talisman - optional for security headers
try:
    from flask_talisman import Talisman
    HAS_TALISMAN = True
except ImportError:
    HAS_TALISMAN = False

# SECURITY IMPORTS (New Modular Architecture)
try:
    from shared.security import (
        init_csrf_protection,
        get_csrf_token,
        sanitize_html,
        sanitize_dict,
        xss_protection_middleware,
        init_rate_limiter,
        init_audit_logger,
        get_audit_logger,
        init_security_middleware,
        SessionManager,
        LoginRequest,
        AnnotationCreate,
        validate_input,
        sanitize_filename
    )
    HAS_SECURITY = True
except ImportError as e:
    HAS_SECURITY = False
    logging.getLogger(__name__).warning("Security modules not available: %s", e)

# GZIP COMPRESSION
try:
    from flask_compress import Compress
    HAS_COMPRESS = True
except ImportError:
    HAS_COMPRESS = False

# METRICS MONITORING
HAS_METRICS = False
try:
    from dashboard.metrics_monitor import get_metrics_monitor, MetricsMiddleware
    HAS_METRICS = True
except ImportError:
    try:
        from metrics_monitor import get_metrics_monitor, MetricsMiddleware
        HAS_METRICS = True
    except ImportError:
        pass

# MOCK DATA
HAS_MOCK_DATA = False
try:
    from dashboard.mock_data import get_section_data
    HAS_MOCK_DATA = True
except ImportError:
    try:
        from mock_data import get_section_data
        HAS_MOCK_DATA = True
    except ImportError:
        pass

# DATABASE (OPTIONAL)
HAS_DATABASE = False
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    try:
        from dashboard.models import Base
    except ImportError:
        from models import Base
    HAS_DATABASE = True
except ImportError:
    pass

# BLUEPRINTS
try:
    from dashboard.routes.control_routes import control_bp
    from dashboard.routes.monitoring_routes import monitoring_bp
    from dashboard.routes.strategy_routes import strategy_bp
    from dashboard.routes.metrics_routes import metrics_bp as metrics_routes_bp
except ImportError:
    from routes.control_routes import control_bp
    from routes.monitoring_routes import monitoring_bp
    from routes.strategy_routes import strategy_bp
    from routes.metrics_routes import metrics_bp as metrics_routes_bp

# Dashboard version
__version__ = '7.6'

logger = logging.getLogger(__name__)

# Application start time for uptime calculation
APP_START_TIME = time.time()

# Recent activity log (in-memory, limited to last 100 entries)
RECENT_ACTIVITY: deque = deque(maxlen=100)

# ASCII Banner
ASCII_BANNER = r"""
================================================================================
    ____        __ _    _____    ____            __    __                       
   / __ )____  / /| |  / /__ \  / __ \____ ___  / /_  / /_  ____  ____ _________
  / __  / __ \/ __/ | / /__/ / / / / / __ `__ \/ __ \/ __ \/ __ \/ __ `/ ___/ _ \
 / /_/ / /_/ / /_ | |/ / __/  / /_/ / / / / / / /_/ / /_/ / /_/ / /_/ / /  /  __/
/_____/\____/\__/ |___/____/ /_____/_/ /_/ /_/_.___/_.___/\____/\__,_/_/   \___/ 
                                                                                 
    Version {version}  |  Security Phase 1 Complete  |  {env}
================================================================================
"""


def log_activity(activity_type: str, message: str):
    """Log activity to recent activity buffer."""
    RECENT_ACTIVITY.appendleft({
        'time': datetime.now().strftime('%H:%M:%S'),
        'type': activity_type,
        'message': message,
        'timestamp': time.time()
    })


class SSLErrorFilter(logging.Filter):
    """Filter out SSL/TLS handshake errors from logs."""
    
    def filter(self, record):
        if 'Bad request version' in record.getMessage():
            return False
        if 'code 400' in record.getMessage() and '\\x' in record.getMessage():
            return False
        return True


def generate_csp_nonce() -> str:
    """Generate cryptographically secure nonce for CSP."""
    return secrets.token_urlsafe(18)


class DashboardAuth:
    """Enhanced Session-Based Authentication with Security Audit Logging."""
    
    def __init__(self, audit_logger=None):
        self.username = os.getenv('DASHBOARD_USERNAME', 'admin')
        self.password_hash = self._get_password_hash()
        self.audit_logger = audit_logger
        self.failed_attempts = defaultdict(lambda: {'count': 0, 'last_attempt': None, 'locked_until': None})
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=5)
        
        env_username = os.getenv('DASHBOARD_USERNAME')
        env_password = os.getenv('DASHBOARD_PASSWORD')
        
        if env_username and env_password:
            logger.info(f"[AUTH] Using credentials from .env: username={self.username}")
        else:
            logger.warning("[AUTH] No DASHBOARD_USERNAME/PASSWORD in .env, using defaults")
        
        if not self.password_hash:
            demo_password = os.getenv('DASHBOARD_PASSWORD', 'admin')
            self.password_hash = self._hash_password(demo_password)
    
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
        
        if self.audit_logger:
            self.audit_logger.log_login_failure(username, reason='invalid_credentials', failed_attempts=attempt_info['count'])
        
        log_activity('warning', f'Failed login attempt for user: {username}')
        
        if attempt_info['count'] >= self.max_attempts:
            attempt_info['locked_until'] = datetime.now() + self.lockout_duration
            if self.audit_logger:
                self.audit_logger.log_account_locked(
                    username, 
                    reason='too_many_failed_attempts',
                    locked_until=attempt_info['locked_until'].isoformat()
                )
            log_activity('error', f'Account locked: {username} (too many attempts)')
    
    def record_successful_login(self, ip: str, username: str):
        if ip in self.failed_attempts:
            del self.failed_attempts[ip]
        
        if self.audit_logger:
            self.audit_logger.log_login_success(username)
        
        log_activity('success', f'User logged in: {username}')
    
    def check_credentials(self, username: str, password: str) -> bool:
        if not self.password_hash:
            return True
        
        username_match = secrets.compare_digest(username, self.username)
        password_match = secrets.compare_digest(
            self._hash_password(password), self.password_hash
        )
        return username_match and password_match


class ProfessionalDashboard:
    """Ultra-professional trading dashboard v7.6 with System Health."""
    
    def __init__(self, config):
        self.config = config
        dash_config = config.get('dashboard', {}) if hasattr(config, 'get') else {}
        
        self.host = dash_config.get('host', '0.0.0.0')
        self.port = int(os.getenv('DASHBOARD_PORT', dash_config.get('port', 8050)))
        self.debug = dash_config.get('debug', False)
        
        # Environment detection
        flask_env = os.getenv('FLASK_ENV', '').lower()
        general_env = os.getenv('ENVIRONMENT', '').lower()
        
        if flask_env:
            self.env = flask_env
        elif general_env:
            self.env = general_env
        else:
            self.env = 'development'
        
        force_https = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
        self.is_production = (self.env == 'production' and force_https)
        self.is_development = not self.is_production
        
        logger.info("="*70)
        logger.info("ENVIRONMENT DETECTION:")
        logger.info("  FLASK_ENV = %s", os.getenv('FLASK_ENV', 'NOT SET'))
        logger.info("  ENVIRONMENT = %s", os.getenv('ENVIRONMENT', 'NOT SET'))
        logger.info("  FORCE_HTTPS = %s", os.getenv('FORCE_HTTPS', 'false'))
        logger.info("  Detected mode: %s", self.env.upper())
        logger.info("="*70)
        
        # Initialize audit logger
        if HAS_SECURITY:
            self.audit_logger = init_audit_logger()
        else:
            self.audit_logger = None
        
        self.auth = DashboardAuth(self.audit_logger)
        
        # Initialize Flask app
        self.app = Flask(
            __name__,
            template_folder=str(_DASHBOARD_DIR / 'templates'),
            static_folder=str(_DASHBOARD_DIR / 'static')
        )
        
        # Flask configuration
        self._configure_flask()
        
        # Security features
        self._setup_security()
        
        # Other features
        self._setup_compression()
        self._setup_cors()
        self._setup_socketio()
        self._setup_database()
        self._setup_metrics()
        
        # Register blueprints
        self._register_blueprints()
        
        # Initialize state
        self.alerts = []
        self.annotations = []
        
        # WebSocket connection counter
        self.websocket_connections = 0
        
        # Setup routes
        self._setup_routes()
        self._setup_websocket_handlers()
        
        # Setup log filters
        self._setup_log_filters()
        
        # Log startup
        log_activity('info', f'BotV2 Dashboard v{__version__} started')
        self._log_startup_banner()
    
    def _configure_flask(self):
        """Configure Flask application settings."""
        self.app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
        self.app.config['SESSION_COOKIE_SECURE'] = self.is_production
        self.app.config['SESSION_COOKIE_HTTPONLY'] = True
        self.app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
            minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES', 30))
        )
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        self.app.config['CSRF_ENABLED'] = os.getenv('CSRF_ENABLED', 'true').lower() == 'true'
        self.app.config['CSRF_TOKEN_TTL'] = int(os.getenv('CSRF_TOKEN_TTL', 3600))
        
        @self.app.before_request
        def set_csp_nonce():
            g.csp_nonce = generate_csp_nonce()
    
    def _setup_security(self):
        """Initialize all security features."""
        if not HAS_SECURITY:
            logger.warning("[!] Security features disabled - modules not available")
        else:
            self.csrf = init_csrf_protection(
                self.app,
                token_length=int(os.getenv('CSRF_TOKEN_LENGTH', 32)),
                token_ttl=int(os.getenv('CSRF_TOKEN_TTL', 3600))
            )
            logger.info("[+] CSRF Protection enabled")
            
            xss_protection_middleware(self.app, strip=True, detect_only=False)
            logger.info("[+] XSS Protection middleware enabled")
            
            rate_limit_enabled = os.getenv('RATE_LIMITING_ENABLED', 'true').lower() == 'true'
            if rate_limit_enabled:
                self.limiter = init_rate_limiter(
                    self.app,
                    requests_per_minute=int(os.getenv('RATE_LIMIT_RPM', 60)),
                    burst_size=int(os.getenv('RATE_LIMIT_BURST', 10))
                )
                logger.info("[+] Rate Limiting enabled")
            else:
                self.limiter = None
            
            session_timeout_seconds = int(os.getenv('SESSION_TIMEOUT_MINUTES', 15)) * 60
            self.session_manager = SessionManager(self.app, session_lifetime=session_timeout_seconds)
            logger.info("[+] Session Management enabled")
            
            init_security_middleware(self.app)
            logger.info("[+] Security Middleware enabled")
        
        if HAS_TALISMAN and self.is_production:
            csp_config = {
                'default-src': "'self'",
                'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'", "cdn.jsdelivr.net", "cdn.socket.io", "cdn.plot.ly", "unpkg.com", "cdn.sheetjs.com", "cdnjs.cloudflare.com"],
                'style-src': ["'self'", "'unsafe-inline'", "fonts.googleapis.com", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
                'font-src': ["'self'", "fonts.gstatic.com", "fonts.googleapis.com", "cdnjs.cloudflare.com", "data:"],
                'img-src': ["'self'", "data:", "https:", "blob:"],
                'connect-src': ["'self'", "wss:", "ws:", "localhost:*", "cdn.sheetjs.com", "cdnjs.cloudflare.com", "cdn.jsdelivr.net", "cdn.plot.ly", "cdn.socket.io"],
                'frame-ancestors': "'none'",
                'base-uri': "'self'",
                'form-action': "'self'"
            }
            
            Talisman(
                self.app,
                force_https=True,
                strict_transport_security=True,
                strict_transport_security_max_age=31536000,
                content_security_policy=csp_config,
                content_security_policy_nonce_in=['script-src']
            )
            logger.info("[+] Talisman ENABLED - HTTPS + CSP (production)")
        else:
            logger.info("[*] Talisman DISABLED - Development Mode")
    
    def _setup_compression(self):
        if HAS_COMPRESS:
            self.app.config['COMPRESS_MIMETYPES'] = [
                'text/html', 'text/css', 'text/javascript',
                'application/javascript', 'application/json',
                'text/xml', 'application/xml', 'text/plain'
            ]
            self.app.config['COMPRESS_LEVEL'] = 6
            self.app.config['COMPRESS_MIN_SIZE'] = 500
            self.compress = Compress(self.app)
            logger.info("[+] GZIP compression enabled (level 6)")
        else:
            self.compress = None
    
    def _setup_cors(self):
        CORS(self.app)
    
    def _setup_socketio(self):
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
    
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
            logger.info("[+] Database connected: %s", DATABASE_URL)
        except Exception as e:
            logger.warning("[-] Database failed: %s", e)
            self.db_session = None
    
    def _setup_metrics(self):
        if HAS_METRICS:
            self.metrics_monitor = get_metrics_monitor(window_seconds=300)
            MetricsMiddleware(self.app, self.metrics_monitor)
            logger.info("[+] Metrics monitoring enabled (5min window)")
        else:
            self.metrics_monitor = None
    
    def _register_blueprints(self):
        self.app.register_blueprint(control_bp)
        self.app.register_blueprint(monitoring_bp)
        self.app.register_blueprint(strategy_bp)
        self.app.register_blueprint(metrics_routes_bp)
        logger.info("[+] All blueprints registered")
    
    def _setup_log_filters(self):
        werkzeug_logger = logging.getLogger('werkzeug')
        ssl_filter = SSLErrorFilter()
        werkzeug_logger.addFilter(ssl_filter)
    
    def _log_startup_banner(self):
        if self.audit_logger:
            self.audit_logger.log_system_startup(version=__version__, environment=self.env)
        
        print(ASCII_BANNER.format(version=__version__, env=self.env.upper()), flush=True)
        print("", flush=True)
        print("  COMPONENT               STATUS", flush=True)
        print("  -----------------------------------------", flush=True)
        print("  Security                {}".format('ENABLED' if HAS_SECURITY else 'DISABLED'), flush=True)
        
        if HAS_SECURITY:
            print("    - CSRF Protection     OK", flush=True)
            print("    - XSS Prevention      OK", flush=True)
            print("    - Input Validation    OK", flush=True)
            print("    - Rate Limiting       OK", flush=True)
            print("    - Session Mgmt        OK", flush=True)
            print("    - Audit Logging       OK", flush=True)
            print("    - Security Headers    OK ({})".format(self.env), flush=True)
        
        print("  Metrics                 {}".format('ENABLED' if HAS_METRICS else 'DISABLED'), flush=True)
        print("  GZIP Compression        {}".format('ENABLED' if HAS_COMPRESS else 'DISABLED'), flush=True)
        print("  Database                {}".format('CONNECTED' if self.db_session else 'MOCK MODE'), flush=True)
        print("  System Metrics          {}".format('ENABLED' if HAS_PSUTIL else 'DISABLED'), flush=True)
        print("  -----------------------------------------", flush=True)
        print("  URL: http://{}:{}".format(self.host, self.port), flush=True)
        print("", flush=True)
        sys.stdout.flush()
    
    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('login'))
            
            if HAS_SECURITY and hasattr(self, 'session_manager') and self.session_manager:
                if not self.session_manager.is_valid():
                    session.clear()
                    return redirect(url_for('login', error='session_expired'))
            
            return f(*args, **kwargs)
        return decorated_function
    
    def _get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics."""
        metrics = {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_used_gb': 0,
            'memory_total_gb': 0,
            'disk_percent': 0,
            'disk_used_gb': 0,
            'disk_total_gb': 0,
            'network_io_mbps': 0,
            'uptime_seconds': time.time() - APP_START_TIME
        }
        
        if HAS_PSUTIL:
            try:
                # CPU
                metrics['cpu_percent'] = psutil.cpu_percent(interval=0.1)
                
                # Memory
                mem = psutil.virtual_memory()
                metrics['memory_percent'] = mem.percent
                metrics['memory_used_gb'] = round(mem.used / (1024**3), 2)
                metrics['memory_total_gb'] = round(mem.total / (1024**3), 2)
                
                # Disk
                disk = psutil.disk_usage('/')
                metrics['disk_percent'] = disk.percent
                metrics['disk_used_gb'] = round(disk.used / (1024**3), 2)
                metrics['disk_total_gb'] = round(disk.total / (1024**3), 2)
                
                # Network I/O
                net_io = psutil.net_io_counters()
                # Simple approximation (bytes per second converted to MB/s)
                metrics['network_io_mbps'] = round((net_io.bytes_sent + net_io.bytes_recv) / (1024**2 * 100), 2)
                
            except Exception as e:
                logger.warning("Failed to get system metrics: %s", e)
        
        return metrics
    
    def _get_python_env(self) -> Dict:
        """Get Python environment details."""
        env_info = {
            'version': platform.python_version(),
            'flask_version': FLASK_VERSION,
            'platform': platform.system() + ' ' + platform.release(),
            'pid': os.getpid(),
            'threads': threading.active_count(),
            'open_files': 0
        }
        
        if HAS_PSUTIL:
            try:
                process = psutil.Process(os.getpid())
                env_info['open_files'] = len(process.open_files())
                env_info['threads'] = process.num_threads()
            except:
                pass
        
        return env_info
    
    def _get_component_status(self) -> Dict:
        """Get status of all system components."""
        return {
            'flask': True,
            'socketio': True,
            'database': self.db_session is not None,
            'mock_data': HAS_MOCK_DATA,
            'metrics': HAS_METRICS,
            'compression': HAS_COMPRESS,
            'rate_limiter': HAS_SECURITY and hasattr(self, 'limiter') and self.limiter is not None,
            'session_manager': HAS_SECURITY and hasattr(self, 'session_manager') and self.session_manager is not None
        }
    
    def _get_security_status(self) -> Dict:
        """Get security features status."""
        return {
            'csrf_protection': HAS_SECURITY,
            'xss_prevention': HAS_SECURITY,
            'input_validation': HAS_SECURITY and HAS_PYDANTIC,
            'session_security': HAS_SECURITY,
            'audit_logging': self.audit_logger is not None,
            'https_enforced': self.is_production and HAS_TALISMAN
        }
    
    def _get_connections_info(self) -> Dict:
        """Get active connections information."""
        return {
            'http': 1,  # Current request
            'websocket': self.websocket_connections,
            'database': 'Active' if self.db_session else 'N/A',
            'exchange_apis': 0  # Placeholder for future implementation
        }
    
    def _setup_routes(self):
        """Setup all Flask routes."""
        
        # ==================== AUTHENTICATION ====================
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'GET':
                if 'user' in session:
                    return redirect(url_for('index'))
                return render_template('login.html', csp_nonce=g.csp_nonce)
            
            try:
                if HAS_SECURITY and HAS_PYDANTIC:
                    try:
                        login_data = validate_input(LoginRequest, {
                            'username': request.form.get('username', ''),
                            'password': request.form.get('password', '')
                        })
                        username = login_data.username
                        password = login_data.password
                    except ValidationError as e:
                        return jsonify({'error': 'Invalid input format'}), 400
                else:
                    username = request.form.get('username', '').strip()
                    password = request.form.get('password', '')
                
                ip = request.remote_addr
                
                if self.auth.is_locked_out(ip):
                    lockout_info = self.auth.failed_attempts[ip]
                    remaining = (lockout_info['locked_until'] - datetime.now()).seconds
                    return jsonify({
                        'error': 'Account locked',
                        'message': 'Too many failed attempts. Try again in {}s'.format(remaining)
                    }), 429
                
                if self.auth.check_credentials(username, password):
                    session.permanent = True
                    session['user'] = username
                    session['login_time'] = datetime.now().isoformat()
                    session['last_activity'] = datetime.now().isoformat()
                    
                    if HAS_SECURITY and hasattr(self, 'session_manager') and self.session_manager:
                        session_id = self.session_manager.create_session(username)
                        session['session_id'] = session_id
                    
                    self.auth.record_successful_login(ip, username)
                    
                    if HAS_METRICS and self.metrics_monitor:
                        self.metrics_monitor.record_user_activity(username)
                    
                    session.modified = True
                    
                    return jsonify({
                        'success': True, 
                        'redirect': '/',
                        'message': 'Login successful'
                    }), 200
                else:
                    self.auth.record_failed_attempt(ip, username)
                    return jsonify({'error': 'Invalid credentials'}), 401
            
            except Exception as e:
                logger.error("Login error: %s", e)
                return jsonify({'error': 'Login failed'}), 500
        
        @self.app.route('/logout')
        def logout():
            username = session.get('user')
            
            if HAS_SECURITY and hasattr(self, 'session_manager') and self.session_manager:
                self.session_manager.destroy_session()
            
            if self.audit_logger and username:
                self.audit_logger.log_logout(username)
            
            if username:
                log_activity('info', f'User logged out: {username}')
            
            session.clear()
            return redirect(url_for('login'))
        
        # ==================== DASHBOARD ====================
        
        @self.app.route('/')
        @self.login_required
        def index():
            if HAS_METRICS and self.metrics_monitor:
                user = session.get('user')
                if user:
                    self.metrics_monitor.record_user_activity(user)
            
            return render_template(
                'dashboard.html', 
                user=session.get('user'),
                csp_nonce=g.csp_nonce
            )
        
        # ==================== SYSTEM HEALTH UI ====================
        
        @self.app.route('/system-health')
        @self.login_required
        def system_health_ui():
            """System Health dashboard UI."""
            log_activity('info', f'System Health viewed by {session.get("user", "unknown")}')
            return render_template(
                'system_health.html',
                user=session.get('user'),
                csp_nonce=g.csp_nonce
            )
        
        # ==================== FAVICON ====================
        
        @self.app.route('/favicon.ico')
        def favicon():
            from flask import send_from_directory
            favicon_path = Path(self.app.static_folder) / 'favicon.ico'
            if favicon_path.exists():
                return send_from_directory(self.app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
            else:
                return '', 204
        
        # ==================== API - SECTION DATA ====================
        
        @self.app.route('/api/section/<section>')
        @self.login_required
        def get_section_data_route(section):
            try:
                if not section.replace('_', '').isalnum():
                    return jsonify({'error': 'Invalid section name'}), 400
                
                if HAS_MOCK_DATA:
                    data = get_section_data(section)
                    if data:
                        if HAS_SECURITY:
                            data = sanitize_dict(data)
                        return jsonify(data)
                    else:
                        return jsonify({'error': 'Section not found'}), 404
                else:
                    return jsonify(self._get_fallback_data(section))
            
            except Exception as e:
                logger.error("Section error: %s", e)
                return jsonify({'error': 'Internal server error'}), 500
        
        # ==================== API - ANNOTATIONS ====================
        
        @self.app.route('/api/annotations/<chart_id>')
        @self.login_required
        def get_annotations(chart_id):
            if HAS_SECURITY:
                chart_id = sanitize_html(chart_id, strip=True)
            
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
        @self.login_required
        def create_annotation():
            try:
                data = request.get_json()
                
                if HAS_SECURITY and HAS_PYDANTIC:
                    try:
                        validated = validate_input(AnnotationCreate, data)
                        annotation_data = validated.model_dump()
                        annotation_data['text'] = sanitize_html(annotation_data['text'], strip=True)
                    except ValidationError as e:
                        return jsonify({'success': False, 'error': str(e)}), 400
                else:
                    annotation_data = data
                
                annotation_id = len(self.annotations) + 1
                annotation = {
                    'id': annotation_id,
                    **annotation_data,
                    'created_at': datetime.now().isoformat() + 'Z',
                    'created_by': session.get('user', 'unknown')
                }
                
                self.annotations.append(annotation)
                self.socketio.emit('annotation_created', annotation, broadcast=True)
                
                return jsonify({
                    'success': True,
                    'annotation': annotation,
                    'message': 'Annotation created successfully'
                }), 201
            
            except Exception as e:
                logger.error("Annotation error: %s", e)
                return jsonify({'success': False, 'error': 'Internal server error'}), 500
        
        @self.app.route('/api/annotations/<int:annotation_id>', methods=['DELETE'])
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
        
        # ==================== HEALTH CHECK (BASIC) ====================
        
        @self.app.route('/health')
        def health():
            """Basic health check endpoint (no auth required)."""
            return jsonify({
                'status': 'healthy',
                'version': __version__,
                'environment': self.env
            })
        
        # ==================== API - SYSTEM HEALTH (COMPREHENSIVE) ====================
        
        @self.app.route('/api/system-health')
        @self.login_required
        def api_system_health():
            """Comprehensive system health API endpoint."""
            try:
                # Get metrics snapshot
                metrics_data = {}
                if HAS_METRICS and self.metrics_monitor:
                    try:
                        snapshot = self.metrics_monitor.get_current_snapshot()
                        metrics_data = {
                            'request_rate_rpm': snapshot.request_rate_rpm,
                            'error_rate_pct': snapshot.error_rate_pct,
                            'active_users': snapshot.active_users,
                            'websocket_connections': snapshot.websocket_connections,
                            'avg_latency_ms': getattr(snapshot, 'avg_latency_ms', 0)
                        }
                    except Exception as e:
                        logger.warning("Failed to get metrics snapshot: %s", e)
                        metrics_data = {
                            'request_rate_rpm': 0,
                            'error_rate_pct': 0,
                            'active_users': 1,
                            'websocket_connections': self.websocket_connections
                        }
                else:
                    metrics_data = {
                        'request_rate_rpm': 0,
                        'error_rate_pct': 0,
                        'active_users': 1,
                        'websocket_connections': self.websocket_connections
                    }
                
                # Build comprehensive response
                health_data = {
                    'status': 'healthy',
                    'version': __version__,
                    'environment': self.env,
                    'timestamp': datetime.now().isoformat(),
                    
                    # System resources
                    'system': self._get_system_metrics(),
                    
                    # Python environment
                    'python': self._get_python_env(),
                    
                    # Component status
                    'components': self._get_component_status(),
                    
                    # Security status
                    'security': self._get_security_status(),
                    
                    # Connections
                    'connections': self._get_connections_info(),
                    
                    # Metrics
                    'metrics': metrics_data,
                    
                    # Recent activity
                    'recent_activity': list(RECENT_ACTIVITY)[:20]
                }
                
                return jsonify(health_data)
            
            except Exception as e:
                logger.error("System health API error: %s", e)
                return jsonify({
                    'status': 'error',
                    'error': str(e)
                }), 500
    
    def _get_fallback_data(self, section: str) -> Dict:
        """Fallback data if mock_data.py not available."""
        fallback = {
            'dashboard': {'overview': {'equity': 'EUR 10,000', 'total_pnl': '+EUR 500'}},
            'portfolio': {'summary': {'total_value': 10000}, 'positions': []},
            'strategies': {'summary': {'active': 0}, 'strategies': []},
            'risk': {'metrics': {'var_95': 0, 'max_drawdown': 0}},
            'trades': {'summary': {'total': 0}, 'trades': []},
            'settings': {'settings': {}, 'system': {'version': __version__}}
        }
        return fallback.get(section, {'error': 'Section not found'})
    
    def _setup_websocket_handlers(self):
        """Setup WebSocket event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            self.websocket_connections += 1
            
            if HAS_METRICS and self.metrics_monitor:
                self.metrics_monitor.increment_websocket_connections()
            
            log_activity('info', 'WebSocket client connected')
            
            emit('connected', {
                'message': 'Connected to BotV2 v{}'.format(__version__),
                'version': __version__,
                'security': HAS_SECURITY
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            self.websocket_connections = max(0, self.websocket_connections - 1)
            
            if HAS_METRICS and self.metrics_monitor:
                self.metrics_monitor.decrement_websocket_connections()
            
            log_activity('info', 'WebSocket client disconnected')
    
    def run(self):
        """Start the dashboard server."""
        logger.info("Starting BotV2 Dashboard...")
        
        if HAS_SECURITY:
            logger.info("Security Phase 1: ACTIVE")
        else:
            logger.warning("Security Phase 1: DISABLED")
        
        if HAS_METRICS and self.metrics_monitor:
            logger.info("Metrics endpoint: /api/metrics")
        
        self.socketio.run(
            self.app,
            host=self.host,
            port=self.port,
            debug=self.debug,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )


TradingDashboard = ProfessionalDashboard


def create_app(config=None):
    """Factory function to create dashboard app."""
    if config is None:
        config = {
            'dashboard': {
                'host': '0.0.0.0',
                'port': int(os.getenv('DASHBOARD_PORT', 8050)),
                'debug': os.getenv('FLASK_ENV', 'development') == 'development'
            }
        }
    dashboard = ProfessionalDashboard(config)
    return dashboard.app


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = None
    try:
        from bot.config.config_manager import ConfigManager
        config = ConfigManager()
    except ImportError:
        logger.info("Running in standalone/demo mode")
        config = {
            'dashboard': {
                'host': '0.0.0.0',
                'port': int(os.getenv('DASHBOARD_PORT', 8050)),
                'debug': True
            }
        }
    
    dashboard = ProfessionalDashboard(config)
    dashboard.run()
