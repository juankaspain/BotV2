"""
Secrets Manager - Secure handling of credentials and API keys
Validates required environment variables at startup
"""

import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logging.warning("python-dotenv not installed, using system environment variables only")

logger = logging.getLogger(__name__)


@dataclass
class SecretValidation:
    """Result of secret validation"""
    is_valid: bool
    missing_secrets: List[str]
    optional_missing: List[str]
    warnings: List[str]


class SecretsManager:
    """
    Centralized secrets management
    
    Handles:
    - Loading from .env files
    - Validation of required secrets
    - Secure access to credentials
    - Secret rotation support
    """
    
    # Required secrets (will cause startup failure if missing)
    REQUIRED_SECRETS = [
        'POSTGRES_PASSWORD',
        'SECRET_KEY',  # For general encryption/signing
    ]
    
    # Optional secrets (warnings only)
    OPTIONAL_SECRETS = [
        'POLYMARKET_API_KEY',
        'BINANCE_API_KEY',
        'BINANCE_API_SECRET',
        'TELEGRAM_BOT_TOKEN',
        'SLACK_WEBHOOK_URL',
        'EMAIL_SMTP_PASSWORD',
    ]
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize secrets manager
        
        Args:
            env_file: Path to .env file (default: .env in project root)
        """
        self.env_file = env_file or '.env'
        self._secrets_cache: Dict[str, str] = {}
        
        # Load environment variables
        self._load_env()
    
    def _load_env(self):
        """Load environment variables from .env file"""
        if DOTENV_AVAILABLE:
            env_path = Path(self.env_file)
            
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"✓ Loaded environment variables from {self.env_file}")
            else:
                logger.warning(f"⚠️ .env file not found at {env_path}, using system env vars")
        else:
            logger.info("Using system environment variables only")
    
    def validate(self) -> SecretValidation:
        """
        Validate that all required secrets are present
        
        Returns:
            SecretValidation object with results
        """
        missing_required = []
        missing_optional = []
        warnings = []
        
        # Check required secrets
        for secret in self.REQUIRED_SECRETS:
            value = os.getenv(secret)
            if not value:
                missing_required.append(secret)
                logger.error(f"❌ Missing required secret: {secret}")
            else:
                logger.debug(f"✓ Found required secret: {secret}")
        
        # Check optional secrets
        for secret in self.OPTIONAL_SECRETS:
            value = os.getenv(secret)
            if not value:
                missing_optional.append(secret)
                warnings.append(f"Optional secret not set: {secret}")
            else:
                logger.debug(f"✓ Found optional secret: {secret}")
        
        # Additional warnings
        if missing_optional:
            warnings.append(
                f"Some features may be limited without optional secrets: "
                f"{', '.join(missing_optional)}"
            )
        
        is_valid = len(missing_required) == 0
        
        return SecretValidation(
            is_valid=is_valid,
            missing_secrets=missing_required,
            optional_missing=missing_optional,
            warnings=warnings
        )
    
    def validate_or_exit(self):
        """
        Validate secrets and exit if required ones are missing
        Use this at application startup
        """
        validation = self.validate()
        
        # Print warnings
        for warning in validation.warnings:
            logger.warning(f"⚠️ {warning}")
        
        # Exit if invalid
        if not validation.is_valid:
            logger.critical(
                f"\n{'='*70}\n"
                f"❌ CRITICAL: Missing required environment variables\n"
                f"{'='*70}\n"
                f"\nMissing secrets:\n"
            )
            for secret in validation.missing_secrets:
                logger.critical(f"  - {secret}")
            
            logger.critical(
                f"\nPlease set these in your .env file or system environment.\n"
                f"Example .env file:\n"
                f"\n"
                f"  POSTGRES_PASSWORD=your_secure_password_here\n"
                f"  SECRET_KEY=your_random_secret_key_here\n"
                f"  POLYMARKET_API_KEY=your_polymarket_key_here\n"
                f"\nExiting...\n"
            )
            exit(1)
        
        logger.info("✅ All required secrets validated")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Securely retrieve a secret
        
        Args:
            key: Secret key name
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        # Check cache first
        if key in self._secrets_cache:
            return self._secrets_cache[key]
        
        # Get from environment
        value = os.getenv(key, default)
        
        # Cache if found
        if value:
            self._secrets_cache[key] = value
        
        return value
    
    def get_database_url(self) -> str:
        """
        Build PostgreSQL connection URL with password from secrets
        
        Returns:
            Database URL string
        """
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DATABASE', 'botv2')
        user = os.getenv('POSTGRES_USER', 'botv2_user')
        password = self.get_secret('POSTGRES_PASSWORD')
        
        if not password:
            raise ValueError("POSTGRES_PASSWORD not set")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def rotate_secret(self, key: str, new_value: str):
        """
        Rotate a secret (update cache)
        
        Args:
            key: Secret key
            new_value: New secret value
        """
        self._secrets_cache[key] = new_value
        logger.info(f"Secret rotated: {key}")
    
    def clear_cache(self):
        """Clear secrets cache (use on logout/shutdown)"""
        self._secrets_cache.clear()
        logger.info("Secrets cache cleared")


# Global instance
_secrets_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """
    Get global SecretsManager instance (singleton)
    
    Returns:
        SecretsManager instance
    """
    global _secrets_manager
    
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    
    return _secrets_manager
