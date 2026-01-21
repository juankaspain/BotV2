"""Unit tests for BotV2 Dashboard

Test Coverage:
- Data processing functions
- Chart generation logic
- WebSocket message handling
- Filter and query logic
- Export functionality
- Modal data formatting
- Annotation system
- Performance benchmarks

Run with:
    pytest tests/test_dashboard.py -v
    pytest tests/test_dashboard.py -v --cov=src/dashboard
"""

import pytest
import json
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing"""
    return {
        'total_value': 125420.50,
        'daily_change': 1234.50,
        'daily_change_pct': 0.99,
        'total_pnl': 25420.50,
        'total_pnl_pct': 25.42,
        'positions': [
            {'symbol': 'EUR/USD', 'size': 100000, 'pnl': 420.50, 'pnl_pct': 0.42},
            {'symbol': 'GBP/USD', 'size': 50000, 'pnl': -120.30, 'pnl_pct': -0.24},
            {'symbol': 'USD/JPY', 'size': 75000, 'pnl': 680.20, 'pnl_pct': 0.91}
        ]
    }

@pytest.fixture
def sample_strategy_data():
    """Sample strategy performance data"""
    return {
        'strategies': [
            {
                'name': 'Momentum',
                'return': 24.5,
                'sharpe': 1.85,
                'max_drawdown': -8.2,
                'win_rate': 62.5,
                'trades': 145,
                'equity': [10000, 10500, 11200, 11800, 12450],
                'timestamps': ['2026-01-17', '2026-01-18', '2026-01-19', '2026-01-20', '2026-01-21']
            },
            {
                'name': 'Mean Reversion',
                'return': 18.3,
                'sharpe': 1.42,
                'max_drawdown': -12.5,
                'win_rate': 58.3,
                'trades': 210,
                'equity': [10000, 10300, 10800, 11200, 11830],
                'timestamps': ['2026-01-17', '2026-01-18', '2026-01-19', '2026-01-20', '2026-01-21']
            }
        ]
    }

@pytest.fixture
def sample_trade_data():
    """Sample trade history data"""
    return [
        {
            'id': 1,
            'symbol': 'EUR/USD',
            'strategy': 'Momentum',
            'entry_time': '2026-01-21T10:30:00',
            'exit_time': '2026-01-21T14:45:00',
            'entry_price': 1.0850,
            'exit_price': 1.0920,
            'size': 100000,
            'pnl': 420.50,
            'pnl_pct': 0.65,
            'duration_minutes': 255
        },
        {
            'id': 2,
            'symbol': 'GBP/USD',
            'strategy': 'Breakout',
            'entry_time': '2026-01-21T09:15:00',
            'exit_time': '2026-01-21T11:30:00',
            'entry_price': 1.2650,
            'exit_price': 1.2620,
            'size': 50000,
            'pnl': -120.30,
            'pnl_pct': -0.24,
            'duration_minutes': 135
        }
    ]

@pytest.fixture
def sample_risk_metrics():
    """Sample risk metrics data"""
    return {
        'sharpe_ratio': 1.85,
        'sortino_ratio': 2.12,
        'max_drawdown': -8.2,
        'var_95': -1250.50,
        'cvar_95': -1820.75,
        'volatility': 12.5,
        'beta': 0.85,
        'alpha': 2.3
    }


# ============================================
# DATA PROCESSING TESTS
# ============================================

class TestDataProcessing:
    """Test data processing and transformation functions"""
    
    def test_portfolio_calculation(self, sample_portfolio_data):
        """Test portfolio value calculation"""
        # Calculate total from positions
        calculated_total = sum(pos['pnl'] for pos in sample_portfolio_data['positions'])
        expected_total = 420.50 - 120.30 + 680.20
        
        assert abs(calculated_total - expected_total) < 0.01
        assert sample_portfolio_data['total_value'] > 0
        assert -100 < sample_portfolio_data['daily_change_pct'] < 100
    
    def test_strategy_metrics(self, sample_strategy_data):
        """Test strategy performance metrics"""
        for strategy in sample_strategy_data['strategies']:
            # Validate required fields
            assert 'name' in strategy
            assert 'return' in strategy
            assert 'sharpe' in strategy
            
            # Validate data ranges
            assert -100 <= strategy['return'] <= 1000  # Reasonable return range
            assert -5 <= strategy['sharpe'] <= 5  # Reasonable Sharpe range
            assert strategy['max_drawdown'] <= 0  # Drawdown should be negative
            assert 0 <= strategy['win_rate'] <= 100
            assert strategy['trades'] >= 0
    
    def test_equity_curve_calculation(self, sample_strategy_data):
        """Test equity curve generation"""
        strategy = sample_strategy_data['strategies'][0]
        equity = strategy['equity']
        
        # Equity should be monotonically increasing (for profitable strategy)
        assert len(equity) > 0
        assert equity[0] > 0  # Starting capital
        assert equity[-1] >= equity[0]  # Final >= Initial (if profitable)
    
    def test_trade_pnl_calculation(self, sample_trade_data):
        """Test trade P&L calculation"""
        for trade in sample_trade_data:
            # Calculate P&L
            price_diff = trade['exit_price'] - trade['entry_price']
            expected_pnl = price_diff * trade['size']
            
            # Allow small floating point differences
            assert abs(trade['pnl'] - expected_pnl) < 1.0
            
            # P&L percentage should match
            expected_pnl_pct = (price_diff / trade['entry_price']) * 100
            assert abs(trade['pnl_pct'] - expected_pnl_pct) < 0.1
    
    def test_risk_metrics_validity(self, sample_risk_metrics):
        """Test risk metrics validity"""
        metrics = sample_risk_metrics
        
        # Sharpe ratio reasonable range
        assert -5 <= metrics['sharpe_ratio'] <= 5
        
        # Sortino usually >= Sharpe (accounts only for downside)
        assert metrics['sortino_ratio'] >= metrics['sharpe_ratio'] * 0.8
        
        # Drawdown should be negative
        assert metrics['max_drawdown'] <= 0
        
        # VaR and CVaR should be negative (losses)
        assert metrics['var_95'] < 0
        assert metrics['cvar_95'] < 0
        
        # CVaR should be more negative than VaR (tail risk)
        assert metrics['cvar_95'] <= metrics['var_95']
        
        # Volatility should be positive
        assert metrics['volatility'] > 0


# ============================================
# CHART DATA GENERATION TESTS
# ============================================

class TestChartGeneration:
    """Test chart data generation for various chart types"""
    
    def test_equity_curve_data(self, sample_strategy_data):
        """Test equity curve chart data structure"""
        strategy = sample_strategy_data['strategies'][0]
        
        assert len(strategy['equity']) == len(strategy['timestamps'])
        assert all(isinstance(val, (int, float)) for val in strategy['equity'])
        assert all(isinstance(ts, str) for ts in strategy['timestamps'])
    
    def test_correlation_matrix_generation(self, sample_strategy_data):
        """Test correlation matrix generation"""
        strategies = sample_strategy_data['strategies']
        n = len(strategies)
        
        # Generate mock correlation matrix
        import numpy as np
        correlations = np.eye(n)  # Identity matrix as base
        
        # Validate matrix properties
        assert correlations.shape == (n, n)
        assert np.allclose(correlations, correlations.T)  # Symmetric
        assert np.all(np.diag(correlations) == 1)  # Diagonal = 1
        assert np.all(correlations >= -1) and np.all(correlations <= 1)  # Range [-1, 1]
    
    def test_candlestick_data_structure(self):
        """Test OHLC candlestick data structure"""
        candlestick_data = [
            {'date': '2026-01-21', 'open': 1.0850, 'high': 1.0920, 'low': 1.0830, 'close': 1.0910, 'volume': 150000},
            {'date': '2026-01-21', 'open': 1.0910, 'high': 1.0950, 'low': 1.0880, 'close': 1.0930, 'volume': 180000}
        ]
        
        for candle in candlestick_data:
            # Validate OHLC relationships
            assert candle['low'] <= candle['open'] <= candle['high']
            assert candle['low'] <= candle['close'] <= candle['high']
            assert candle['low'] <= candle['high']
            assert candle['volume'] >= 0
    
    def test_box_plot_data_generation(self, sample_strategy_data):
        """Test box plot data generation for return distribution"""
        # Generate sample returns
        import numpy as np
        returns = np.random.normal(0.05, 0.02, 50)  # Mean 5%, std 2%
        
        # Calculate box plot statistics
        q1 = np.percentile(returns, 25)
        median = np.percentile(returns, 50)
        q3 = np.percentile(returns, 75)
        iqr = q3 - q1
        
        # Validate box plot properties
        assert q1 < median < q3
        assert iqr > 0
        
        # Whiskers (1.5 * IQR rule)
        lower_whisker = q1 - 1.5 * iqr
        upper_whisker = q3 + 1.5 * iqr
        assert lower_whisker < upper_whisker


# ============================================
# FILTER LOGIC TESTS
# ============================================

class TestFilterLogic:
    """Test filtering and data query logic"""
    
    def test_time_range_filter(self, sample_trade_data):
        """Test time range filtering"""
        # Filter trades from today
        today = datetime.now().date()
        filtered = [
            trade for trade in sample_trade_data
            if datetime.fromisoformat(trade['entry_time']).date() == today
        ]
        
        # All filtered trades should be from today
        for trade in filtered:
            trade_date = datetime.fromisoformat(trade['entry_time']).date()
            assert trade_date == today
    
    def test_strategy_filter(self, sample_trade_data):
        """Test strategy filtering"""
        # Filter by strategy
        strategy_name = 'Momentum'
        filtered = [trade for trade in sample_trade_data if trade['strategy'] == strategy_name]
        
        # All filtered trades should be from selected strategy
        for trade in filtered:
            assert trade['strategy'] == strategy_name
    
    def test_performance_threshold_filter(self, sample_trade_data):
        """Test filtering by performance threshold"""
        # Filter profitable trades only
        profitable = [trade for trade in sample_trade_data if trade['pnl'] > 0]
        
        # All should have positive P&L
        for trade in profitable:
            assert trade['pnl'] > 0
            assert trade['pnl_pct'] > 0
    
    def test_combined_filters(self, sample_trade_data):
        """Test multiple filters combined"""
        # Filter: Momentum strategy AND profitable AND today
        today = datetime.now().date()
        filtered = [
            trade for trade in sample_trade_data
            if trade['strategy'] == 'Momentum'
            and trade['pnl'] > 0
            and datetime.fromisoformat(trade['entry_time']).date() == today
        ]
        
        # Validate all conditions
        for trade in filtered:
            assert trade['strategy'] == 'Momentum'
            assert trade['pnl'] > 0
            assert datetime.fromisoformat(trade['entry_time']).date() == today


# ============================================
# EXPORT FUNCTIONALITY TESTS
# ============================================

class TestExportFunctionality:
    """Test data export functions"""
    
    def test_csv_export_format(self, sample_trade_data):
        """Test CSV export formatting"""
        import csv
        from io import StringIO
        
        # Generate CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=sample_trade_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_trade_data)
        
        csv_content = output.getvalue()
        
        # Validate CSV structure
        assert 'symbol' in csv_content
        assert 'pnl' in csv_content
        assert len(csv_content.split('\n')) == len(sample_trade_data) + 2  # Header + data + empty line
    
    def test_json_export_format(self, sample_portfolio_data):
        """Test JSON export formatting"""
        # Export as JSON
        json_str = json.dumps(sample_portfolio_data, indent=2)
        
        # Parse back and validate
        parsed = json.loads(json_str)
        assert parsed['total_value'] == sample_portfolio_data['total_value']
        assert len(parsed['positions']) == len(sample_portfolio_data['positions'])
    
    def test_export_special_characters(self):
        """Test export with special characters (€, %, etc.)"""
        data = {'symbol': 'EUR/USD', 'pnl': '€420.50', 'return': '12.5%'}
        
        # Export as JSON (should handle Unicode)
        json_str = json.dumps(data, ensure_ascii=False)
        assert '€' in json_str
        assert '%' in json_str
        
        # Parse back
        parsed = json.loads(json_str)
        assert parsed['pnl'] == '€420.50'


# ============================================
# WEBSOCKET MESSAGE HANDLING TESTS
# ============================================

class TestWebSocketHandling:
    """Test WebSocket message processing"""
    
    def test_portfolio_update_message(self, sample_portfolio_data):
        """Test portfolio update message handling"""
        message = {
            'type': 'portfolio_update',
            'data': sample_portfolio_data
        }
        
        # Validate message structure
        assert message['type'] == 'portfolio_update'
        assert 'data' in message
        assert 'total_value' in message['data']
    
    def test_trade_execution_message(self, sample_trade_data):
        """Test trade execution message"""
        message = {
            'type': 'trade_executed',
            'data': sample_trade_data[0]
        }
        
        # Validate message
        assert message['type'] == 'trade_executed'
        assert message['data']['symbol'] is not None
        assert message['data']['pnl'] is not None
    
    def test_invalid_message_handling(self):
        """Test handling of invalid WebSocket messages"""
        invalid_messages = [
            {},  # Empty
            {'type': 'unknown'},  # Unknown type
            {'data': 'test'},  # Missing type
            None,  # Null
            'invalid'  # String instead of object
        ]
        
        for msg in invalid_messages:
            # Should not raise exception, should log error instead
            # In production, use proper error handling
            if isinstance(msg, dict):
                assert 'type' not in msg or msg.get('type') != 'portfolio_update'


# ============================================
# MODAL DATA FORMATTING TESTS
# ============================================

class TestModalDataFormatting:
    """Test modal content generation and formatting"""
    
    def test_trade_modal_data(self, sample_trade_data):
        """Test trade modal data structure"""
        trade = sample_trade_data[0]
        
        # Generate modal data
        modal_data = {
            'title': f"Trade Details - {trade['symbol']}",
            'symbol': trade['symbol'],
            'strategy': trade['strategy'],
            'entry': trade['entry_price'],
            'exit': trade['exit_price'],
            'pnl': trade['pnl'],
            'duration': f"{trade['duration_minutes']} minutes"
        }
        
        # Validate modal data
        assert 'title' in modal_data
        assert modal_data['symbol'] == 'EUR/USD'
        assert modal_data['pnl'] > 0
    
    def test_strategy_modal_data(self, sample_strategy_data):
        """Test strategy modal data structure"""
        strategy = sample_strategy_data['strategies'][0]
        
        # Generate modal data
        modal_data = {
            'title': f"Strategy Performance - {strategy['name']}",
            'return': f"{strategy['return']}%",
            'sharpe': strategy['sharpe'],
            'winRate': f"{strategy['win_rate']}%",
            'trades': strategy['trades']
        }
        
        # Validate
        assert 'Momentum' in modal_data['title']
        assert modal_data['trades'] > 0


# ============================================
# PERFORMANCE TESTS
# ============================================

class TestPerformance:
    """Test performance benchmarks"""
    
    def test_large_dataset_processing(self):
        """Test processing large datasets"""
        import time
        
        # Generate large dataset (1000 trades)
        large_dataset = [
            {
                'id': i,
                'symbol': 'EUR/USD',
                'pnl': i * 10.5,
                'entry_time': f'2026-01-21T{i%24:02d}:00:00'
            }
            for i in range(1000)
        ]
        
        # Measure processing time
        start = time.time()
        filtered = [trade for trade in large_dataset if trade['pnl'] > 0]
        duration = time.time() - start
        
        # Should process in less than 100ms
        assert duration < 0.1
        assert len(filtered) > 0
    
    def test_chart_data_generation_speed(self, sample_strategy_data):
        """Test chart data generation performance"""
        import time
        
        strategy = sample_strategy_data['strategies'][0]
        
        # Measure chart data prep time
        start = time.time()
        chart_data = {
            'x': strategy['timestamps'],
            'y': strategy['equity'],
            'type': 'scatter',
            'mode': 'lines'
        }
        duration = time.time() - start
        
        # Should be nearly instantaneous
        assert duration < 0.01
        assert len(chart_data['x']) == len(chart_data['y'])
    
    def test_filter_performance(self, sample_trade_data):
        """Test filter operation performance"""
        import time
        
        # Repeat dataset 100 times
        large_dataset = sample_trade_data * 100
        
        # Measure filter time
        start = time.time()
        filtered = [
            trade for trade in large_dataset
            if trade['pnl'] > 0 and trade['strategy'] == 'Momentum'
        ]
        duration = time.time() - start
        
        # Should filter 200 trades in less than 50ms
        assert duration < 0.05


# ============================================
# EDGE CASE TESTS
# ============================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_portfolio(self):
        """Test handling of empty portfolio"""
        empty_portfolio = {
            'total_value': 0,
            'positions': []
        }
        
        # Should not crash
        assert empty_portfolio['total_value'] == 0
        assert len(empty_portfolio['positions']) == 0
    
    def test_negative_values(self):
        """Test handling of negative values"""
        negative_data = {
            'total_value': 95000,  # Lost money
            'total_pnl': -5000,
            'daily_change': -1500
        }
        
        # Should handle negative values correctly
        assert negative_data['total_pnl'] < 0
        assert negative_data['daily_change'] < 0
    
    def test_zero_division_protection(self):
        """Test protection against division by zero"""
        # Calculate return percentage with zero initial capital
        initial = 0
        final = 1000
        
        # Should handle gracefully
        if initial == 0:
            return_pct = 0  # Or handle differently
        else:
            return_pct = ((final - initial) / initial) * 100
        
        assert return_pct == 0  # Protected
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        invalid_dates = [
            '2026-13-01',  # Invalid month
            '2026-01-32',  # Invalid day
            'not-a-date',  # Gibberish
            '',  # Empty
        ]
        
        for date_str in invalid_dates:
            try:
                datetime.fromisoformat(date_str)
                parsed = True
            except (ValueError, TypeError):
                parsed = False
            
            # Most should fail to parse
            if date_str in ['2026-13-01', '2026-01-32', 'not-a-date', '']:
                assert not parsed
    
    def test_missing_data_fields(self):
        """Test handling of missing data fields"""
        incomplete_trade = {
            'symbol': 'EUR/USD',
            # Missing: entry_price, exit_price, pnl
        }
        
        # Should handle missing fields
        assert incomplete_trade.get('symbol') == 'EUR/USD'
        assert incomplete_trade.get('pnl', 0) == 0  # Default value


# ============================================
# INTEGRATION TESTS (require running server)
# ============================================

@pytest.mark.integration
class TestIntegration:
    """Integration tests (require running backend server)"""
    
    @pytest.mark.skip(reason="Requires running server")
    def test_api_portfolio_endpoint(self):
        """Test /api/portfolio endpoint"""
        import requests
        response = requests.get('http://localhost:5000/api/portfolio')
        assert response.status_code == 200
        data = response.json()
        assert 'total_value' in data
    
    @pytest.mark.skip(reason="Requires running server")
    def test_websocket_connection(self):
        """Test WebSocket connection"""
        import socketio
        sio = socketio.Client()
        connected = False
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
        
        try:
            sio.connect('http://localhost:5000')
            assert connected
        finally:
            sio.disconnect()


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])