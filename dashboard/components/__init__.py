"""Dashboard UI Components.

Reusable components for the BotV2 trading dashboard.
All components support Jinja2 auto-escaping and accessibility features.
"""

# Core components
from dashboard.components.stat_card import (
    StatCard,
    StatCardTrend,
    TrendDirection,
    CardVariant,
    CardSize,
    # Factory functions
    create_pnl_card,
    create_balance_card,
    create_positions_card,
    create_win_rate_card,
)

from dashboard.components.data_table import (
    DataTable,
    Column,
    ColumnAlign,
    TableVariant,
    # Utility formatters
    format_currency,
    format_percentage,
    format_pnl,
    format_timestamp,
    format_status_badge,
)

from dashboard.components.toast import (
    Toast,
    ToastVariant,
)

# TODO: Add Alert and Skeleton components when needed
# from dashboard.components.alert import Alert, AlertVariant
# from dashboard.components.skeleton import Skeleton, SkeletonVariant

__all__ = [
    # StatCard
    'StatCard',
    'StatCardTrend',
    'TrendDirection',
    'CardVariant',
    'CardSize',
    'create_pnl_card',
    'create_balance_card',
    'create_positions_card',
    'create_win_rate_card',
    # DataTable
    'DataTable',
    'Column',
    'ColumnAlign',
    'TableVariant',
    'format_currency',
    'format_percentage',
    'format_pnl',
    'format_timestamp',
    'format_status_badge',
    # Toast
    'Toast',
    'ToastVariant',
]

__version__ = '1.0.0'
