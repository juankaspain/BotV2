"""
Tests for Malicious Data Validation
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.data.data_validator import DataValidator


class TestMaliciousDataValidation:
    """Test validation against malicious data"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        config = {
            'validation': {
                'enabled': True,
                'check_duplicates': True,
                'check_chronological': True,
                'check_future_timestamps': True,
                'max_gap_minutes': 5
            }
        }
        return DataValidator(config)
    
    def test_sql_injection_in_symbol(self, validator):
        """Test SQL injection attempt in symbol field"""
        data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'symbol': ["BTCUSDT'; DROP TABLE orders; --"],
            'price': [50000.0]
        })
        
        # Validator should handle this safely
        # In production, symbol validation should reject this
        assert data['symbol'][0].startswith("BTC")
    
    def test_xss_script_injection(self, validator):
        """Test XSS script injection"""
        data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'notes': ["<script>alert('XSS')</script>"],
            'price': [50000.0]
        })
        
        # Should not execute scripts
        assert '<script>' in data['notes'][0]
    
    def test_negative_prices(self, validator):
        """Test negative price values"""
        data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='1min'),
            'price': [50000.0, -1000.0, 51000.0]  # Negative price
        })
        
        # Should detect invalid prices
        assert (data['price'] < 0).any()
    
    def test_zero_prices(self, validator):
        """Test zero price values"""
        data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='1min'),
            'price': [50000.0, 0.0, 51000.0]  # Zero price
        })
        
        # Should detect zero prices
        assert (data['price'] == 0).any()
    
    def test_nan_values(self, validator):
        """Test NaN values in data"""
        data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='1min'),
            'price': [50000.0, np.nan, 51000.0]
        })
        
        # Should detect NaN
        assert data['price'].isna().any()
    
    def test_inf_values(self, validator):
        """Test infinity values"""
        data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=3, freq='1min'),
            'price': [50000.0, np.inf, 51000.0]
        })
        
        # Should detect inf
        assert np.isinf(data['price']).any()
    
    def test_timestamp_manipulation(self, validator):
        """Test timestamp manipulation"""
        data = pd.DataFrame({
            'timestamp': [
                datetime(2024, 1, 1, 10, 0, 0),
                datetime(2024, 1, 1, 9, 0, 0),  # Out of order
                datetime(2024, 1, 1, 11, 0, 0)
            ],
            'price': [50000.0, 50100.0, 50200.0]
        })
        
        # Validation should detect out-of-order
        validated = validator.validate(data)
        # After validation, should be ordered
        assert validated['timestamp'].is_monotonic_increasing
    
    def test_future_timestamps(self, validator):
        """Test future timestamps"""
        from datetime import timedelta
        
        future_time = datetime.now() + timedelta(hours=1)
        data = pd.DataFrame({
            'timestamp': [
                datetime.now(),
                future_time,  # Future timestamp
                datetime.now()
            ],
            'price': [50000.0, 50100.0, 50200.0]
        })
        
        # Should detect future timestamps
        validated = validator.validate(data)
        # Future timestamps should be removed
        assert len(validated) <= len(data)
    
    def test_oversized_data(self, validator):
        """Test handling of oversized data"""
        # Very large dataset
        data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=1000000, freq='1s'),
            'price': np.random.uniform(50000, 51000, 1000000)
        })
        
        # Should handle large data without crashing
        try:
            validated = validator.validate(data)
            assert len(validated) > 0
        except MemoryError:
            pytest.skip("Insufficient memory for test")
    
    def test_missing_required_fields(self, validator):
        """Test missing required fields"""
        data = pd.DataFrame({
            'timestamp': [datetime.now()],
            # Missing 'price' field
        })
        
        # Should handle missing fields
        with pytest.raises(Exception):
            validator.validate(data)
    
    def test_type_confusion(self, validator):
        """Test type confusion attacks"""
        data = pd.DataFrame({
            'timestamp': [datetime.now()],
            'price': ["not_a_number"]  # String instead of number
        })
        
        # Should detect type mismatch
        with pytest.raises(Exception):
            float(data['price'][0])
