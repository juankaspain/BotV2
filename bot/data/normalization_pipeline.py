"""
Data Normalization Pipeline
Z-score normalization for cross-market feature consistency
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)


class NormalizationPipeline:
    """
    Normalizes market data features using z-score method
    Ensures features are on comparable scales for ML models
    """
    
    def __init__(self, 
                 lookback: int = 252,
                 clip_range: tuple = (-3, 3)):
        """
        Args:
            lookback: Rolling window for mean/std calculation (days)
            clip_range: Range to clip normalized values (prevents extreme outliers)
        """
        self.lookback = lookback
        self.clip_range = clip_range
        
        # Store statistics for denormalization
        self.stats_cache = {}
        
        logger.info(
            f"✓ Normalization Pipeline initialized "
            f"(lookback={lookback}, clip={clip_range})"
        )
    
    def normalize_features(self, data: pd.DataFrame, symbol: Optional[str] = None) -> pd.DataFrame:
        """
        Normalize market features using z-score
        
        Z-score formula: (x - μ) / σ
        
        Args:
            data: DataFrame with market data
            symbol: Optional symbol identifier for caching stats
            
        Returns:
            DataFrame with normalized features
        """
        
        if data.empty:
            logger.warning("Empty data provided for normalization")
            return pd.DataFrame()
        
        normalized = pd.DataFrame(index=data.index)
        
        # Feat
