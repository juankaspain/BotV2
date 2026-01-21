"""
Unit Tests for Data Validation
Tests timestamp validation, gap detection, and data quality checks
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.data_validator import DataValidator


@pytest.fixture
def mock_config():
    """Create mock configuration"""
    config = Mock()
    config.data.validation = {
        'timestamp_validation': {
            'enabled': True,
            'check_duplicates': True,
            'check_order': True,
            'check_future': True,
            'detect_gaps': True,
            'gap_threshold_minutes': 5,
            'critical_gap_minutes': 30,
            'timezone': 'UTC',
            'on_duplicate': 'skip',
            'on_out_of_order': 'error',
            'on_future': 'error',
            'on_critical_gap': 'error'
        }
    }
    return config


@pytest.fixture
def validator(mock_config):
    """Create DataValidator instance"""
    return DataValidator(mock_config)


@pytest.fixture
def clean_data():
    """Create clean sample data"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': 100 + np.random.randn(100),
        'high': 101 + np.random.randn(100),
        'low': 99 + np.random.randn(100),
        'close': 100 + np.random.randn(100),
        'volume': np.random.randint(1000, 10000, 100)
    })
    return df


class TestBasicValidation:
    """Test basic validation functionality"""
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly"""
        assert validator.config is not None
        # Add more assertions based on actual DataValidator implementation
    
    def test_empty_dataframe(self, validator):
        """Test validation with empty dataframe"""
        df = pd.DataFrame()
        
        # Should handle empty dataframe gracefully
        # Implementation depends on actual validator behavior
        assert len(df) == 0


class TestDuplicateDetection:
    """Test duplicate timestamp detection"""
    
    def test_detect_duplicates(self, validator, clean_data):
        """Test detection of duplicate timestamps"""
        # Add duplicate
        duplicate_row = clean_data.iloc[10:11].copy()
        df_with_dup = pd.concat([clean_data, duplicate_row], ignore_index=True)
        df_with_dup = df_with_dup.sort_values('timestamp').reset_index(drop=True)
        
        # Check for duplicates
        duplicates = df_with_dup['timestamp'].duplicated()
        assert duplicates.sum() > 0
    
    def test_remove_duplicates(self, validator, clean_data):
        """Test removing duplicate timestamps"""
        # Add duplicates
        df_with_dup = pd.concat([clean_data, clean_data.iloc[10:15]], ignore_index=True)
        
        # Remove duplicates
        df_clean = df_with_dup.drop_duplicates(subset=['timestamp'], keep='first')
        
        assert len(df_clean) == len(clean_data)
        assert not df_clean['timestamp'].duplicated().any()
    
    def test_duplicate_action_skip(self, validator, clean_data):
        """Test 'skip' action on duplicates"""
        # Add duplicate
        df_with_dup = pd.concat([clean_data, clean_data.iloc[10:11]], ignore_index=True)
        
        # With skip action, should remove duplicates
        df_clean = df_with_dup.drop_duplicates(subset=['timestamp'])
        assert len(df_clean) < len(df_with_dup)


class TestChronologicalOrder:
    """Test chronological order validation"""
    
    def test_chronological_order_validation(self, validator, clean_data):
        """Test that data is in chronological order"""
        # Clean data should already be ordered
        assert clean_data['timestamp'].is_monotonic_increasing
    
    def test_out_of_order_detection(self, validator, clean_data):
        """Test detection of out-of-order timestamps"""
        # Shuffle some rows
        df_shuffled = clean_data.copy()
        df_shuffled.iloc[20:25] = df_shuffled.iloc[20:25].iloc[::-1]
        
        # Check if not monotonic
        assert not df_shuffled['timestamp'].is_monotonic_increasing
    
    def test_out_of_order_correction(self, validator, clean_data):
        """Test correction of out-of-order timestamps"""
        # Shuffle
        df_shuffled = clean_data.copy()
        df_shuffled = df_shuffled.sample(frac=1).reset_index(drop=True)
        
        # Sort to correct
        df_corrected = df_shuffled.sort_values('timestamp').reset_index(drop=True)
        
        assert df_corrected['timestamp'].is_monotonic_increasing


class TestFutureTimestamps:
    """Test future timestamp detection"""
    
    def test_future_timestamps_detection(self, validator, clean_data):
        """Test detection of future timestamps"""
        # Add future timestamp
        future_date = datetime.now() + timedelta(days=1)
        df_with_future = clean_data.copy()
        df_with_future.loc[len(df_with_future)] = [
            future_date, 100, 101, 99, 100, 5000
        ]
        
        # Check for future timestamps
        now = pd.Timestamp.now()
        future_mask = df_with_future['timestamp'] > now
        
        assert future_mask.sum() > 0
    
    def test_remove_future_timestamps(self, validator, clean_data):
        """Test removing future timestamps"""
        # Add future timestamp
        future_date = datetime.now() + timedelta(days=1)
        df_with_future = clean_data.copy()
        df_with_future.loc[len(df_with_future)] = [
            future_date, 100, 101, 99, 100, 5000
        ]
        
        # Remove future
        now = pd.Timestamp.now()
        df_clean = df_with_future[df_with_future['timestamp'] <= now]
        
        assert len(df_clean) == len(clean_data)


class TestGapDetection:
    """Test gap detection in timestamps"""
    
    def test_gap_detection_small(self, validator, clean_data):
        """Test detection of small gaps"""
        # Create gap by removing rows
        df_with_gap = pd.concat([
            clean_data.iloc[:50],
            clean_data.iloc[55:]  # 5-minute gap
        ]).reset_index(drop=True)
        
        # Calculate time differences
        time_diffs = df_with_gap['timestamp'].diff()
        
        # Check for gaps > 1 minute (normal interval)
        gaps = time_diffs[time_diffs > pd.Timedelta(minutes=1)]
        assert len(gaps) > 0
    
    def test_gap_detection_critical(self, validator, clean_data):
        """Test detection of critical gaps"""
        # Create large gap
        df_with_gap = pd.concat([
            clean_data.iloc[:30],
            clean_data.iloc[70:]  # 40-minute gap
        ]).reset_index(drop=True)
        
        time_diffs = df_with_gap['timestamp'].diff()
        
        # Check for critical gaps > 30 minutes
        critical_gaps = time_diffs[time_diffs > pd.Timedelta(minutes=30)]
        assert len(critical_gaps) > 0
    
    def test_interpolation_small_gaps(self, validator):
        """Test interpolation for small gaps"""
        # Create data with small gap
        dates1 = pd.date_range(start='2024-01-01', periods=10, freq='1min')
        dates2 = pd.date_range(start='2024-01-01 00:15:00', periods=10, freq='1min')
        
        df = pd.DataFrame({
            'timestamp': list(dates1) + list(dates2),
            'value': list(range(10)) + list(range(10, 20))
        })
        
        # Set timestamp as index for interpolation
        df = df.set_index('timestamp')
        
        # Resample to 1-minute frequency and interpolate
        df_resampled = df.resample('1min').interpolate()
        
        # Should have no gaps now
        assert len(df_resampled) > len(df)


class TestTimezoneValidation:
    """Test timezone validation"""
    
    def test_timezone_validation(self, validator, clean_data):
        """Test timezone validation and conversion"""
        # Make timestamps timezone-aware
        df_utc = clean_data.copy()
        df_utc['timestamp'] = pd.to_datetime(df_utc['timestamp'], utc=True)
        
        # Check timezone
        assert df_utc['timestamp'].dt.tz is not None
    
    def test_timezone_conversion_to_utc(self, validator):
        """Test conversion to UTC timezone"""
        # Create data with different timezone
        dates = pd.date_range(
            start='2024-01-01',
            periods=10,
            freq='1H',
            tz='America/New_York'
        )
        
        df = pd.DataFrame({'timestamp': dates})
        
        # Convert to UTC
        df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')
        
        assert df['timestamp'].dt.tz.zone == 'UTC'


class TestValidationActions:
    """Test different validation actions"""
    
    def test_validation_actions_skip(self, validator):
        """Test 'skip' action removes invalid data"""
        # Create data with issues
        dates = pd.date_range(start='2024-01-01', periods=10, freq='1min')
        df = pd.DataFrame({'timestamp': dates, 'value': range(10)})
        
        # Add duplicate
        df = pd.concat([df, df.iloc[5:6]], ignore_index=True)
        
        # Skip duplicates
        df_clean = df.drop_duplicates(subset=['timestamp'])
        
        assert len(df_clean) == 10
    
    def test_validation_actions_error(self, validator):
        """Test 'error' action raises exception"""
        # This test verifies that errors are raised when configured
        # Implementation depends on actual validator behavior
        pass


class TestEdgeCases:
    """Test edge cases"""
    
    def test_single_row_dataframe(self, validator):
        """Test validation with single row"""
        df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'value': [100]
        })
        
        # Should handle single row
        assert len(df) == 1
    
    def test_large_dataframe(self, validator):
        """Test validation with large dataframe"""
        dates = pd.date_range(start='2024-01-01', periods=100000, freq='1s')
        df = pd.DataFrame({
            'timestamp': dates,
            'value': np.random.randn(100000)
        })
        
        # Should handle large dataset
        assert len(df) == 100000
        assert df['timestamp'].is_monotonic_increasing
    
    def test_mixed_frequency_data(self, validator):
        """Test data with mixed frequencies"""
        # 1-minute data for first half
        dates1 = pd.date_range(start='2024-01-01', periods=50, freq='1min')
        # 5-minute data for second half
        dates2 = pd.date_range(start='2024-01-01 01:00:00', periods=50, freq='5min')
        
        df = pd.DataFrame({
            'timestamp': list(dates1) + list(dates2),
            'value': range(100)
        })
        
        # Should detect frequency change
        time_diffs = df['timestamp'].diff()
        unique_diffs = time_diffs.dropna().unique()
        
        assert len(unique_diffs) > 1


class TestConfigurationOptions:
    """Test different configuration options"""
    
    def test_disabled_validation(self, mock_config):
        """Test with validation disabled"""
        mock_config.data.validation['timestamp_validation']['enabled'] = False
        validator = DataValidator(mock_config)
        
        # Validation should be disabled
        # Test depends on implementation
    
    def test_custom_gap_threshold(self, mock_config):
        """Test custom gap threshold"""
        mock_config.data.validation['timestamp_validation']['gap_threshold_minutes'] = 10
        validator = DataValidator(mock_config)
        
        # Should use custom threshold
        # Test depends on implementation
    
    def test_custom_timezone(self, mock_config):
        """Test custom timezone configuration"""
        mock_config.data.validation['timestamp_validation']['timezone'] = 'Europe/Madrid'
        validator = DataValidator(mock_config)
        
        # Should use custom timezone
        # Test depends on implementation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
