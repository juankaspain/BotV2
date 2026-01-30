"""Centralized Environment Loader for BotV2.

This module ensures .env file is loaded only ONCE across the entire application,
preventing duplicate log messages and ensuring consistent environment state.

Usage:
    from shared.utils.env_loader import load_env_once
    load_env_once()  # Call at application entry point
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Global state to track if env has been loaded
_ENV_LOADED = False
_ENV_FILE_PATH: Optional[Path] = None
_LOAD_MESSAGE_SHOWN = False


def find_env_file() -> Optional[Path]:
    """Find the .env file by searching upward from current location.
    
    Search order:
    1. Current working directory
    2. Script directory
    3. Parent directories (up to 3 levels)
    
    Returns:
        Path to .env file if found, None otherwise
    """
    search_paths = [
        Path.cwd(),
        Path(__file__).parent.parent.parent,  # Project root from shared/utils/
        Path(sys.argv[0]).parent if sys.argv[0] else Path.cwd(),
    ]
    
    # Add parent directories
    for base in search_paths[:2]:
        for i in range(3):
            parent = base.parents[i] if i < len(base.parents) else None
            if parent:
                search_paths.append(parent)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for p in search_paths:
        try:
            resolved = p.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique_paths.append(resolved)
        except (OSError, ValueError):
            continue
    
    # Search for .env
    for path in unique_paths:
        env_file = path / '.env'
        if env_file.exists() and env_file.is_file():
            return env_file
    
    return None


def load_env_once(env_path: Optional[str] = None, verbose: bool = False) -> bool:
    """Load environment variables from .env file exactly once.
    
    This function is idempotent - calling it multiple times has no effect
    after the first successful load.
    
    Args:
        env_path: Optional explicit path to .env file
        verbose: If True, print confirmation message (only on first load)
    
    Returns:
        True if .env was loaded (this call or previously), False if not found
    """
    global _ENV_LOADED, _ENV_FILE_PATH, _LOAD_MESSAGE_SHOWN
    
    # Already loaded - return immediately
    if _ENV_LOADED:
        return True
    
    # Find .env file
    if env_path:
        env_file = Path(env_path)
    else:
        env_file = find_env_file()
    
    if not env_file or not env_file.exists():
        return False
    
    # Try to load with python-dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file, override=False)
        _ENV_LOADED = True
        _ENV_FILE_PATH = env_file
        
        # Show message only once, only if verbose requested
        if verbose and not _LOAD_MESSAGE_SHOWN:
            print(f"[+] Environment loaded from {env_file}", flush=True)
            _LOAD_MESSAGE_SHOWN = True
        
        return True
    
    except ImportError:
        # python-dotenv not installed - try manual parsing
        try:
            _load_env_manual(env_file)
            _ENV_LOADED = True
            _ENV_FILE_PATH = env_file
            
            if verbose and not _LOAD_MESSAGE_SHOWN:
                print(f"[+] Environment loaded from {env_file} (manual)", flush=True)
                _LOAD_MESSAGE_SHOWN = True
            
            return True
        except Exception:
            return False
    
    except Exception:
        return False


def _load_env_manual(env_file: Path) -> None:
    """Manually parse .env file when python-dotenv is not available.
    
    Args:
        env_file: Path to .env file
    """
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Skip lines without =
            if '=' not in line:
                continue
            
            # Parse key=value
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            
            # Remove quotes if present
            if value and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            
            # Only set if not already in environment (don't override)
            if key and key not in os.environ:
                os.environ[key] = value


def get_env_file_path() -> Optional[Path]:
    """Get the path to the loaded .env file.
    
    Returns:
        Path to .env file if loaded, None otherwise
    """
    return _ENV_FILE_PATH


def is_env_loaded() -> bool:
    """Check if environment has been loaded.
    
    Returns:
        True if load_env_once() was called successfully
    """
    return _ENV_LOADED


def reset_env_state() -> None:
    """Reset the environment loading state.
    
    This is primarily for testing purposes. In normal operation,
    the environment should only be loaded once.
    """
    global _ENV_LOADED, _ENV_FILE_PATH, _LOAD_MESSAGE_SHOWN
    _ENV_LOADED = False
    _ENV_FILE_PATH = None
    _LOAD_MESSAGE_SHOWN = False
