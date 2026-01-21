"""
Secrets Validator
Validates all required environment variables are present at startup
Fails fast if critical secrets are missing or invalid

Usage:
    from config.secrets_validator import validate_secrets
    
    # At application startup (in main.py)
    validate_secrets(environment='production')  # Exits if validation fails
"""

import os
import sys
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels"""
    REQUIRED = "required"      # Must be present and valid
    RECOMMENDED = "recommended"  # Should be present (warning if missing)
    OPTIONAL = "optional"       # Nice to have (info if missing)


@dataclass
class SecretRequirement:
    """
    Definition of a required/recommended secret
    
    Attributes:
        name: Environment variable name
        description: Human-readable description
        level: Validation level (required, recommended, optional)
        min_length: Minimum length for the value
        max_length: Maximum length for the value
        pattern: Regex pattern the value must match
        environments: List of environments where this applies (None = all)
        validator: Custom validation function
    """
    name: str
    description: str
    level: ValidationLevel = ValidationLevel.REQUIRED
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    environments: Optional[List[str]] = None
    validator: Optional[callable] = None


class SecretsValidator:
    """
    Validates environment variables and secrets
    Fails fast if critical secrets are missing or invalid
    """
    
    # Define all secrets with their validation rules
    SECRETS = [
        # ===== DATABASE =====
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
            level=ValidationLevel.REQUIRED,
        ),
        SecretRequirement(
            name="POSTGRES_USER",
            description="PostgreSQL user",
            level=ValidationLevel.REQUIRED,
        ),
        
        # ===== EXCHANGE APIs =====
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
        
        # ===== SECURITY =====
        SecretRequirement(
            name="SECRET_KEY",
            description="Application secret key for JWT/sessions",
            level=ValidationLevel.REQUIRED,
            min_length=32,
        ),
        SecretRequirement(
            name="DASHBOARD_PASSWORD",
            description="Dashboard authentication password",
            level=ValidationLevel.REQUIRED,
            min_length=12,
            environments=["production", "staging"]
        ),
        
        # ===== NOTIFICATIONS (Recommended) =====
        SecretRequirement(
            name="TELEGRAM_BOT_TOKEN",
            description="Telegram bot token for alerts",
            level=ValidationLevel.RECOMMENDED,
            pattern=r'^\d+:[A-Za-z0-9_-]+$'
        ),
        SecretRequirement(
            name="TELEGRAM_CHAT_ID",
            description="Telegram chat ID for alerts",
            level=ValidationLevel.RECOMMENDED,
        ),
        SecretRequirement(
            name="SLACK_WEBHOOK_URL",
            description="Slack webhook URL for notifications",
            level=ValidationLevel.RECOMMENDED,
            pattern=r'^https://hooks\.slack\.com/services/.*$'
        ),
        
        # ===== MONITORING (Recommended for production) =====
        SecretRequirement(
            name="SENTRY_DSN",
            description="Sentry DSN for error tracking",
            level=ValidationLevel.RECOMMENDED,
            environments=["production"],
            pattern=r'^https://.*@sentry\.io/.*$'
        ),
        
        # ===== OPTIONAL =====
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
        Initialize validator
        
        Args:
            environment: Current environment (development, staging, production)
            strict: If True, fail on any error. If False, only warn.
        """
        self.environment = environment
        self.strict = strict
        
        # Validation results
        self.missing_required: List[str] = []
        self.missing_recommended: List[str] = []
        self.missing_optional: List[str] = []
        self.invalid_secrets: Dict[str, str] = {}
        self.warnings: List[str] = []
        
    def validate_all(self) -> bool:
        """
        Validate all required secrets
        
        Returns:
            True if all validations pass, False otherwise
        """
        logger.info(f"Validating secrets for environment: {self.environment}")
        logger.info("=" * 70)
        
        for requirement in self.SECRETS:
            self._validate_secret(requirement)
        
        # Report results
        self._report_results()
        
        # Determine if validation passed
        has_critical_issues = bool(
            self.missing_required or 
            self.invalid_secrets
        )
        
        if has_critical_issues:
            logger.critical("\u274c SECRET VALIDATION FAILED")
            logger.critical("Cannot start application with invalid configuration")
            logger.critical("Please check .env file and set all required variables")
            logger.critical("See .env.example for reference")
            return False
        
        if self.missing_recommended:
            logger.warning(
                f"\u26a0\ufe0f  {len(self.missing_recommended)} recommended secrets missing. "
                "Application will run but with reduced functionality."
            )
        
        logger.info("\u2705 All required secrets validated successfully")
        logger.info("=" * 70)
        return True
    
    def _validate_secret(self, requirement: SecretRequirement):
        """
        Validate a single secret
        
        Args:
            requirement: Secret requirement definition
        """
        # Check if applicable to current environment
        if requirement.environments and self.environment not in requirement.environments:
            logger.debug(f"Skipping {requirement.name} (not required in {self.environment})")
            return
        
        value = os.getenv(requirement.name)
        
        # Check if present
        if value is None or value == "":
            self._handle_missing_secret(requirement)
            return
        
        # Validate the value
        validation_error = self._validate_value(value, requirement)
        if validation_error:
            self.invalid_secrets[requirement.name] = validation_error
            logger.error(
                f"\u274c {requirement.name}: {validation_error} "
                f"({requirement.description})"
            )
            return
        
        # Custom validator if provided
        if requirement.validator:
            try:
                if not requirement.validator(value):
                    self.invalid_secrets[requirement.name] = "Failed custom validation"
                    logger.error(f"\u274c {requirement.name}: Failed custom validation")
                    return
            except Exception as e:
                self.invalid_secrets[requirement.name] = f"Validation error: {e}"
                logger.error(f"\u274c {requirement.name}: {e}")
                return
        
        # Passed all checks
        logger.debug(f"\u2713 {requirement.name} validated")
    
    def _handle_missing_secret(self, requirement: SecretRequirement):
        """Handle missing secret based on validation level"""
        
        if requirement.level == ValidationLevel.REQUIRED:
            self.missing_required.append(requirement.name)
            logger.error(
                f"\u274c Missing REQUIRED secret: {requirement.name} "
                f"({requirement.description})"
            )
        
        elif requirement.level == ValidationLevel.RECOMMENDED:
            self.missing_recommended.append(requirement.name)
            logger.warning(
                f"\u26a0\ufe0f  Missing RECOMMENDED secret: {requirement.name} "
                f"({requirement.description})"
            )
        
        elif requirement.level == ValidationLevel.OPTIONAL:
            self.missing_optional.append(requirement.name)
            logger.debug(
                f"\u2139\ufe0f  Optional secret not set: {requirement.name} "
                f"({requirement.description})"
            )
    
    def _validate_value(self, value: str, requirement: SecretRequirement) -> Optional[str]:
        """
        Validate secret value against requirements
        
        Args:
            value: Secret value to validate
            requirement: Secret requirement definition
            
        Returns:
            Error message if validation fails, None otherwise
        """
        # Check minimum length
        if requirement.min_length and len(value) < requirement.min_length:
            return (
                f"Too short (min {requirement.min_length} chars, got {len(value)})"
            )
        
        # Check maximum length
        if requirement.max_length and len(value) > requirement.max_length:
            return (
                f"Too long (max {requirement.max_length} chars, got {len(value)})"
            )
        
        # Check pattern
        if requirement.pattern:
            if not re.match(requirement.pattern, value):
                return "Does not match required pattern"
        
        # Check for common insecure values
        insecure_values = [
            'password', 'changeme', 'admin', '12345678', 'test', 'example',
            'your_', 'replace_', 'enter_', 'insert_'
        ]
        value_lower = value.lower()
        if any(insecure in value_lower for insecure in insecure_values):
            return "Appears to be a placeholder value (not a real secret)"
        
        return None
    
    def _report_results(self):
        """Report validation results to logger"""
        
        if self.missing_required:
            logger.error("")
            logger.error(
                f"\u274c MISSING REQUIRED SECRETS ({len(self.missing_required)}):")
            for name in self.missing_required:
                logger.error(f"  • {name}")
        
        if self.invalid_secrets:
            logger.error("")
            logger.error(f"\u274c INVALID SECRETS ({len(self.invalid_secrets)}):")
            for name, reason in self.invalid_secrets.items():
                logger.error(f"  • {name}: {reason}")
        
        if self.missing_recommended:
            logger.warning("")
            logger.warning(
                f"\u26a0\ufe0f  MISSING RECOMMENDED SECRETS ({len(self.missing_recommended)}):")
            for name in self.missing_recommended:
                logger.warning(f"  • {name}")
        
        if self.missing_optional:
            logger.info("")
            logger.info(
                f"\u2139\ufe0f  OPTIONAL SECRETS NOT SET ({len(self.missing_optional)}):")
            for name in self.missing_optional:
                logger.info(f"  • {name}")
    
    def fail_fast(self):
        """
        Validate and exit if validation fails
        
        Call this at application startup to prevent running with invalid config
        """
        if not self.validate_all():
            logger.critical("")
            logger.critical("EXITING due to invalid secrets configuration")
            logger.critical("")
            logger.critical("To fix:")
            logger.critical("  1. Copy .env.example to .env")
            logger.critical("  2. Fill in all REQUIRED values")
            logger.critical("  3. Ensure passwords are strong (min 8-12 chars)")
            logger.critical("  4. Never use placeholder values in production")
            logger.critical("")
            sys.exit(1)
    
    def get_summary(self) -> Dict:
        """
        Get validation summary as dictionary
        
        Returns:
            Dictionary with validation results
        """
        return {
            'environment': self.environment,
            'validation_passed': not (self.missing_required or self.invalid_secrets),
            'missing_required': self.missing_required,
            'missing_recommended': self.missing_recommended,
            'missing_optional': self.missing_optional,
            'invalid_secrets': self.invalid_secrets,
            'warnings': self.warnings,
        }


