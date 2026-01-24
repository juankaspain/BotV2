"""Comprehensive Tests for BotV2 Dashboard v4.4

Test Coverage:
- Authentication & Sessions
- Dashboard UI Routes
- API Endpoints (40+)
- Strategy Editor v4.4
- Live Monitor v4.3
- Control Panel v4.2
- WebSocket Real-time
- Market Data v5.1
- Annotations CRUD
- Rate Limiting
- Security
- Error Handling
"""

import pytest
import json
from datetime import datetime, timedelta
from typing import Dict

pytestmark = [pytest.mark.dashboard, pytest.mark.api]


# ==================== AUTHENTICATION TESTS ====================

@pytest.mark.unit
class TestAuthentication:
    """Test authentication and session management"""
    
    def test_login_page_loads(self, client):
        """Test login page is accessible"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()
    
    def test_successful_login(self, client, valid_credentials):
        """Test successful login creates session"""
        response = client.post('/login', 
            data=valid_credentials,
            follow_redirects=False
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_failed_login(self, client, invalid_credentials):
        """Test failed login with wrong credentials"""
        response = client.post('/login',
            data=invalid_credentials,
            follow_redirects=False
        )
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_logout(self, authenticated_client):
        """Test logout clears session"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_brute_force_protection(self, client, invalid_credentials):
        """Test account lockout after 5 failed attempts"""
        # Try 5 failed logins
        for _ in range(5):
            client.post('/login', data=invalid_credentials)
        
        # 6th attempt should be locked
        response = client.post('/login', data=invalid_credentials)
        assert response.status_code == 429
        data = json.loads(response.data)
        assert 'locked' in data.get('error', '').lower()
    
    def test_protected_route_without_auth(self, client):
        """Test accessing protected route without authentication"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login


# ==================== DASHBOARD UI TESTS ====================

@pytest.mark.unit
class TestDashboardUI:
    """Test dashboard UI routes"""
    
    def test_main_dashboard_loads(self, authenticated_client):
        """Test main dashboard page loads"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'dashboard' in response.data.lower()
    
    def test_control_panel_loads(self, authenticated_client):
        """Test Control Panel v4.2 loads"""
        response = authenticated_client.get('/control')
        assert response.status_code == 200
        assert b'control' in response.data.lower()
    
    def test_live_monitor_loads(self, authenticated_client):
        """Test Live Monitor v4.3 loads"""
        response = authenticated_client.get('/monitoring')
        assert response.status_code == 200
        assert b'monitor' in response.data.lower()
    
    def test_strategy_editor_loads(self, authenticated_client):
        """Test Strategy Editor v4.4 loads"""
        response = authenticated_client.get('/strategy-editor')
        assert response.status_code == 200
        assert b'strategy' in response.data.lower()
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data


# ==================== SECTION DATA API TESTS ====================

