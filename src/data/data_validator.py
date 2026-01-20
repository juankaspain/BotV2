"""
Data Validator
Comprehensive validation of market data
Checks: NaN, Inf, Outliers, OHLC consistency, Gaps
"""

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict

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
    
    def __init__(self, outlier_threshold: float = 5.0):
        """
        Args:
            outlier_threshold: Standard deviations for outlier detection
        """
        self.outlier_threshold = outlier_threshold
        
        logger.info(f"✓ Data Validator initialized (outlier_threshold={outlier_threshold}σ)")
    
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
        checks_total = 7
        
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
        
        # Check 6: Time gaps
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
        
        # Calculate quality score
        quality_score = checks_passed / checks_total
        
        # Valid only if no errors and score >= 0.8
        is_valid = len(errors) == 0 and quality_score >= 0.8
        
        if not is_valid:
            logger.warning(f"Data validation failed: {len(errors)} errors, score={quality_score:.2%}")
        
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
