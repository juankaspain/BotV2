"""Toast/Notification Component."""
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from markupsafe import Markup

class ToastVariant(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class Toast:
    """Toast notification component."""
    title: str
    message: str
    variant: ToastVariant = ToastVariant.INFO
    duration: int = 5000
    closeable: bool = True
    
    def render(self) -> Markup:
        close_btn = '<button class="toast__close" aria-label="Close">×</button>' if self.closeable else ""
        return Markup(f'''<div class="toast toast--{self.variant.value}" role="alert">
            <span class="toast__icon" aria-hidden="true">{self._get_icon()}</span>
            <div class="toast__content">
                <h4 class="toast__title">{self.title}</h4>
                <p class="toast__message">{self.message}</p>
            </div>
            {close_btn}
        </div>''')
    
    def _get_icon(self) -> str:
        icons = {"success": "✓", "error": "×", "warning": "⚠", "info": "ℹ"}
        return icons.get(self.variant.value, "ℹ")
    
    def __html__(self) -> str:
        return self.render()
