"""UI Components for BotV2 Dashboard - Phase 2.

This module provides reusable UI components:
- Modal: Confirmation dialogs and custom modals
- Dropdown: Custom dropdown menus
- Breadcrumbs: Navigation breadcrumbs
- Pagination: Table pagination
- Tabs: Tabbed interfaces
"""

from markupsafe import Markup, escape
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class ModalVariant(Enum):
    DEFAULT = "default"
    DANGER = "danger"
    CONFIRM = "confirm"
    SUCCESS = "success"


class ModalSize(Enum):
    SMALL = "sm"
    MEDIUM = "md"
    LARGE = "lg"


@dataclass
class Modal:
    """Modal dialog component."""
    id: str
    title: str
    body: str = ""
    variant: ModalVariant = ModalVariant.DEFAULT
    size: ModalSize = ModalSize.MEDIUM
    confirm_text: str = "Confirm"
    cancel_text: str = "Cancel"
    show_close: bool = True
    
    def render(self) -> Markup:
        size_class = f"modal--{self.size.value}" if self.size != ModalSize.MEDIUM else ""
        variant_class = f"modal--{self.variant.value}" if self.variant != ModalVariant.DEFAULT else ""
        
        return Markup(f'''
        <div class="modal-overlay" id="{escape(self.id)}" role="dialog" aria-modal="true" aria-labelledby="{escape(self.id)}-title">
            <div class="modal {size_class} {variant_class}">
                <div class="modal__header">
                    <h3 class="modal__title" id="{escape(self.id)}-title">{escape(self.title)}</h3>
                    {self._render_close_btn() if self.show_close else ''}
                </div>
                <div class="modal__body">{self.body}</div>
                <div class="modal__footer">
                    <button class="btn btn--secondary" data-modal-close>{escape(self.cancel_text)}</button>
                    <button class="btn btn--primary" data-modal-confirm>{escape(self.confirm_text)}</button>
                </div>
            </div>
        </div>
        ''')
    
    def _render_close_btn(self) -> str:
        return '<button class="modal__close" data-modal-close aria-label="Close"><i class="fas fa-times"></i></button>'


@dataclass
class DropdownItem:
    """Single dropdown menu item."""
    label: str
    value: str = ""
    icon: str = ""
    danger: bool = False
    divider: bool = False
    
    def render(self) -> str:
        if self.divider:
            return '<div class="dropdown__divider"></div>'
        danger_class = "dropdown__item--danger" if self.danger else ""
        icon_html = f'<i class="{escape(self.icon)}"></i>' if self.icon else ""
        return f'<div class="dropdown__item {danger_class}" data-value="{escape(self.value)}">{icon_html}{escape(self.label)}</div>'


@dataclass
class Dropdown:
    """Custom dropdown menu component."""
    id: str
    trigger_text: str
    items: List[DropdownItem] = field(default_factory=list)
    icon: str = ""
    
    def render(self) -> Markup:
        icon_html = f'<i class="{escape(self.icon)}"></i>' if self.icon else ""
        items_html = '\n'.join(item.render() for item in self.items)
        
        return Markup(f'''
        <div class="dropdown" id="{escape(self.id)}">
            <button class="dropdown__trigger" aria-haspopup="true" aria-expanded="false">
                {icon_html}{escape(self.trigger_text)}
            </button>
            <div class="dropdown__menu" role="menu">
                {items_html}
            </div>
        </div>
        ''')


@dataclass
class BreadcrumbItem:
    """Single breadcrumb item."""
    label: str
    url: str = ""
    is_current: bool = False
    
    def render(self) -> str:
        if self.is_current:
            return f'<span class="breadcrumbs__current">{escape(self.label)}</span>'
        return f'<a href="{escape(self.url)}" class="breadcrumbs__link">{escape(self.label)}</a>'


@dataclass
class Breadcrumbs:
    """Breadcrumb navigation component."""
    items: List[BreadcrumbItem] = field(default_factory=list)
    separator: str = "/"
    
    def render(self) -> Markup:
        parts = []
        for i, item in enumerate(self.items):
            parts.append(f'<span class="breadcrumbs__item">{item.render()}</span>')
            if i < len(self.items) - 1:
                parts.append(f'<span class="breadcrumbs__separator">{escape(self.separator)}</span>')
        
        return Markup(f'<nav class="breadcrumbs" aria-label="Breadcrumb">{" ".join(parts)}</nav>')


