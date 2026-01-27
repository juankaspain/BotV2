"""
Data Module for BotV2

Provides data handling, validation, and exchange connectivity.
"""

from .data_validator import DataValidator
from .exchange_connector import ExchangeConnector
from .normalization_pipeline import NormalizationPipeline

__all__ = [
    'DataValidator',
    'ExchangeConnector',
    'NormalizationPipeline',
]
