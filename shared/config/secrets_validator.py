"""
Secrets Validator
Validates all required environment variables are present at startup
Fails fast if critical secrets are missing or invalid

Usage:
    from shared.config.secrets_validator import validate_secrets
"""
import os
import sys
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# Use standard logging (professional logger may not be available in demo)
logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""
    REQUIRED = "required"      # Must be present and valid
    RECOMMENDED = "recommended"  # Should be present (warning if missing)
    OPTIONAL = "optional"      # Nice to have (info if missing)


@dataclass
class SecretRequirement:
    """Definition of a secret requirement"""
    name: str
    description: str
    level: ValidationLevel = ValidationLevel.REQUIRED
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    environments: Optional[List[str]] = None  # None = all environments
    validator: Optional[callable] = None


class SecretsValidator:
    """
    Validates environment variables/secrets at startup.
    Supports different validation levels and environment-specific requirements.
    """
    
    # Define all secrets with their validation rules
    SECRETS = [
        # Database (required in production only)
        SecretRequirement(
            name="POSTGRES_PASSWORD",
            description="PostgreSQL database password",
            level=ValidationLevel.REQUIRED,
            min_length=8,
            environments=["production", "staging"]
        ),
        SecretRequirement(
            name="POSTGRES_HOST",
            description="PostgreSQL host",
            level=ValidationLevel.REQUIRED,
            environments=["production", "staging"]
        ),
        SecretRequirement(
            name="POSTGRES_DATABASE",
            description="PostgreSQL database name",
            level=ValidationLevel.RECOMMENDED,
        ),
        SecretRequirement(
            name="POSTGRES_USER",
            description="PostgreSQL user",
            level=ValidationLevel.RECOMMENDED,
        ),
        
        # Trading APIs (required in production only)
        SecretRequirement(
            name="POLYMARKET_API_KEY",
            description="Polymarket API key",
            level=ValidationLevel.REQUIRED,
            min_length=20,
            environments=["production", "staging"]
        ),
        SecretRequirement(
            name="POLYMARKET_API_SECRET",
            description="Polymarket API secret",
            level=ValidationLevel.REQUIRED,
            min_length=32,
            environments=["production", "staging"]
        ),
        
        # Application secrets
        SecretRequirement(
            name="SECRET_KEY",
            description="Application secret key for JWT/sessions",
            level=ValidationLevel.RECOMMENDED,
            min_length=16,
        ),
        SecretRequirement(
            name="DASHBOARD_PASSWORD",
            description="Dashboard authentication password",
            level=ValidationLevel.RECOMMENDED,
            min_length=4,
        ),
        
        # Notifications (optional)
        SecretRequirement(
            name="TELEGRAM_BOT_TOKEN",
            description="Telegram bot token for alerts",
            level=ValidationLevel.OPTIONAL,
            pattern=r'^\d+:[A-Za-z0-9_-]+$'
        ),
        SecretRequirement(
            name="TELEGRAM_CHAT_ID",
            description="Telegram chat ID for alerts",
            level=ValidationLevel.OPTIONAL,
        ),
        SecretRequirement(
            name="SLACK_WEBHOOK_URL",
            description="Slack webhook URL for notifications",
            level=ValidationLevel.OPTIONAL,
            pattern=r'^https://hooks\.slack\.com/services/.*$'
        ),
        
        # Monitoring (optional)
        SecretRequirement(
            name="SENTRY_DSN",
            description="Sentry DSN for error tracking",
            level=ValidationLevel.OPTIONAL,
            environments=["production"],
            pattern=r'^https://.*@sentry\.io/.*$'
        ),
        
        # External APIs (optional)
        SecretRequirement(
            name="TWITTER_BEARER_TOKEN",
            description="Twitter API bearer token for sentiment analysis",
            level=ValidationLevel.OPTIONAL,
        ),
        SecretRequirement(
            name="OPENAI_API_KEY",
            description="OpenAI API key for AI features",
            level=ValidationLevel.OPTIONAL,
            pattern=r'^sk-[A-Za-z0-9]+$'
        ),
    ]
    
    def __init__(self, environment: str = "development", strict: bool = True):
        """
        Initialize the validator.
        
        Args:
            environment: Current environment (development, staging, production)
            strict: If True, exit on missing required secrets
        """
        self.environment = environment
        self.strict = strict
        self.missing_required: List[str] = []
        self.missing_recommended: List[str] = []
        self.missing_optional: List[str] = []
        self.invalid_secrets: Dict[str, str] = {}
        self.warnings: List[str] = []
    
    def validate_all(self) -> bool:
        """
        Validate all secrets for the current environment.
        
        Returns:
            True if all required secrets are valid, False otherwise
        """
        logger.info(f"Validating secrets for environment: {self.environment}")
        
        for requirement in self.SECRETS:
            self._validate_secret(requirement)
        
        self._report_results()
        
        # Check for critical issues
        has_critical_issues = bool(self.missing_required or self.invalid_secrets)
        
        if has_critical_issues:
            logger.error(f"Secret validation failed: {len(self.missing_required)} missing, {len(self.invalid_secrets)} invalid")
            return False
        
        logger.info("✓ All required secrets validated successfully")
        return True
    
    def _validate_secret(self, requirement: SecretRequirement):
        """Validate a single secret requirement"""
        
        # Skip if not applicable to current environment
        if requirement.environments and self.environment not in requirement.environments:
            return
        
        value = os.getenv(requirement.name)
        
        # Check if missing
        if value is None or value == "":
            self._handle_missing_secret(requirement)
            return
        
        # Validate value format
        validation_error = self._validate_value(value, requirement)
        if validation_error:
            self.invalid_secrets[requirement.name] = validation_error
            return
        
        # Run custom validator if present
        if requirement.validator:
            try:
                if not requirement.validator(value):
                    self.invalid_secrets[requirement.name] = "Failed custom validation"
            except Exception as e:
                self.invalid_secrets[requirement.name] = f"Validator error: {e}"
    
    def _handle_missing_secret(self, requirement: SecretRequirement):
        """Handle a missing secret based on its level"""
        if requirement.level == ValidationLevel.REQUIRED:
            self.missing_required.append(requirement.name)
            logger.error(f"✗ Missing required secret: {requirement.name} - {requirement.description}")
        elif requirement.level == ValidationLevel.RECOMMENDED:
            self.missing_recommended.append(requirement.name)
            logger.warning(f"⚠ Missing recommended secret: {requirement.name}")
        else:
            self.missing_optional.append(requirement.name)
            logger.debug(f"ℹ Missing optional secret: {requirement.name}")
    
    def _validate_value(self, value: str, requirement: SecretRequirement) -> Optional[str]:
        """Validate the format of a secret value"""
        
        # Check minimum length
        if requirement.min_length and len(value) < requirement.min_length:
            return f"Too short (min {requirement.min_length} chars, got {len(value)})"
        
        # Check maximum length
        if requirement.max_length and len(value) > requirement.max_length:
            return f"Too long (max {requirement.max_length} chars)"
        
        # Check pattern
        if requirement.pattern and not re.match(requirement.pattern, value):
            return "Does not match required pattern"
        
        return None
    
    def _report_results(self):
        """Log validation results summary"""
        total_checked = len([r for r in self.SECRETS 
                            if not r.environments or self.environment in r.environments])
        
        logger.info(f"Secrets validation summary for '{self.environment}':")
        logger.info(f"  Total checked: {total_checked}")
        logger.info(f"  Missing required: {len(self.missing_required)}")
        logger.info(f"  Missing recommended: {len(self.missing_recommended)}")
        logger.info(f"  Invalid: {len(self.invalid_secrets)}")
        
        if self.missing_required:
            logger.error(f"  Required secrets missing: {', '.join(self.missing_required)}")
        
        if self.invalid_secrets:
            for name, error in self.invalid_secrets.items():
                logger.error(f"  Invalid secret {name}: {error}")
    
    def fail_fast(self):
        """
        Validate and exit immediately if critical secrets are missing.
        Used at application startup.
        """
        if not self.validate_all():
            logger.critical("FATAL: Required secrets validation failed. Cannot start application.")
            logger.critical(f"Missing: {', '.join(self.missing_required)}")
            logger.critical("Please set the required environment variables and restart.")
            sys.exit(1)


