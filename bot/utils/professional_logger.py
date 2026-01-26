"""
Professional Logger Module
Provides clean, visually distinct, colorized logging for production systems.

Features:
- Color-coded log levels
- ASCII art separators
- Validation report formatting
- No duplicate logs on restart
- One-time initialization flags
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# ANSI Color codes
class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'      # Magenta
    BLUE = '\033[94m'        # Blue
    CYAN = '\033[96m'        # Cyan
    GREEN = '\033[92m'       # Green
    YELLOW = '\033[93m'      # Yellow
    RED = '\033[91m'         # Red
    BOLD = '\033[1m'         # Bold
    UNDERLINE = '\033[4m'    # Underline
    END = '\033[0m'          # Reset
    LIGHT_GRAY = '\033[90m'  # Light gray
    DARK_GRAY = '\033[2m'    # Dark gray


class ProfessionalFormatter(logging.Formatter):
    """
    Professional log formatter with:
    - Color-coded levels
    - Clean formatting
    - ASCII art elements
    - No timestamp duplication
    """
    
    # Color mapping for log levels
    COLORS = {
        'DEBUG': Colors.LIGHT_GRAY,
        'INFO': Colors.CYAN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }
    
    # Log level symbols
    SYMBOLS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔴',
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors and symbols
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Get log level name
        level_name = record.levelname
        
        # Get color and symbol
        color = self.COLORS.get(level_name, Colors.CYAN)
        symbol = self.SYMBOLS.get(level_name, '')
        
        # Format the message
        if level_name == 'DEBUG':
            # Debug logs are less verbose
            formatted = f"{color}[{symbol}]{Colors.END} {record.getMessage()}"
        else:
            # Other logs include symbol
            formatted = f"{color}{symbol}{Colors.END} {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{Colors.RED}{record.exc_text}{Colors.END}"
        
        return formatted


class ValidationReporter:
    """
    Professional validation report generator
    
    Provides clean, formatted output for:
    - Environment variable validation
    - Configuration checks
    - System readiness
    """
    
    def __init__(self, logger: logging.Logger):
        """Initialize reporter with logger instance"""
        self.logger = logger
        self._reported = set()  # Track what has been reported
    
    def report_validation_start(self, environment: str):
        """Report start of validation"""
        key = f"validation_start_{environment}"
        if key in self._reported:
            return
        
        self.logger.info("")
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}┌─ ENVIRONMENT VALIDATION ─────────────────────────────────────┐{Colors.END}")
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}│{Colors.END} Environment: {Colors.BOLD}{environment.upper()}{Colors.END}")
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}│{Colors.END} Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"{Colors.BOLD}{Colors.BLUE}└──────────────────────────────────────────────────────────────┘{Colors.END}")
        
        self._reported.add(key)
    
    def report_validation_results(self, 
                                  validated: List[Tuple[str, bool, str]],
                                  environment: str):
        """
        Report validation results in professional format
        
        Args:
            validated: List of (name, is_valid, description) tuples
            environment: Current environment
        """
        key = f"validation_results_{environment}"
        if key in self._reported:
            return
        
        # Count valid/invalid
        total = len(validated)
        valid_count = sum(1 for _, is_valid, _ in validated if is_valid)
        invalid_count = total - valid_count
        
        # Header
        self.logger.info("")
        self.logger.info(f"{Colors.BOLD}VALIDATION RESULTS{Colors.END}")
        self.logger.info("─" * 60)
        
        # Results
        for name, is_valid, description in validated:
            if is_valid:
                status = f"{Colors.GREEN}✓ VALID{Colors.END}"
            else:
                status = f"{Colors.RED}✗ INVALID{Colors.END}"
            
            # Truncate description if too long
            desc = description[:45] + "..." if len(description) > 45 else description
            
            self.logger.info(f"  {status:20} {name:25} {desc}")
        
        # Summary
        self.logger.info("─" * 60)
        
        if invalid_count == 0:
            summary = f"{Colors.GREEN}{Colors.BOLD}✓ ALL VALIDATIONS PASSED{Colors.END} ({valid_count}/{total})"
        else:
            summary = f"{Colors.RED}{Colors.BOLD}✗ VALIDATION FAILED{Colors.END} ({invalid_count} missing)"
        
        self.logger.info(summary)
        self.logger.info("")
        
        self._reported.add(key)
    
    def report_secrets_summary(self, total: int, validated: int, missing: int):
        """Report secrets validation summary"""
        key = "secrets_summary"
        if key in self._reported:
            return
        
        self.logger.info("")
        self.logger.info(f"{Colors.BOLD}{Colors.CYAN}┌─ SECRETS VALIDATION ──────────────────────────────────────┐{Colors.END}")
        self.logger.info(f"{Colors.BOLD}{Colors.CYAN}│{Colors.END} Total Secrets:     {Colors.BOLD}{total}{Colors.END}")
        self.logger.info(f"{Colors.BOLD}{Colors.CYAN}│{Colors.END} Validated:        {Colors.GREEN}{validated}{Colors.END}")
        
        if missing > 0:
            self.logger.info(f"{Colors.BOLD}{Colors.CYAN}│{Colors.END} Missing:          {Colors.RED}{missing}{Colors.END}")
        
        self.logger.info(f"{Colors.BOLD}{Colors.CYAN}└──────────────────────────────────────────────────────────┘{Colors.END}")
        
        self._reported.add(key)
    
    def report_initialization_complete(self, components: List[str], duration: float):
        """Report successful initialization"""
        key = "initialization_complete"
        if key in self._reported:
            return
        
        self.logger.info("")
        self.logger.info(f"{Colors.GREEN}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗{Colors.END}")
        self.logger.info(f"{Colors.GREEN}{Colors.BOLD}║  ✓ INITIALIZATION SUCCESSFUL                              ║{Colors.END}")
        self.logger.info(f"{Colors.GREEN}{Colors.BOLD}╚════════════════════════════════════════════════════════════╝{Colors.END}")
        
        self.logger.info(f"{Colors.GREEN}Components Loaded:{Colors.END}")
        for component in components:
            self.logger.info(f"  {Colors.GREEN}✓{Colors.END} {component}")
        
        self.logger.info(f"{Colors.CYAN}Initialization Time: {duration:.2f}s{Colors.END}")
        self.logger.info("")
        
        self._reported.add(key)
    
    def report_initialization_start():
        """Report start of initialization"""
        key = "initialization_start"
        if key in self._reported:
            return
        
        # This is called before other operations
        pass
    
    def report_error_critical(self, error: str, details: Optional[str] = None):
        """Report critical error"""
        self.logger.error("")
        self.logger.error(f"{Colors.RED}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗{Colors.END}")
        self.logger.error(f"{Colors.RED}{Colors.BOLD}║  ✗ CRITICAL ERROR                                          ║{Colors.END}")
        self.logger.error(f"{Colors.RED}{Colors.BOLD}╚════════════════════════════════════════════════════════════╝{Colors.END}")
        
        self.logger.error(f"{Colors.RED}{error}{Colors.END}")
        
        if details:
            self.logger.error(f"\n{Colors.YELLOW}Details:{Colors.END}")
            self.logger.error(details)
        
        self.logger.error("")


def setup_professional_logger(name: str, 
                             log_file: Optional[str] = None,
                             level: int = logging.INFO) -> Tuple[logging.Logger, ValidationReporter]:
    """
    Setup professional logger with formatter and reporter
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional file path for logging
        level: Logging level (default INFO)
        
    Returns:
        Tuple of (logger, reporter)
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to prevent duplication
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ProfessionalFormatter())
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        # Create logs directory if needed
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        
        # Plain formatter for file (no colors)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Create reporter
    reporter = ValidationReporter(logger)
    
    return logger, reporter


def get_colored_section(title: str, 
                       color: str = Colors.CYAN,
                       width: int = 60) -> Tuple[str, str]:
    """
    Get colored section headers
    
    Args:
        title: Section title
        color: Color code
        width: Section width
        
    Returns:
        Tuple of (header, footer) strings
    """
    header = f"{color}{Colors.BOLD}┌{'─' * (width - 2)}┐{Colors.END}"
    footer = f"{color}{Colors.BOLD}└{'─' * (width - 2)}┘{Colors.END}"
    
    return header, footer
