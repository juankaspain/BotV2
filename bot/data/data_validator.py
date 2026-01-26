"""
Data Validator
Comprehensive validation of market data
Checks: NaN, Inf, Outliers, OHLC consistency, Gaps, Timestamps
"""

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data_quality_score: float  # 0-1
    checks_passed: int
    checks_total: int


class DataValidator:
    """
    Validates market data quality
    All checks must pass for data to be considered valid
    """
    
    def __init__(self, config=None, outlier_threshold: float = 5.0):
        """
        Args:
            config: Configuration object with validation settings
            outlier_threshold: Standard deviations for outlier detection
        """
        self.outlier_threshold = outlier_threshold
        self.config = config
        
        # Timestamp validation settings
        if config and hasattr(config, 'data'):
            ts_config = config.data.validation.get('timestamp_validation', {})
            self.ts_enabled = ts_config.get('enabled', True)
            self.check_duplicates = ts_config.get('check_duplicates', True)
            self.check_order = ts_config.get('check_order', True)
            self.check_future = ts_config.get('check_future', True)
            self.max_gap_seconds = ts_config.get('max_gap_seconds', 300)
            self.allow_backfill = ts_config.get('allow_backfill', False)
            self.expected_tz = ts_config.get('timezone', 'UTC')
            
            gap_config = ts_config.get('gap_detection', {})
            self.gap_enabled = gap_config.get('enabled', True)
            self.critical_gap_seconds = gap_config.get('critical_gap_seconds', 600)
            self.gap_action = gap_config.get('action_on_critical', 'reject')
            self.max_interpolation = gap_config.get('max_interpolation_points', 5)
        else:
            # Defaults
            self.ts_enabled = True
            self.check_duplicates = True
            self.check_order = True
            self.check_future = True
            self.max_gap_seconds = 300
            self.allow_backfill = False
            self.expected_tz = 'UTC'
            self.gap_enabled = True
            self.critical_gap_seconds = 600
            self.gap_action = 'reject'
            self.max_interpolation = 5
        
        logger.info(
            f"✓ Data Validator initialized "
            f"(outlier_threshold={outlier_threshold}σ, timestamp_validation={self.ts_enabled})"
        )
    
    def validate_market_data(self, data: pd.DataFrame) -> ValidationResult:
        """
        Validate market OHLCV data
        
        Args:
            data: DataFrame with market data
            
        Returns:
            ValidationResult with details
        """
        
        errors = []
        warnings = []
        checks_passed = 0
        checks_total = 10  # Increased from 7 to 10
        
        # Check 1: NaN values
        if self._check_nan(data):
            checks_passed += 1
        else:
            nan_count = data.isna().sum().sum()
            errors.append(f"Found {nan_count} NaN values")
        
        # Check 2: Infinity values
        if self._check_infinity(data):
            checks_passed += 1
        else:
            inf_count = np.isinf(data.select_dtypes(include=[np.number]).values).sum()
            errors.append(f"Found {inf_count} infinity values")
        
        # Check 3: Required columns
        if self._check_required_columns(data):
            checks_passed += 1
        else:
            errors.append("Missing required columns (need: open, high, low, close)")
        
        # Check 4: OHLC consistency
        ohlc_result = self._check_ohlc_consistency(data)
        if ohlc_result['valid']:
            checks_passed += 1
        else:
            errors.extend(ohlc_result['errors'])
        
        # Check 5: Outlier detection
        outliers = self._detect_outliers(data)
        if len(outliers) == 0:
            checks_passed += 1
        else:
            warnings.append(f"Found {len(outliers)} potential outliers")
        
        # Check 6: Time gaps (original)
        gaps = self._detect_gaps(data)
        if len(gaps) == 0:
            checks_passed += 1
        else:
            warnings.append(f"Found {len(gaps)} data gaps")
        
        # Check 7: Volume validation
        if self._check_volume(data):
            checks_passed += 1
        else:
            warnings.append("Volume data suspicious (zeros or negatives)")
        
        # NEW Check 8: Timestamp duplicates
        if self.ts_enabled and self.check_duplicates:
            dup_result = self._check_timestamp_duplicates(data)
            if dup_result['valid']:
                checks_passed += 1
            else:
                errors.extend(dup_result['errors'])
        else:
            checks_passed += 1  # Skip if disabled
        
        # NEW Check 9: Timestamp order
        if self.ts_enabled and self.check_order:
            order_result = self._check_timestamp_order(data)
            if order_result['valid']:
                checks_passed += 1
            else:
                errors.extend(order_result['errors'])
        else:
            checks_passed += 1  # Skip if disabled
        
        # NEW Check 10: Future timestamps
        if self.ts_enabled and self.check_future:
            future_result = self._check_future_timestamps(data)
            if future_result['valid']:
                checks_passed += 1
            else:
                errors.extend(future_result['errors'])
        else:
            checks_passed += 1  # Skip if disabled
        
        # Calculate quality score
        quality_score = checks_passed / checks_total
        
        # Valid only if no errors and score >= 0.8
        is_valid = len(errors) == 0 and quality_score >= 0.8
        
        if not is_valid:
            logger.warning(
                f"Data validation failed: {len(errors)} errors, "
                f"score={quality_score:.2%}"
            )
            for error in errors:
                logger.error(f"  ❌ {error}")
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            data_quality_score=quality_score,
            checks_passed=checks_passed,
            checks_total=checks_total
        )
    
    def _check_nan(self, data: pd.DataFrame) -> bool:
        """Check for NaN values"""
        return not data.isna().any().any()
    
    def _check_infinity(self, data: pd.DataFrame) -> bool:
        """Check for infinity values"""
        numeric_data = data.select_dtypes(include=[np.number])
        return not np.isinf(numeric_data.values).any()
    
    def _check_required_columns(self, data: pd.DataFrame) -> bool:
        """Check if required columns exist"""
        required = ['open', 'high', 'low', 'close']
        return all(col in data.columns for col in required)
    
    def _check_ohlc_consistency(self, data: pd.DataFrame) -> Dict:
        """
        Validate OHLC relationships:
        - High >= Open, Close, Low
        - Low <= Open, Close, High
        """
        errors = []
        
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in data.columns for col in required_cols):
            return {'valid': False, 'errors': ["Missing OHLC columns"]}
        
        # High checks
        if (data['high'] < data['open']).any():
            count = (data['high'] < data['open']).sum()
            errors.append(f"High < Open in {count} rows")
        
        if (data['high'] < data['close']).any():
            count = (data['high'] < data['close']).sum()
            errors.append(f"High < Close in {count} rows")
        
        if (data['high'] < data['low']).any():
            count = (data['high'] < data['low']).sum()
            errors.append(f"High < Low in {count} rows")
        
        # Low checks
        if (data['low'] > data['open']).any():
            count = (data['low'] > data['open']).sum()
            errors.append(f"Low > Open in {count} rows")
        
        if (data['low'] > data['close']).any():
            count = (data['low'] > data['close']).sum()
            errors.append(f"Low > Close in {count} rows")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _detect_outliers(self, data: pd.DataFrame) -> List[int]:
        """
        Detect outliers using z-score method
        
        Returns:
            List of row indices with outliers
        """
        outlier_indices = []
        
        for col in ['close', 'volume']:
            if col not in data.columns:
                continue
            
            # Calculate z-scores
            mean = data[col].mean()
            std = data[col].std()
            
            if std == 0:
                continue
            
            z_scores = np.abs((data[col] - mean) / std)
            
            # Find outliers
            outliers = np.where(z_scores > self.outlier_threshold)[0]
            outlier_indices.extend(outliers.tolist())
        
        return list(set(outlier_indices))
    
    def _detect_gaps(self, data: pd.DataFrame) -> List[int]:
        """
        Detect time gaps in data
        
        Returns:
            List of row indices after gaps
        """
        gaps = []
        
        if 'timestamp' not in data.columns:
            return gaps
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            return gaps
        
        # Calculate time differences
        time_diffs = data['timestamp'].diff()
        
        # Get median difference
        median_diff = time_diffs.median()
        
        if pd.isna(median_diff):
            return gaps
        
        # Find gaps (>2x median)
        large_gaps = time_diffs > (2 * median_diff)
        gaps = data[large_gaps].index.tolist()
        
        return gaps
    
    def _check_volume(self, data: pd.DataFrame) -> bool:
        """Validate volume data"""
        
        if 'volume' not in data.columns:
            return True  # No volume to validate
        
        # Check for excessive zeros
        zero_ratio = (data['volume'] == 0).sum() / len(data)
        if zero_ratio > 0.1:  # >10% zeros is suspicious
            return False
        
        # Check for negatives
        if (data['volume'] < 0).any():
            return False
        
        return True
    
    # ========================================================================
    # NEW: Enhanced Timestamp Validation
    # ========================================================================
    
    def _check_timestamp_duplicates(self, data: pd.DataFrame) -> Dict:
        """
        Check for duplicate timestamps
        
        Returns:
            Dict with validation result
        """
        
        if 'timestamp' not in data.columns:
            return {'valid': True, 'errors': []}
        
        errors = []
        
        duplicates = data['timestamp'].duplicated()
        if duplicates.any():
            dup_count = duplicates.sum()
            dup_values = data.loc[duplicates, 'timestamp'].unique()[:5]  # First 5
            
            errors.append(
                f"Found {dup_count} duplicate timestamps. "
                f"Examples: {', '.join(str(t) for t in dup_values)}"
            )
            
            logger.warning(f"⚠️ Duplicate timestamps detected: {dup_count} occurrences")
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _check_timestamp_order(self, data: pd.DataFrame) -> Dict:
        """
        Check if timestamps are in chronological order
        
        Returns:
            Dict with validation result
        """
        
        if 'timestamp' not in data.columns:
            return {'valid': True, 'errors': []}
        
        errors = []
        
        # Ensure datetime type
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            errors.append("Timestamp column is not datetime type")
            return {'valid': False, 'errors': errors}
        
        # Check chronological order
        timestamps = data['timestamp'].values
        out_of_order = np.where(timestamps[1:] < timestamps[:-1])[0]
        
        if len(out_of_order) > 0:
            errors.append(
                f"Found {len(out_of_order)} out-of-order timestamps. "
                f"First occurrence at index {out_of_order[0]}"
            )
            logger.error(
                f"❌ Timestamps out of order: {len(out_of_order)} violations"
            )
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def _check_future_timestamps(self, data: pd.DataFrame) -> Dict:
        """
        Check for timestamps in the future (exchange errors)
        
        Returns:
            Dict with validation result
        """
        
        if 'timestamp' not in data.columns:
            return {'valid': True, 'errors': []}
        
        errors = []
        
        # Ensure datetime type
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            return {'valid': True, 'errors': []}  # Already caught elsewhere
        
        # Current time in UTC
        now = pd.Timestamp.now(tz='UTC')
        
        # Make timestamps timezone-aware if needed
        timestamps = data['timestamp']
        if timestamps.dt.tz is None:
            timestamps = timestamps.dt.tz_localize('UTC')
        
        # Find future timestamps (with 1 minute tolerance for clock skew)
        tolerance = pd.Timedelta(minutes=1)
        future_mask = timestamps > (now + tolerance)
        
        if future_mask.any():
            future_count = future_mask.sum()
            future_examples = timestamps[future_mask].head(3)
            
            errors.append(
                f"Found {future_count} future timestamps. "
                f"Examples: {', '.join(str(t) for t in future_examples)}"
            )
            
            logger.error(
                f"❌ Future timestamps detected: {future_count} occurrences "
                f"(possible exchange error)"
            )
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    def detect_critical_gaps(self, data: pd.DataFrame) -> Dict:
        """
        Detect critical gaps that require action
        
        Returns:
            Dict with gap information and recommended action
        """
        
        if 'timestamp' not in data.columns:
            return {'has_critical_gaps': False, 'gaps': [], 'action': None}
        
        if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
            return {'has_critical_gaps': False, 'gaps': [], 'action': None}
        
        critical_gaps = []
        
        # Calculate time differences in seconds
        time_diffs = data['timestamp'].diff().dt.total_seconds()
        
        # Find critical gaps
        for idx, diff in enumerate(time_diffs):
            if pd.notna(diff) and diff > self.critical_gap_seconds:
                critical_gaps.append({
                    'index': idx,
                    'gap_seconds': diff,
                    'gap_minutes': diff / 60,
                    'before': data['timestamp'].iloc[idx - 1],
                    'after': data['timestamp'].iloc[idx]
                })
        
        has_critical = len(critical_gaps) > 0
        
        if has_critical:
            logger.warning(
                f"⚠️ Critical gaps detected: {len(critical_gaps)} gaps "
                f"> {self.critical_gap_seconds}s"
            )
            
            for gap in critical_gaps[:3]:  # Log first 3
                logger.warning(
                    f"  Gap: {gap['gap_minutes']:.1f} min between "
                    f"{gap['before']} and {gap['after']}"
                )
        
        return {
            'has_critical_gaps': has_critical,
            'gaps': critical_gaps,
            'action': self.gap_action if has_critical else None,
            'total_gaps': len(critical_gaps)
        }
