"""DataTable Component - Reusable data table for the dashboard.

This module provides a flexible DataTable component for displaying
tabular data with sorting, filtering, pagination, and row actions.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, Literal
from enum import Enum
from markupsafe import Markup


class ColumnAlign(Enum):
    """Column alignment options."""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TableVariant(Enum):
    """Table visual variants."""
    DEFAULT = "default"
    STRIPED = "striped"
    BORDERED = "bordered"
    HOVER = "hover"
    COMPACT = "compact"


@dataclass
class Column:
    """Table column definition.
    
    Attributes:
        key: Data key for this column
        label: Display label
        sortable: Whether column is sortable
        align: Column alignment
        width: Optional width (CSS value)
        formatter: Optional function to format cell value
        class_name: Optional CSS class for column
    """
    key: str
    label: str
    sortable: bool = False
    align: ColumnAlign = ColumnAlign.LEFT
    width: Optional[str] = None
    formatter: Optional[Callable[[Any], str]] = None
    class_name: str = ""
    
    def format_value(self, value: Any) -> str:
        """Format the cell value."""
        if self.formatter:
            return self.formatter(value)
        return str(value) if value is not None else ""
    
    @property
    def header_classes(self) -> str:
        """Get header cell CSS classes."""
        classes = ["data-table__header-cell"]
        classes.append(f"data-table__header-cell--{self.align.value}")
        if self.sortable:
            classes.append("data-table__header-cell--sortable")
        if self.class_name:
            classes.append(self.class_name)
        return " ".join(classes)
    
    @property
    def cell_classes(self) -> str:
        """Get data cell CSS classes."""
        classes = ["data-table__cell"]
        classes.append(f"data-table__cell--{self.align.value}")
        if self.class_name:
            classes.append(self.class_name)
        return " ".join(classes)


@dataclass
class DataTable:
    """Reusable data table component.
    
    Attributes:
        columns: List of column definitions
        data: List of data rows (dicts)
        variant: Visual variant
        loading: Whether table is loading
        empty_message: Message when no data
        caption: Optional table caption
        row_key: Key to use as row ID
        selectable: Whether rows are selectable
        actions: Optional row action buttons
        extra_classes: Additional CSS classes
    """
    columns: List[Column]
    data: List[Dict[str, Any]]
    variant: TableVariant = TableVariant.DEFAULT
    loading: bool = False
    empty_message: str = "No data available"
    caption: Optional[str] = None
    row_key: str = "id"
    selectable: bool = False
    actions: List[Dict[str, Any]] = field(default_factory=list)
    extra_classes: str = ""
    
    def _build_css_classes(self) -> str:
        """Build CSS class string."""
        classes = ["data-table"]
        classes.append(f"data-table--{self.variant.value}")
        if self.loading:
            classes.append("data-table--loading")
        if self.selectable:
            classes.append("data-table--selectable")
        if self.extra_classes:
            classes.append(self.extra_classes)
        return " ".join(classes)
    
    def _render_header(self) -> str:
        """Render table header."""
        cells = []
        
        # Checkbox column for selectable rows
        if self.selectable:
            cells.append('''<th class="data-table__header-cell data-table__header-cell--checkbox">
                <input type="checkbox" class="data-table__checkbox-all" 
                       aria-label="Select all rows">
            </th>''')
        
        # Data columns
        for col in self.columns:
            width_style = f'style="width: {col.width};"' if col.width else ""
            sort_attr = 'data-sort-key="{}"'.format(col.key) if col.sortable else ""
            cells.append(f'''<th class="{col.header_classes}" {width_style} {sort_attr}>
                {col.label}
                {self._render_sort_icon(col) if col.sortable else ""}
            </th>''')
        
        # Actions column
        if self.actions:
            cells.append('<th class="data-table__header-cell data-table__header-cell--actions">Actions</th>')
        
        return f'''<thead class="data-table__header">
            <tr class="data-table__header-row">
                {"\n".join(cells)}
            </tr>
        </thead>'''
    
    def _render_sort_icon(self, col: Column) -> str:
        """Render sort icon for column."""
        return '''<span class="data-table__sort-icon" aria-hidden="true">
            <span class="data-table__sort-icon-up">▲</span>
            <span class="data-table__sort-icon-down">▼</span>
        </span>'''
    
    def _render_body(self) -> str:
        """Render table body."""
        if not self.data:
            return self._render_empty_state()
        
        rows = []
        for row_data in self.data:
            rows.append(self._render_row(row_data))
        
        return f'''<tbody class="data-table__body">
            {"\n".join(rows)}
        </tbody>'''
    
    def _render_row(self, row_data: Dict[str, Any]) -> str:
        """Render a single table row."""
        row_id = row_data.get(self.row_key, "")
        cells = []
        
        # Checkbox cell
        if self.selectable:
            cells.append(f'''<td class="data-table__cell data-table__cell--checkbox">
                <input type="checkbox" class="data-table__checkbox" 
                       value="{row_id}" aria-label="Select row">
            </td>''')
        
        # Data cells
        for col in self.columns:
            value = row_data.get(col.key, "")
            formatted_value = col.format_value(value)
            cells.append(f'<td class="{col.cell_classes}">{formatted_value}</td>')
        
        # Actions cell
        if self.actions:
            cells.append(self._render_actions_cell(row_data))
        
        return f'''<tr class="data-table__row" data-row-id="{row_id}">
            {"\n".join(cells)}
        </tr>'''
    
    def _render_actions_cell(self, row_data: Dict[str, Any]) -> str:
        """Render actions cell for a row."""
        row_id = row_data.get(self.row_key, "")
        action_buttons = []
        
        for action in self.actions:
            label = action.get("label", "")
            icon = action.get("icon", "")
            action_class = action.get("class", "")
            action_id = action.get("id", "")
            
            action_buttons.append(f'''<button class="btn btn-sm {action_class}" 
                data-action="{action_id}" data-row-id="{row_id}"
                aria-label="{label}">
                {f'<i class="{icon}"></i>' if icon else ''}
                <span>{label}</span>
            </button>''')
        
        return f'''<td class="data-table__cell data-table__cell--actions">
            <div class="data-table__actions">
                {" ".join(action_buttons)}
            </div>
        </td>'''
    
    def _render_empty_state(self) -> str:
        """Render empty state when no data."""
        colspan = len(self.columns)
        if self.selectable:
            colspan += 1
        if self.actions:
            colspan += 1
        
        return f'''<tbody class="data-table__body data-table__body--empty">
            <tr>
                <td colspan="{colspan}" class="data-table__empty-cell">
                    <div class="empty-state empty-state--compact">
                        <div class="empty-state__icon" aria-hidden="true">📭</div>
                        <p class="empty-state__message">{self.empty_message}</p>
                    </div>
                </td>
            </tr>
        </tbody>'''
    
    def _render_loading_skeleton(self) -> str:
        """Render loading skeleton."""
        return '''<div class="data-table__loading-overlay" aria-busy="true">
            <div class="loading-spinner loading-spinner--lg"></div>
            <p class="data-table__loading-text">Loading data...</p>
        </div>'''
    
    def render(self) -> Markup:
        """Render the DataTable component."""
        caption_html = f'<caption class="data-table__caption">{self.caption}</caption>' if self.caption else ""
        loading_html = self._render_loading_skeleton() if self.loading else ""
        
        html = f'''<div class="data-table-wrapper" role="region" tabindex="0">
            <table class="{self._build_css_classes()}" role="table">
                {caption_html}
                {self._render_header()}
                {self._render_body()}
            </table>
            {loading_html}
        </div>'''
        
        return Markup(html)
    
    def __html__(self) -> str:
        """Support for Jinja2 auto-escaping."""
        return self.render()


# Utility formatters for common data types
def format_currency(value: float, currency: str = "$", decimals: int = 2) -> str:
    """Format value as currency."""
    return f"{currency}{value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


def format_pnl(value: float) -> str:
    """Format P&L value with color class."""
    color_class = "text-success" if value >= 0 else "text-danger"
    sign = "+" if value > 0 else ""
    return f'<span class="{color_class}">{sign}{format_currency(value)}</span>'


def format_timestamp(value: str, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp string."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime(format)
    except:
        return value


def format_status_badge(status: str) -> str:
    """Format status as colored badge."""
    status_lower = status.lower()
    variant_map = {
        "active": "success",
        "open": "success",
        "closed": "secondary",
        "pending": "warning",
        "error": "danger",
        "failed": "danger"
    }
    variant = variant_map.get(status_lower, "default")
    return f'<span class="badge badge--{variant}">{status}</span>'