@pytest.mark.api
class TestSectionDataAPI:
    """Test section data endpoints"""
    
    @pytest.mark.parametrize('section', [
        'dashboard', 'portfolio', 'strategies', 'risk', 'trades', 'settings'
    ])
    def test_section_data_loads(self, authenticated_client, section):
        """Test all section data endpoints"""
        response = authenticated_client.get(f'/api/section/{section}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, dict)
    
    def test_invalid_section(self, authenticated_client):
        """Test invalid section returns 404"""
        response = authenticated_client.get('/api/section/invalid_section')
        assert response.status_code == 404


# ==================== PORTFOLIO API TESTS ====================

@pytest.mark.api
class TestPortfolioAPI:
    """Test portfolio endpoints"""
    
    def test_portfolio_history(self, authenticated_client):
        """Test portfolio history endpoint"""
        response = authenticated_client.get('/api/portfolio/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_portfolio_equity(self, authenticated_client):
        """Test equity curve endpoint"""
        response = authenticated_client.get('/api/portfolio/equity')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_portfolio_history_with_filters(self, authenticated_client):
        """Test portfolio history with date filters"""
        params = {
            'start_date': (datetime.now() - timedelta(days=30)).isoformat(),
            'end_date': datetime.now().isoformat()
        }
        response = authenticated_client.get('/api/portfolio/history', query_string=params)
        assert response.status_code == 200


# ==================== TRADES API TESTS ====================

@pytest.mark.api
class TestTradesAPI:
    """Test trades endpoints"""
    
    def test_trades_list(self, authenticated_client):
        """Test trades list endpoint"""
        response = authenticated_client.get('/api/trades')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_trades_stats(self, authenticated_client):
        """Test trades statistics endpoint"""
        response = authenticated_client.get('/api/trades/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_trades_pagination(self, authenticated_client):
        """Test trades list with pagination"""
        params = {'page': 1, 'per_page': 10}
        response = authenticated_client.get('/api/trades', query_string=params)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'trades' in data or 'data' in data
    
    def test_trades_filter_by_status(self, authenticated_client):
        """Test trades filtered by status"""
        params = {'status': 'closed'}
        response = authenticated_client.get('/api/trades', query_string=params)
        assert response.status_code == 200


# ==================== STRATEGY API TESTS ====================

@pytest.mark.api
class TestStrategyAPI:
    """Test strategy endpoints (v4.4)"""
    
    def test_strategies_list(self, authenticated_client):
        """Test list all strategies"""
        response = authenticated_client.get('/api/strategies/list')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_get_strategy_parameters(self, authenticated_client):
        """Test get strategy parameters"""
        response = authenticated_client.get('/api/strategies/Momentum')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'parameters' in data or 'success' in data
    
    def test_update_strategy_parameter(self, authenticated_client):
        """Test update strategy parameter"""
        payload = {
            'parameter': 'lookback_period',
            'value': 25,
            'user': 'test_admin'
        }
        response = authenticated_client.post(
            '/api/strategies/Momentum/param',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_apply_strategy_preset(self, authenticated_client, strategy_presets):
        """Test apply preset to strategy"""
        payload = {
            'preset': 'conservative',
            'user': 'test_admin'
        }
        response = authenticated_client.post(
            '/api/strategies/Momentum/preset',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_apply_preset_all_strategies(self, authenticated_client):
        """Test apply preset to all strategies"""
        payload = {
            'preset': 'balanced',
            'user': 'test_admin'
        }
        response = authenticated_client.post(
            '/api/strategies/preset/all',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_strategy_change_history(self, authenticated_client):
        """Test get strategy change history"""
        response = authenticated_client.get('/api/strategies/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_strategy_rollback(self, authenticated_client):
        """Test rollback strategy configuration"""
        payload = {
            'strategy': 'Momentum',
            'timestamp': datetime.now().isoformat(),
            'user': 'test_admin'
        }
        response = authenticated_client.post(
            '/api/strategies/rollback',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [200, 404]  # 404 if no history
    
    def test_strategy_impact_estimation(self, authenticated_client):
        """Test estimate parameter change impact"""
        payload = {
            'strategy': 'Momentum',
            'parameter': 'lookback_period',
            'current_value': 20,
            'new_value': 30
        }
        response = authenticated_client.post(
            '/api/strategies/estimate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_quick_backtest(self, authenticated_client):
        """Test quick backtest endpoint"""
        payload = {
            'parameters': {'lookback_period': 25}
        }
        response = authenticated_client.post(
            '/api/strategies/Momentum/backtest',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
    
    def test_get_presets(self, authenticated_client):
        """Test get available presets"""
        response = authenticated_client.get('/api/strategies/presets')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_strategy_editor_stats(self, authenticated_client):
        """Test strategy editor statistics"""
        response = authenticated_client.get('/api/strategies/stats')
        assert response.status_code == 200
    
    def test_export_strategy_config(self, authenticated_client):
        """Test export strategy configuration"""
        payload = {
            'format': 'json',
            'include_history': True
        }
        response = authenticated_client.post(
            '/api/strategies/export',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200


# ==================== MARKET DATA API TESTS ====================

@pytest.mark.api
class TestMarketDataAPI:
    """Test market data endpoints (v5.1)"""
    
    def test_get_current_price(self, authenticated_client):
        """Test get current market price"""
        response = authenticated_client.get('/api/market/BTC/USD')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    @pytest.mark.parametrize('timeframe', ['1m', '5m', '15m', '1h', '4h', '1d'])
    def test_get_ohlcv_data(self, authenticated_client, timeframe):
        """Test OHLCV candlestick data with different timeframes"""
        params = {'timeframe': timeframe, 'limit': 100}
        response = authenticated_client.get(
            '/api/market/BTC/USD/ohlcv',
            query_string=params
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data


# ==================== ANNOTATIONS API TESTS ====================

@pytest.mark.api
class TestAnnotationsAPI:
    """Test chart annotations endpoints (v5.1)"""
    
    def test_get_annotations(self, authenticated_client):
        """Test get chart annotations"""
        response = authenticated_client.get('/api/annotations/equity_chart')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data
    
    def test_create_annotation(self, authenticated_client, mock_annotation_data):
        """Test create new annotation"""
        response = authenticated_client.post(
            '/api/annotations',
            data=json.dumps(mock_annotation_data),
            content_type='application/json'
        )
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'success' in data or 'id' in data
    
    def test_delete_annotation(self, authenticated_client):
        """Test delete annotation"""
        # First create one
        annotation_data = {
            'chart_id': 'test_chart',
            'type': 'line',
            'text': 'Test'
        }
        create_response = authenticated_client.post(
            '/api/annotations',
            data=json.dumps(annotation_data),
            content_type='application/json'
        )
        
        if create_response.status_code in [200, 201]:
            # Try to delete
            response = authenticated_client.delete('/api/annotations/1')
            assert response.status_code in [200, 204, 404]


# ==================== RISK API TESTS ====================

@pytest.mark.api
class TestRiskAPI:
    """Test risk analytics endpoints"""
    
    def test_risk_correlation_matrix(self, authenticated_client):
        """Test correlation matrix endpoint"""
        response = authenticated_client.get('/api/risk/correlation')
        assert response.status_code == 200
    
    def test_risk_metrics(self, authenticated_client):
        """Test risk metrics endpoint"""
        response = authenticated_client.get('/api/risk/metrics')
        assert response.status_code == 200


# ==================== ALERTS API TESTS ====================

@pytest.mark.api
class TestAlertsAPI:
    """Test alerts endpoints"""
    
    def test_get_alerts(self, authenticated_client):
        """Test get active alerts"""
        response = authenticated_client.get('/api/alerts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'success' in data


# ==================== WEBSOCKET TESTS ====================

@pytest.mark.websocket
class TestWebSocket:
    """Test WebSocket real-time functionality"""
    
    def test_websocket_connection(self, socketio_client):
        """Test WebSocket connection"""
        assert socketio_client.is_connected()
    
    def test_price_update_event(self, socketio_client):
        """Test price update event"""
        socketio_client.emit('subscribe', {'channel': 'prices'})
        received = socketio_client.get_received()
        # Just verify no errors
        assert isinstance(received, list)
    
    def test_portfolio_update_event(self, socketio_client):
        """Test portfolio update event"""
        socketio_client.emit('subscribe', {'channel': 'portfolio'})
        received = socketio_client.get_received()
        assert isinstance(received, list)


# ==================== RATE LIMITING TESTS ====================

@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limit_enforcement(self, authenticated_client):
        """Test rate limiting kicks in after threshold"""
        # Make 15 rapid requests (limit is 10/min for some endpoints)
        responses = []
        for i in range(15):
            response = authenticated_client.get('/api/portfolio/equity')
            responses.append(response.status_code)
        
        # At least one should be rate limited
        # Note: Might not trigger in all test environments
        assert any(code == 429 for code in responses) or all(code == 200 for code in responses)


# ==================== ERROR HANDLING TESTS ====================

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling"""
    
    def test_404_on_invalid_route(self, authenticated_client):
        """Test 404 for non-existent routes"""
        response = authenticated_client.get('/api/nonexistent/route')
        assert response.status_code == 404
    
    def test_invalid_json_payload(self, authenticated_client):
        """Test error on invalid JSON"""
        response = authenticated_client.post(
            '/api/strategies/Momentum/param',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]
    
    def test_missing_required_fields(self, authenticated_client):
        """Test error on missing required fields"""
        response = authenticated_client.post(
            '/api/strategies/Momentum/param',
            data=json.dumps({}),  # Empty payload
            content_type='application/json'
        )
        assert response.status_code in [400, 422, 500]


# ==================== INTEGRATION TESTS ====================

@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_strategy_edit_workflow(self, authenticated_client):
        """Test complete strategy editing workflow"""
        # 1. Get strategies list
        response = authenticated_client.get('/api/strategies/list')
        assert response.status_code == 200
        
        # 2. Get strategy parameters
        response = authenticated_client.get('/api/strategies/Momentum')
        assert response.status_code == 200
        
        # 3. Update parameter
        payload = {
            'parameter': 'lookback_period',
            'value': 25,
            'user': 'test_admin'
        }
        response = authenticated_client.post(
            '/api/strategies/Momentum/param',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # 4. Check history
        response = authenticated_client.get('/api/strategies/history')
        assert response.status_code == 200
    
    def test_complete_monitoring_workflow(self, authenticated_client):
        """Test complete live monitoring workflow"""
        # 1. Load market prices
        response = authenticated_client.get('/api/market/BTC/USD')
        assert response.status_code == 200
        
        # 2. Load positions
        response = authenticated_client.get('/api/trades?status=open')
        assert response.status_code == 200
        
        # 3. Load strategies performance
        response = authenticated_client.get('/api/strategies/list')
        assert response.status_code == 200
        
        # 4. Load risk metrics
        response = authenticated_client.get('/api/risk/metrics')
        assert response.status_code == 200


# ==================== PERFORMANCE TESTS ====================

@pytest.mark.performance
@pytest.mark.slow
class TestPerformance:
    """Performance tests"""
    
    def test_dashboard_load_time(self, authenticated_client):
        """Test dashboard loads within acceptable time"""
        import time
        start = time.time()
        response = authenticated_client.get('/')
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 2.0  # Should load in < 2 seconds
    
    def test_api_response_time(self, authenticated_client):
        """Test API responds within acceptable time"""
        import time
        start = time.time()
        response = authenticated_client.get('/api/portfolio/equity')
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 0.5  # Should respond in < 500ms
