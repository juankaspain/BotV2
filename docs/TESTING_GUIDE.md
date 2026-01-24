# 🧪 BotV2 Testing Guide

**Version:** 4.4  
**Last Updated:** January 24, 2026  
**Target Coverage:** 95%+

---

## 📑 Table of Contents

1. [Overview](#overview)
2. [Setup](#setup)
3. [Running Tests](#running-tests)
4. [Test Structure](#test-structure)
5. [Fixtures](#fixtures)
6. [Writing Tests](#writing-tests)
7. [Coverage](#coverage)
8. [CI/CD Integration](#cicd-integration)
9. [Best Practices](#best-practices)

---

## 🎯 Overview

### Test Pyramid

```
         ▲
        /E2E\         (~5%)   - End-to-end tests
       /-----\       
      /  INT  \      (~25%)  - Integration tests
     /---------\    
    /   UNIT    \   (~70%)  - Unit tests
   /-------------\ 
```

### Test Categories

- **Unit Tests** (`@pytest.mark.unit`): Fast, isolated component tests
- **Integration Tests** (`@pytest.mark.integration`): Multiple component interactions
- **E2E Tests** (`@pytest.mark.e2e`): Full system workflows
- **Security Tests** (`@pytest.mark.security`): Security vulnerability tests
- **Performance Tests** (`@pytest.mark.performance`): Performance benchmarks

### Coverage Targets

| Component | Target | Current |
|-----------|--------|----------|
| Dashboard | 95% | 🔶 TBD |
| API Endpoints | 90% | 🔶 TBD |
| Strategies | 85% | 🔶 TBD |
| Risk Manager | 90% | 🔶 TBD |
| Utils | 80% | 🔶 TBD |
| **Overall** | **90%** | **🔶 TBD** |

---

## 🔧 Setup

### 1. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development and testing dependencies
pip install -r requirements-dev.txt
```

### 2. Setup Environment

```bash
# Create .env.test file
cp .env.example .env.test

# Edit .env.test with test configuration
FLASK_ENV=testing
DATABASE_URL=sqlite:///:memory:
DASHBOARD_USERNAME=test_admin
DASHBOARD_PASSWORD=test_password_123
SECRET_KEY=test_secret_key_for_testing_only
```

### 3. Verify Installation

```bash
# Check pytest is installed
pytest --version

# Check coverage is installed
coverage --version

# List available test markers
pytest --markers
```

---

## ▶️ Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_dashboard_v4_4.py

# Run specific test class
pytest tests/test_dashboard_v4_4.py::TestAuthentication

# Run specific test function
pytest tests/test_dashboard_v4_4.py::TestAuthentication::test_login_page_loads
```

### By Markers

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run dashboard tests
pytest -m dashboard

# Run API tests
pytest -m api

# Exclude slow tests
pytest -m "not slow"

# Run security tests only
pytest -m security
```

### Parallel Execution

```bash
# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect number of CPUs
pytest -n auto
```

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file change
ptw
```

### With Coverage

```bash
# Run with coverage report
pytest --cov=src --cov-report=html

# Run with terminal coverage report
pytest --cov=src --cov-report=term-missing

# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

---

## 📁 Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py                      # Centralized fixtures
├── test_dashboard_v4_4.py           # Dashboard v4.4 tests ✅ NEW
├── test_dashboard.py                # General dashboard tests
├── test_dashboard_security.py       # Security tests
├── test_strategies.py               # Strategy tests
├── test_risk_manager.py             # Risk management tests
├── test_integration.py              # Integration tests
├── test_circuit_breaker.py          # Circuit breaker tests
├── test_recovery_system.py          # Recovery tests
├── test_notification_system.py      # Notification tests
└── ...
```

### Test File Naming

- **Unit tests**: `test_<module>.py`
- **Integration tests**: `test_<feature>_integration.py`
- **E2E tests**: `test_<workflow>_e2e.py`

### Test Function Naming

```python
def test_<what>_<when>_<then>():
    """Test that <what> <when> <then>"""
    pass

# Examples:
def test_login_with_valid_credentials_succeeds():
    pass

def test_strategy_update_with_invalid_value_fails():
    pass

def test_rate_limit_after_10_requests_returns_429():
    pass
```

---

## 🧬 Fixtures

### Available Fixtures

All fixtures are defined in [`tests/conftest.py`](../tests/conftest.py).

#### Configuration Fixtures

```python
@pytest.fixture
def test_config() -> Dict:
    """Complete test configuration"""

@pytest.fixture
def temp_dir() -> Path:
    """Temporary directory for tests"""

@pytest.fixture
def config_file(temp_dir) -> Path:
    """Temporary config file"""
```

#### Flask App Fixtures

```python
@pytest.fixture
def app() -> Flask:
    """Flask application instance"""

@pytest.fixture
def client(app) -> FlaskClient:
    """Flask test client"""

@pytest.fixture
def authenticated_client(client) -> FlaskClient:
    """Pre-authenticated Flask client"""

@pytest.fixture
def socketio_client(app) -> SocketIOTestClient:
    """SocketIO test client"""
```

#### Database Fixtures

```python
@pytest.fixture
def db_engine():
    """In-memory SQLite engine"""

@pytest.fixture
def db_session(db_engine) -> Session:
    """Database session"""

@pytest.fixture
def populated_db(db_session) -> Session:
    """Database with sample data"""
```

#### Mock Data Fixtures

```python
@pytest.fixture
def mock_portfolio_data() -> Dict:
    """Mock portfolio data"""

@pytest.fixture
def mock_trade_data() -> Dict:
    """Mock trade data"""

@pytest.fixture
def mock_strategy_data() -> Dict:
    """Mock strategy data"""

@pytest.fixture
def mock_market_data() -> Dict:
    """Mock market data"""

@pytest.fixture
def mock_ohlcv_data() -> List[Dict]:
    """Mock OHLCV candlestick data"""
```

#### Security Fixtures

```python
@pytest.fixture
def valid_credentials() -> Dict:
    """Valid login credentials"""

@pytest.fixture
def invalid_credentials() -> Dict:
    """Invalid login credentials"""

@pytest.fixture
def malicious_payloads() -> List[str]:
    """XSS, SQL injection, etc."""
```

### Using Fixtures

```python
def test_portfolio_endpoint(authenticated_client, mock_portfolio_data):
    """Test portfolio endpoint with mock data"""
    response = authenticated_client.get('/api/portfolio/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'equity' in data
```

---

## ✍️ Writing Tests

### Test Template

```python
import pytest
import json

pytestmark = pytest.mark.unit  # Mark all tests in file


class TestFeature:
    """Test feature description"""
    
    def test_feature_success_case(self, authenticated_client):
        """Test feature succeeds with valid input"""
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
    
    def test_feature_failure_case(self, authenticated_client):
        """Test feature fails with invalid input"""
        # Arrange
        payload = {}  # Invalid empty payload
        
        # Act
        response = authenticated_client.post(
            '/api/endpoint',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
```

### Parametrized Tests

```python
@pytest.mark.parametrize('timeframe,expected', [
    ('1m', 60),
    ('5m', 300),
    ('1h', 3600),
    ('1d', 86400),
])
def test_timeframe_conversion(timeframe, expected):
    """Test timeframe to seconds conversion"""
    result = convert_timeframe_to_seconds(timeframe)
    assert result == expected
```

### Testing Exceptions

```python
def test_invalid_strategy_raises_error():
    """Test that invalid strategy raises ValueError"""
    with pytest.raises(ValueError, match="Invalid strategy"):
        strategy = Strategy(name="Invalid")
        strategy.validate()
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_api_call_with_mock(mocker):
    """Test API call with mocked response"""
    # Mock external API
    mock_response = Mock()
    mock_response.json.return_value = {'price': 50000}
    
    with patch('requests.get', return_value=mock_response):
        price = fetch_market_price('BTC/USD')
        assert price == 50000
```

---

## 📊 Coverage

### Generating Coverage Reports

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Generate coverage badge
coverage-badge -o coverage.svg -f
```

### Coverage Requirements

- **Minimum**: 80% overall
- **Target**: 90% overall
- **Goal**: 95% overall

### Viewing Coverage

```bash
# Open HTML report
open htmlcov/index.html

# Terminal report
coverage report

# Show uncovered lines
coverage report --show-missing
```

### Excluding Code from Coverage

```python
if __name__ == '__main__':  # pragma: no cover
    main()

def debug_function():  # pragma: no cover
    """Debug only, not tested"""
    print("Debug info")
```

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest -m "unit and not slow"
        language: system
        pass_filenames: false
        always_run: true
```

---

## ✅ Best Practices

### DO's ✅

1. **Write tests first** (TDD)
2. **Keep tests simple** and focused
3. **Use descriptive names** for tests
4. **Test one thing** per test
5. **Use fixtures** for common setup
6. **Mock external dependencies**
7. **Test edge cases** and errors
8. **Keep tests fast** (< 1s per test)
9. **Maintain test independence**
10. **Document complex test scenarios**

### DON'Ts ❌

1. **Don't test implementation details**
2. **Don't write flaky tests**
3. **Don't ignore failing tests**
4. **Don't skip security tests**
5. **Don't hardcode test data**
6. **Don't test third-party libraries**
7. **Don't write slow tests** (mark as `@pytest.mark.slow`)
8. **Don't use production database**
9. **Don't share state between tests**
10. **Don't commit commented-out tests**

### Test Patterns

#### AAA Pattern (Arrange-Act-Assert)

```python
def test_feature():
    # Arrange - Setup test data
    user = User(username="test")
    
    # Act - Execute functionality
    result = user.authenticate("password")
    
    # Assert - Verify results
    assert result is True
```

#### Given-When-Then (BDD)

```python
def test_user_login():
    # Given a valid user
    user = create_user(username="test", password="pass123")
    
    # When they login with correct credentials
    response = login(username="test", password="pass123")
    
    # Then they should be authenticated
    assert response.status_code == 200
    assert response.session['user'] == "test"
```

---

## 📚 Resources

### Documentation

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)

### Tutorials

- [Effective Python Testing](https://realpython.com/pytest-python-testing/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

---

## 📞 Support

If you need help with testing:

1. Check this guide
2. Review existing tests in `tests/`
3. Check pytest documentation
4. Ask in team chat

---

**Last Updated:** January 24, 2026  
**Maintained By:** Development Team  
**Version:** 4.4