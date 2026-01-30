"""Log Symbols - ASCII-compatible symbols for cross-platform logging.

This module provides ASCII alternatives to Unicode symbols/emojis
to ensure logs display correctly on all platforms, especially
Windows console which often doesn't support UTF-8 by default.

Usage:
    from shared.utils.log_symbols import OK, FAIL, WARN, INFO
    logger.info(f"{OK} Configuration loaded")
"""

# =============================================================================
# ASCII SYMBOLS FOR LOGGING (Windows Compatible)
# =============================================================================

# Status indicators
OK = "[OK]"           # Success (replaces ✓ ✅)
FAIL = "[FAIL]"       # Failure (replaces ✗ ❌)
WARN = "[!]"          # Warning (replaces ⚠️)
ERROR = "[ERROR]"     # Error
INFO = "[i]"          # Info (replaces ℹ️)

# Action indicators
START = "[>>]"        # Starting (replaces 🚀)
STOP = "[||]"         # Stopping
DONE = "[DONE]"       # Completed (replaces ✅)
SKIP = "[--]"         # Skipped
RUN = "[>]"           # Running

# Security indicators
LOCK = "[LOCK]"       # Locked/Secure (replaces 🔒)
UNLOCK = "[OPEN]"     # Unlocked
SHIELD = "[+]"        # Protected (replaces 🛡️)
ALERT = "[!!!]"       # Alert (replaces 🚨)

# System indicators  
LOAD = "[~]"          # Loading
SAVE = "[S]"          # Saving
DELETE = "[X]"        # Deleting
CONFIG = "[C]"        # Configuration
DB = "[DB]"           # Database

# Trading indicators
BUY = "[BUY]"         # Buy signal
SELL = "[SELL]"       # Sell signal
HOLD = "[HOLD]"       # Hold
TARGET = "[*]"        # Target (replaces 🎯)

# Mode indicators
DEMO = "[DEMO]"       # Demo mode (replaces 🎮)
LIVE = "[LIVE]"       # Live mode
TEST = "[TEST]"       # Test mode
DEV = "[DEV]"         # Development
PROD = "[PROD]"       # Production

# Misc
ARROW = "->"          # Arrow
BULLET = "*"          # Bullet point
CHECK = "[v]"         # Checkbox checked
UNCHECK = "[ ]"       # Checkbox unchecked
BYE = "[END]"         # Goodbye (replaces 👋)
STATS = "[#]"         # Statistics (replaces 📊)

# Box drawing (ASCII art for banners)
BOX_H = "="            # Horizontal line
BOX_V = "|"            # Vertical line
BOX_TL = "+"           # Top-left corner
BOX_TR = "+"           # Top-right corner
BOX_BL = "+"           # Bottom-left corner
BOX_BR = "+"           # Bottom-right corner


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def status(success: bool) -> str:
    """Return OK or FAIL based on boolean."""
    return OK if success else FAIL


def progress(current: int, total: int) -> str:
    """Return progress indicator like [3/10]."""
    return f"[{current}/{total}]"


def banner(text: str, width: int = 70) -> str:
    """Create ASCII banner."""
    line = BOX_H * width
    padding = (width - len(text) - 2) // 2
    content = f"{BOX_V}{' ' * padding}{text}{' ' * (width - padding - len(text) - 2)}{BOX_V}"
    return f"{line}\n{content}\n{line}"
