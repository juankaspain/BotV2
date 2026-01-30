"""Centralized environment loader to avoid duplicate load messages.

This module ensures .env is loaded only once and all imports use the same loaded environment.
Uses thread-safe singleton pattern to prevent duplicate loads even in complex import scenarios.
"""

import os
import sys
import threading
from pathlib import Path
from typing import Optional

# Thread-safe singleton implementation
_lock = threading.Lock()
_ENV_LOADED = False
_ENV_FILE_PATH: Optional[Path] = None
_LOAD_MESSAGE_SHOWN = False


def load_env_once(verbose: bool = False) -> bool:
    """Load .env file only once across entire application.
    
    Thread-safe implementation that guarantees:
    1. The .env file is loaded exactly once
    2. The load message is printed exactly once (if verbose=True)
    3. Safe for use in multi-threaded or complex import scenarios
    
    Args:
        verbose: If True, print load message to console (only first time)
        
    Returns:
        bool: True if env was loaded this time, False if already loaded
    """
    global _ENV_LOADED, _ENV_FILE_PATH, _LOAD_MESSAGE_SHOWN
    
    # Quick check without lock (optimization for already-loaded case)
    if _ENV_LOADED:
        return False
    
    # Thread-safe double-checked locking pattern
    with _lock:
        # Check again inside lock (another thread might have loaded it)
        if _ENV_LOADED:
            return False
        
        try:
            from dotenv import load_dotenv
            
            # Find .env file (works from any subdirectory)
            # Try multiple strategies to find project root
            env_file = _find_env_file()
            
            if env_file and env_file.exists():
                load_dotenv(env_file)
                _ENV_FILE_PATH = env_file
                _ENV_LOADED = True
                
                # Only show message once, even if verbose=True is called multiple times
                if verbose and not _LOAD_MESSAGE_SHOWN:
                    _LOAD_MESSAGE_SHOWN = True
                    print(f"[+] Environment loaded from {env_file}", flush=True)
                
                return True
            else:
                if verbose and not _LOAD_MESSAGE_SHOWN:
                    _LOAD_MESSAGE_SHOWN = True
                    print("[!] No .env file found", flush=True)
                
                _ENV_LOADED = True  # Mark as attempted to prevent retry
                return False
                
        except ImportError:
            if verbose and not _LOAD_MESSAGE_SHOWN:
                _LOAD_MESSAGE_SHOWN = True
                print("[!] python-dotenv not installed", flush=True)
            _ENV_LOADED = True  # Mark as attempted
            return False


def _find_env_file() -> Optional[Path]:
    """Find the .env file using multiple strategies.
    
    Searches in order:
    1. From this file's location: shared/utils -> shared -> project root
    2. Current working directory
    3. Parent directories up to 3 levels
    
    Returns:
        Optional[Path]: Path to .env file or None if not found
    """
    candidates = []
    
    # Strategy 1: Relative to this file
    try:
        current_dir = Path(__file__).resolve().parent
        project_root = current_dir.parent.parent  # shared/utils -> shared -> root
        candidates.append(project_root / '.env')
    except Exception:
        pass
    
    # Strategy 2: Current working directory
    try:
        cwd = Path.cwd()
        candidates.append(cwd / '.env')
        
        # Strategy 3: Parent directories (up to 3 levels)
        for i in range(1, 4):
            parent = cwd
            for _ in range(i):
                parent = parent.parent
            candidates.append(parent / '.env')
    except Exception:
        pass
    
    # Strategy 4: Check PYTHONPATH entries
    for path_str in sys.path:
        try:
            path = Path(path_str)
            if path.is_dir():
                candidates.append(path / '.env')
        except Exception:
            pass
    
    # Return first existing file
    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_file():
                return candidate.resolve()
        except Exception:
            pass
    
    return None


def get_env_file_path() -> Optional[Path]:
    """Get the path of the loaded .env file.
    
    Returns:
        Optional[Path]: Path to .env file or None if not loaded
    """
    return _ENV_FILE_PATH


def is_env_loaded() -> bool:
    """Check if environment has been loaded.
    
    Returns:
        bool: True if env was loaded/attempted
    """
    return _ENV_LOADED


def reset_env_loader() -> None:
    """Reset the env loader state (for testing purposes only).
    
    WARNING: This should only be used in test scenarios.
    Using this in production can cause duplicate loads.
    """
    global _ENV_LOADED, _ENV_FILE_PATH, _LOAD_MESSAGE_SHOWN
    with _lock:
        _ENV_LOADED = False
        _ENV_FILE_PATH = None
        _LOAD_MESSAGE_SHOWN = False
