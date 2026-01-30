"""Centralized environment loader to avoid duplicate load messages.

This module ensures .env is loaded only once and all imports use the same loaded environment.
"""

import os
from pathlib import Path
from typing import Optional

# Global flag to track if env has been loaded
_ENV_LOADED = False
_ENV_FILE_PATH: Optional[Path] = None


def load_env_once(verbose: bool = False) -> bool:
    """Load .env file only once across entire application.
    
    Args:
        verbose: If True, print load message to console
        
    Returns:
        bool: True if env was loaded this time, False if already loaded
    """
    global _ENV_LOADED, _ENV_FILE_PATH
    
    # Already loaded, skip
    if _ENV_LOADED:
        return False
    
    try:
        from dotenv import load_dotenv
        
        # Find .env file (works from any subdirectory)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent  # shared/utils -> shared -> root
        env_file = project_root / '.env'
        
        if env_file.exists():
            load_dotenv(env_file)
            _ENV_FILE_PATH = env_file
            _ENV_LOADED = True
            
            if verbose:
                print(f"[+] Environment loaded from {env_file}", flush=True)
            
            return True
        else:
            # Try current working directory as fallback
            cwd_env = Path.cwd() / '.env'
            if cwd_env.exists():
                load_dotenv(cwd_env)
                _ENV_FILE_PATH = cwd_env
                _ENV_LOADED = True
                
                if verbose:
                    print(f"[+] Environment loaded from {cwd_env}", flush=True)
                
                return True
            
            if verbose:
                print(f"[!] No .env file found", flush=True)
            
            _ENV_LOADED = True  # Mark as attempted
            return False
            
    except ImportError:
        if verbose:
            print("[!] python-dotenv not installed", flush=True)
        _ENV_LOADED = True  # Mark as attempted
        return False


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