def validate_secrets(
    environment: Optional[str] = None,
    strict: bool = True
) -> SecretsValidator:
    """
    Convenience function to validate secrets
    
    Args:
        environment: Environment name (defaults to ENVIRONMENT env var)
        strict: If True, exit on validation failure
        
    Returns:
        SecretsValidator instance
        
    Raises:
        SystemExit: If validation fails and strict=True
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    validator = SecretsValidator(environment=environment, strict=strict)
    
    if strict:
        validator.fail_fast()
    else:
        validator.validate_all()
    
    return validator


def check_secret_exists(name: str) -> bool:
    """
    Quick check if a secret exists and is not empty
    
    Args:
        name: Environment variable name
        
    Returns:
        True if secret exists and is not empty, False otherwise
    """
    value = os.getenv(name)
    return value is not None and value != ""


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get secret value with optional default
    
    Args:
        name: Environment variable name
        default: Default value if not found
        
    Returns:
        Secret value or default
    """
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


if __name__ == "__main__":
    """
    Run standalone validation
    
    Usage:
        python -m src.config.secrets_validator
    """
    # Setup logging for standalone run
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    # Get environment from command line or env var
    import sys
    environment = sys.argv[1] if len(sys.argv) > 1 else os.getenv("ENVIRONMENT", "development")
    
    print(f"\nValidating secrets for environment: {environment}\n")
    
    validator = SecretsValidator(environment=environment)
    passed = validator.validate_all()
    
    print("\n" + "=" * 70)
    if passed:
        print("\u2705 VALIDATION PASSED")
        sys.exit(0)
    else:
        print("\u274c VALIDATION FAILED")
        sys.exit(1)
