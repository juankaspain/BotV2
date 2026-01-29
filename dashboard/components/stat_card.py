"""StatCard Component - Reusable statistics card for the dashboard.

This module provides a flexible StatCard component that can display
various types of statistics with optional trends, icons, and actions.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, Dict, Any
from enum import Enum
from markupsafe import Markup


class TrendDirection(Enum):
    """Direction of the trend indicator."""
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class CardVariant(Enum):
    """Visual variant of the card."""
    DEFAULT = "default"
    PRIMARY = "primary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"


class CardSize(Enum):
    """Size variant of the card."""
    SM = "sm"
    MD = "md"
    LG = "lg"


@dataclass
class StatCardTrend:
    """Trend information for a StatCard."""
    value: float
    direction: TrendDirection = TrendDirection.NEUTRAL
    label: str = ""
    
    @property
    def formatted_value(self) -> str:
        """Return formatted trend value with sign."""
        sign = "+" if self.value > 0 else ""
        return f"{sign}{self.value:.2f}%"
    
    @property
    def css_class(self) -> str:
        """Return CSS class based on trend direction."""
        return f"stat-card__trend--{self.direction.value}"


@dataclass
class StatCard:
    """Reusable statistics card component.
    
    Attributes:
        title: Card title/label
        value: Main value to display
        subtitle: Optional subtitle or description
        icon: Optional icon class (e.g., 'icon-chart')
        trend: Optional trend indicator
        variant: Visual style variant
        size: Size of the card
        loading: Whether to show loading skeleton
        tooltip: Optional tooltip text
        action_url: Optional URL for card click action
        extra_classes: Additional CSS classes
        data_attrs: Additional data attributes
    """
    title: str
    value: str
    subtitle: Optional[str] = None
    icon: Optional[str] = None
    trend: Optional[StatCardTrend] = None
    variant: CardVariant = CardVariant.DEFAULT
    size: CardSize = CardSize.MD
    loading: bool = False
    tooltip: Optional[str] = None
    action_url: Optional[str] = None
    extra_classes: str = ""
    data_attrs: Dict[str, Any] = field(default_factory=dict)
    
    def _build_css_classes(self) -> str:
        """Build the complete CSS class string."""
        classes = ["stat-card"]
        classes.append(f"stat-card--{self.variant.value}")
        classes.append(f"stat-card--{self.size.value}")
        
        if self.loading:
            classes.append("stat-card--loading skeleton")
        if self.action_url:
            classes.append("stat-card--clickable")
        if self.extra_classes:
            classes.append(self.extra_classes)
            
        return " ".join(classes)
    
    def _build_data_attrs(self) -> str:
        """Build data attributes string."""
        attrs = []
        for key, value in self.data_attrs.items():
            attrs.append(f'data-{key}="{value}"')
        return " ".join(attrs)
    
    def _render_icon(self) -> str:
        """Render the icon element."""
        if not self.icon:
            return ""
        return f'''<div class="stat-card__icon" aria-hidden="true">
            <i class="{self.icon}"></i>
        </div>'''
    
    def _render_trend(self) -> str:
        """Render the trend indicator."""
        if not self.trend:
            return ""
        
        icon_map = {
            TrendDirection.UP: "↑",
            TrendDirection.DOWN: "↓",
            TrendDirection.NEUTRAL: "→"
        }
        
        return f'''<div class="stat-card__trend {self.trend.css_class}" 
                        aria-label="Trend: {self.trend.formatted_value}">
            <span class="stat-card__trend-icon">{icon_map[self.trend.direction]}</span>
            <span class="stat-card__trend-value">{self.trend.formatted_value}</span>
            {f'<span class="stat-card__trend-label">{self.trend.label}</span>' if self.trend.label else ''}
        </div>'''
    
    def _render_skeleton(self) -> str:
        """Render skeleton loading state."""
        return '''<div class="stat-card stat-card--loading skeleton" aria-busy="true" aria-label="Loading...">
            <div class="stat-card__content">
                <div class="skeleton-line skeleton-line--sm" style="width: 60%;"></div>
                <div class="skeleton-line skeleton-line--lg" style="width: 40%;"></div>
                <div class="skeleton-line skeleton-line--sm" style="width: 80%;"></div>
            </div>
        </div>'''
    
    def render(self) -> Markup:
        """Render the StatCard component as HTML."""
        if self.loading:
            return Markup(self._render_skeleton())
        
        wrapper_tag = "a" if self.action_url else "div"
        href_attr = f'href="{self.action_url}"' if self.action_url else ""
        tooltip_attr = f'title="{self.tooltip}" data-tooltip' if self.tooltip else ""
        
        html = f'''<{wrapper_tag} class="{self._build_css_classes()}" 
                    {href_attr} {tooltip_attr} {self._build_data_attrs()}
                    role="{"link" if self.action_url else "article"}" 
                    aria-label="{self.title}: {self.value}">
            {self._render_icon()}
            <div class="stat-card__content">
                <h3 class="stat-card__title">{self.title}</h3>
                <div class="stat-card__value">{self.value}</div>
                {f'<p class="stat-card__subtitle">{self.subtitle}</p>' if self.subtitle else ''}
                {self._render_trend()}
            </div>
        </{wrapper_tag}>'''
        
        return Markup(html)
    
    def __html__(self) -> str:
        """Support for Jinja2 auto-escaping."""
        return self.render()


# Factory functions for common card types
def create_pnl_card(
    value: float,
    period: str = "Today",
    loading: bool = False
) -> StatCard:
    """Create a P&L statistics card."""
    trend_dir = TrendDirection.UP if value >= 0 else TrendDirection.DOWN
    variant = CardVariant.SUCCESS if value >= 0 else CardVariant.DANGER
    
    return StatCard(
        title=f"P&L ({period})",
        value=f"${value:,.2f}",
        icon="icon-chart-line",
        trend=StatCardTrend(value=value, direction=trend_dir),
        variant=variant,
        loading=loading
    )


def create_balance_card(
    balance: float,
    currency: str = "USDT",
    change_pct: Optional[float] = None,
    loading: bool = False
) -> StatCard:
    """Create a balance statistics card."""
    trend = None
    if change_pct is not None:
        trend_dir = TrendDirection.UP if change_pct >= 0 else TrendDirection.DOWN
        trend = StatCardTrend(value=change_pct, direction=trend_dir, label="24h")
    
    return StatCard(
        title="Balance",
        value=f"{balance:,.2f} {currency}",
        icon="icon-wallet",
        trend=trend,
        variant=CardVariant.PRIMARY,
        loading=loading
    )


def create_positions_card(
    open_count: int,
    total_value: Optional[float] = None,
    loading: bool = False
) -> StatCard:
    """Create an open positions statistics card."""
    subtitle = f"Total: ${total_value:,.2f}" if total_value else None
    
    return StatCard(
        title="Open Positions",
        value=str(open_count),
        subtitle=subtitle,
        icon="icon-layers",
        variant=CardVariant.INFO,
        loading=loading
    )


def create_win_rate_card(
    win_rate: float,
    total_trades: int,
    loading: bool = False
) -> StatCard:
    """Create a win rate statistics card."""
    variant = CardVariant.SUCCESS if win_rate >= 50 else CardVariant.WARNING
    
    return StatCard(
        title="Win Rate",
        value=f"{win_rate:.1f}%",
        subtitle=f"{total_trades} total trades",
        icon="icon-target",
        variant=variant,
        loading=loading
    )
