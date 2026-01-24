# 🧪 BotV2 Test Suite

**Comprehensive test coverage for BotV2 Dashboard v4.4**

---

## 🚀 Quick Start

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_dashboard_v4_4.py -v
```

---

## 📁 Test Files

### Dashboard Tests 🖥️

| File | Description | Coverage |
|------|-------------|----------|
| `test_dashboard_v4_4.py` | Dashboard v4.4 comprehensive tests (NEW) | ✅ Complete |
| `test_dashboard.py` | General dashboard functionality | ✅ Complete |
| `test_dashboard_security.py` | Security and auth tests | ✅ Complete |

### Strategy Tests 🎯

| File | Description | Coverage |
|------|-------------|----------|
| `test_strategies.py` | Strategy execution tests | ✅ Complete |
| `test_trailing_stops.py` | Trailing stop functionality | ✅ Complete |

### System Tests ⚙️

| File | Description | Coverage |
|------|-------------|----------|
| `test_circuit_breaker.py` | Circuit breaker patterns | ✅ Complete |
| `test_recovery_system.py` | Error recovery | ✅ Complete |
| `test_latency_simulator.py` | Latency simulation | ✅ Complete |

### Risk Tests 🛡️

| File | Description | Coverage |
|------|-------------|----------|
| `test_risk_manager.py` | Risk management | ✅ Complete |
| `test_data_validation.py` | Input validation | ✅ Complete |
| `test_malicious_data.py` | Security validation | ✅ Complete |
| `test_malicious_data_detector.py` | Attack detection | ✅ Complete |

### Integration Tests 🔗

| File | Description | Coverage |
|------|-------------|----------|
| `test_integration.py` | Component integration | ✅ Complete |

### Notification Tests 🔔

| File | Description | Coverage |
|------|-------------|----------|
| `test_notification_system.py` | Full notification system | ✅ Complete |
| `test_notifications.py` | Basic notifications | ✅ Complete |

---

## 🧬 Fixtures (`conftest.py`)

### Configuration
- `test_config` - Complete test configuration
- `temp_dir` - Temporary directory
- `config_file` - Temporary config file
- `test_env_vars` - Test environment variables (auto-use)

### Flask App
- `app` - Flask application instance
- `client` - Flask test client
- `authenticated_client` - Pre-authenticated client
- `socketio_client` - SocketIO test client

### Database
- `db_engine` - In-memory SQLite engine
- `db_session` - Database session
- `populated_db` - Database with sample data

### Mock Data
- `mock_portfolio_data` - Portfolio data
- `mock_trade_data` - Trade data
- `mock_strategy_data` - Strategy configuration
- `mock_market_data` - Market price data
- `mock_ohlcv_data` - Candlestick data
- `mock_annotation_data` - Chart annotations

### Generators
- `sample_trades(count)` - Generate N trades
- `sample_portfolio_history(days)` - Generate history
- `performance_metrics` - Performance data

### Security
- `valid_credentials` - Valid login
- `invalid_credentials` - Invalid login
- `malicious_payloads` - Attack vectors

---

## 🏷️ Test Markers

```python
@pytest.mark.unit          # Fast, isolated tests
@pytest.mark.integration   # Multi-component tests
@pytest.mark.e2e           # End-to-end workflows
@pytest.mark.slow          # Slow tests (>1s)
@pytest.mark.security      # Security tests
@pytest.mark.performance   # Performance tests
@pytest.mark.dashboard     # Dashboard tests
@pytest.mark.api           # API tests
@pytest.mark.websocket     # WebSocket tests
```

### Running by Marker

```bash
# Unit tests only
pytest -m unit

# API tests only
pytest -m api

# Everything except slow tests
pytest -m "not slow"

# Dashboard and API tests
pytest -m "dashboard or api"
```

---

## 📊 Coverage

### Generate Coverage Report

```bash
# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=src --cov-report=term-missing

# XML for CI
pytest --cov=src --cov-report=xml
```

### Coverage Targets

- **Overall**: 90%+
- **Dashboard**: 95%+
- **API**: 90%+
- **Strategies**: 85%+

---

## ⚡ Performance

### Parallel Execution

```bash
# Use 4 workers
pytest -n 4

# Auto-detect CPUs
pytest -n auto
```

### Fast Subset

```bash
# Run only fast tests
pytest -m "unit and not slow"

# Skip integration and e2e
pytest -m "not integration and not e2e"
```

---

## 🐛 Debugging

### Debug Failed Tests

```bash
# Stop on first failure
pytest -x

# Show local variables
pytest -l

# Enter debugger on failure
pytest --pdb

# Verbose output
pytest -vv
```

### Print Output

```bash
# Show print statements
pytest -s

# Show captured logs
pytest --log-cli-level=INFO
```

---

## 🔍 Troubleshooting

### Import Errors

```bash
# Ensure project root in PYTHONPATH
export PYTHONPATH=.
pytest
```

### Database Errors

```bash
# Use in-memory database
export DATABASE_URL=sqlite:///:memory:
pytest
```

### Permission Errors

```bash
# Clean up __pycache__ and .pytest_cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
```

### Fixture Not Found

```bash
# List all available fixtures
pytest --fixtures

# List fixtures used by specific test
pytest --fixtures-per-test tests/test_dashboard_v4_4.py
```

---

## 📝 Writing New Tests

### Test Template

```python
import pytest
import json

pytestmark = pytest.mark.unit


class TestMyFeature:
    """Test my new feature"""
    
    def test_feature_success(self, authenticated_client):
        """Test feature succeeds"""
        # Arrange
        payload = {'key': 'value'}
        
        # Act
        response = authenticated_client.post(
            '/api/endpoint',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
```

### Best Practices

1. ✅ Use descriptive test names
2. ✅ Test one thing per test
3. ✅ Use fixtures for setup
4. ✅ Use AAA pattern (Arrange-Act-Assert)
5. ✅ Test edge cases and errors
6. ✅ Keep tests fast (< 1s)
7. ✅ Mark slow tests with `@pytest.mark.slow`
8. ✅ Document complex scenarios

---

## 📚 Additional Documentation

- [Complete Testing Guide](../docs/TESTING_GUIDE.md) - Comprehensive guide
- [Audit Report](../docs/AUDIT_REPORT_v4.4.md) - System audit
- [pytest.ini](../pytest.ini) - Pytest configuration
- [requirements-dev.txt](../requirements-dev.txt) - Dev dependencies

---

## 📞 Support

Questions? Check:

1. This README
2. [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)
3. Existing test files for examples
4. Pytest documentation

---

**Last Updated:** January 24, 2026  
**Version:** 4.4  
**Maintained By:** Development Team