def validate_secrets(environment: Optional[str] = None, strict: bool = True) -> SecretsValidator:
    """
    Convenience function to validate secrets.
    
    Args:
        environment: Environment to validate for (default: from ENVIRONMENT env var)
        strict: If True and in non-demo mode, exit on missing required secrets
    
    Returns:
        SecretsValidator instance with results
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    # Check if we're in demo mode
    demo_mode = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    
    validator = SecretsValidator(environment=environment, strict=strict)
    
    if strict and not demo_mode:
        validator.fail_fast()
    else:
        # In demo mode or non-strict mode, just validate without exiting
        validator.validate_all()
        if demo_mode:
            logger.info("🎮 Demo mode: Skipping strict secret validation")
    
    return validator


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret from environment variables.
    
    Args:
        name: Name of the environment variable
        default: Default value if not found
    
    Returns:
        The secret value or default
    """
    value = os.getenv(name)
    return value if value else default


if __name__ == "__main__":
    # Run validation when executed directly
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate secrets")
    parser.add_argument("--env", default="development", help="Environment")
    parser.add_argument("--strict", action="store_true", help="Exit on failure")
    args = parser.parse_args()
    
    validator = SecretsValidator(environment=args.env, strict=args.strict)
    success = validator.validate_all()
    sys.exit(0 if success else 1)