@dataclass
class Pagination:
    """Pagination component for tables."""
    current_page: int
    total_pages: int
    total_items: int = 0
    items_per_page: int = 10
    show_info: bool = True
    max_visible: int = 5
    
    def render(self) -> Markup:
        items = self._build_page_items()
        items_html = '\n'.join(items)
        info_html = self._render_info() if self.show_info else ""
        
        return Markup(f'''
        <nav class="pagination" aria-label="Pagination">
            {items_html}
            {info_html}
        </nav>
        ''')
    
    def _build_page_items(self) -> List[str]:
        items = []
        # Prev button
        prev_disabled = "pagination__item--disabled" if self.current_page <= 1 else ""
        items.append(f'<button class="pagination__item {prev_disabled}" data-page="{self.current_page - 1}" aria-label="Previous"><i class="fas fa-chevron-left"></i></button>')
        
        # Page numbers
        start = max(1, self.current_page - self.max_visible // 2)
        end = min(self.total_pages, start + self.max_visible - 1)
        if end - start < self.max_visible - 1:
            start = max(1, end - self.max_visible + 1)
        
        if start > 1:
            items.append('<span class="pagination__item" data-page="1">1</span>')
            if start > 2:
                items.append('<span class="pagination__ellipsis">...</span>')
        
        for page in range(start, end + 1):
            active = "pagination__item--active" if page == self.current_page else ""
            items.append(f'<button class="pagination__item {active}" data-page="{page}">{page}</button>')
        
        if end < self.total_pages:
            if end < self.total_pages - 1:
                items.append('<span class="pagination__ellipsis">...</span>')
            items.append(f'<span class="pagination__item" data-page="{self.total_pages}">{self.total_pages}</span>')
        
        # Next button
        next_disabled = "pagination__item--disabled" if self.current_page >= self.total_pages else ""
        items.append(f'<button class="pagination__item {next_disabled}" data-page="{self.current_page + 1}" aria-label="Next"><i class="fas fa-chevron-right"></i></button>')
        
        return items
    
    def _render_info(self) -> str:
        start = (self.current_page - 1) * self.items_per_page + 1
        end = min(self.current_page * self.items_per_page, self.total_items)
        return f'<span class="pagination__info">Showing {start}-{end} of {self.total_items}</span>'


@dataclass
class Tab:
    """Single tab item."""
    id: str
    label: str
    content: str = ""
    icon: str = ""
    active: bool = False
    
    def render_tab(self) -> str:
        active_class = "tabs__tab--active" if self.active else ""
        icon_html = f'<i class="{escape(self.icon)}"></i> ' if self.icon else ""
        return f'<button class="tabs__tab {active_class}" data-tab="{escape(self.id)}" role="tab" aria-selected="{str(self.active).lower()}">{icon_html}{escape(self.label)}</button>'
    
    def render_panel(self) -> str:
        active_class = "tabs__panel--active" if self.active else ""
        return f'<div class="tabs__panel {active_class}" id="{escape(self.id)}-panel" role="tabpanel" aria-labelledby="{escape(self.id)}">{self.content}</div>'


@dataclass
class Tabs:
    """Tabbed interface component."""
    id: str
    tabs: List[Tab] = field(default_factory=list)
    
    def render(self) -> Markup:
        tabs_html = '\n'.join(tab.render_tab() for tab in self.tabs)
        panels_html = '\n'.join(tab.render_panel() for tab in self.tabs)
        
        return Markup(f'''
        <div class="tabs" id="{escape(self.id)}">
            <div class="tabs__list" role="tablist">
                {tabs_html}
            </div>
            <div class="tabs__content">
                {panels_html}
            </div>
        </div>
        ''')


# Factory functions for convenience
def create_confirm_modal(id: str, title: str, message: str, 
                         confirm_text: str = "Confirm", 
                         danger: bool = False) -> Modal:
    """Create a confirmation modal."""
    variant = ModalVariant.DANGER if danger else ModalVariant.CONFIRM
    return Modal(
        id=id,
        title=title,
        body=f'<p>{escape(message)}</p>',
        variant=variant,
        confirm_text=confirm_text,
        size=ModalSize.SMALL
    )


def create_pagination(page: int, per_page: int, total: int) -> Pagination:
    """Create pagination from total item count."""
    total_pages = max(1, (total + per_page - 1) // per_page)
    return Pagination(
        current_page=page,
        total_pages=total_pages,
        total_items=total,
        items_per_page=per_page
    )


__all__ = [
    'Modal', 'ModalVariant', 'ModalSize',
    'Dropdown', 'DropdownItem',
    'Breadcrumbs', 'BreadcrumbItem',
    'Pagination',
    'Tabs', 'Tab',
    'create_confirm_modal', 'create_pagination'
]
