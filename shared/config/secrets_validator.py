\"\"\"
Secrets Validator
Validates all required environment variables are present at startup
Fails fast if critical secrets are missing or invalid
Usage:
    from shared.config.secrets_validator import validate_secrets
\"\"\"
import os
import sys
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# Use professional logger
try:
    from shared.utils.professional_logger import setup_professional_logger
    logger, reporter = setup_professional_logger(
        name=__name__,
        log_file=\"logs/validation.log\",
        level=logging.INFO
    )
    HAS_PROFESSIONAL_LOGGER = True
except ImportError:
    # Fallback to standard logging
    logger = logging.getLogger(__name__)
    reporter = None
    HAS_PROFESSIONAL_LOGGER = False

class ValidationLevel(Enum):
    \"\"\"Validation severity levels\"\"\"
    REQUIRED = \"required\" # Must be present and valid
    RECOMMENDED = \"recommended\" # Should be present (warning if missing)
    OPTIONAL = \"optional\" # Nice to have (info if missing)

@dataclass
class SecretRequirement:
    name: str
    description: str
    level: ValidationLevel = ValidationLevel.REQUIRED
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    environments: Optional[List[str]] = None
    validator: Optional[callable] = None

class SecretsValidator:
    # Define all secrets with their validation rules
    SECRETS = [
        SecretRequirement(
            name=\"POSTGRES_PASSWORD\",
            description=\"PostgreSQL database password\",
            level=ValidationLevel.REQUIRED,
            min_length=8,
            environments=[\"production\", \"staging\"]
        ),
        SecretRequirement(
            name=\"POSTGRES_HOST\",
            description=\"PostgreSQL host\",
            level=ValidationLevel.REQUIRED,
            environments=[\"production\", \"staging\"]
        ),
        SecretRequirement(
            name=\"POSTGRES_DATABASE\",
            description=\"PostgreSQL database name\",
            level=ValidationLevel.REQUIRED,
        ),
        SecretRequirement(
            name=\"POSTGRES_USER\",
            description=\"PostgreSQL user\",
            level=ValidationLevel.REQUIRED,
        ),
        SecretRequirement(
            name=\"POLYMARKET_API_KEY\",
            description=\"Polymarket API key\",
            level=ValidationLevel.REQUIRED,
            min_length=20,
            environments=[\"production\", \"staging\"]
        ),
        SecretRequirement(
            name=\"POLYMARKET_API_SECRET\",
            description=\"Polymarket API secret\",
            level=ValidationLevel.REQUIRED,
            min_length=32,
            environments=[\"production\", \"staging\"]
        ),
        SecretRequirement(
            name=\"SECRET_KEY\",
            description=\"Application secret key for JWT/sessions\",
            level=ValidationLevel.REQUIRED,
            min_length=32,
        ),
        SecretRequirement(
            name=\"DASHBOARD_PASSWORD\",
            description=\"Dashboard authentication password\",
            level=ValidationLevel.REQUIRED,
            min_length=12,
            environments=[\"production\", \"staging\"]
        ),
        SecretRequirement(
            name=\"TELEGRAM_BOT_TOKEN\",
            description=\"Telegram bot token for alerts\",
            level=ValidationLevel.RECOMMENDED,
            pattern=r'^\\d+:[A-Za-z0-9_-]+$'
        ),
        SecretRequirement(
            name=\"TELEGRAM_CHAT_ID\",
            description=\"Telegram chat ID for alerts\",
            level=ValidationLevel.RECOMMENDED,
        ),
        SecretRequirement(
            name=\"SLACK_WEBHOOK_URL\",
            description=\"Slack webhook URL for notifications\",
            level=ValidationLevel.RECOMMENDED,
            pattern=r'^https://hooks\\.slack\\.com/services/.*$'
        ),
        SecretRequirement(
            name=\"SENTRY_DSN\",
            description=\"Sentry DSN for error tracking\",
            level=ValidationLevel.RECOMMENDED,
            environments=[\"production\"],
            pattern=r'^https://.*@sentry\\.io/.*$'
        ),
        SecretRequirement(
            name=\"TWITTER_BEARER_TOKEN\",
            description=\"Twitter API bearer token for sentiment analysis\",
            level=ValidationLevel.OPTIONAL,
        ),
        SecretRequirement(
            name=\"OPENAI_API_KEY\",
            description=\"OpenAI API key for AI features\",
            level=ValidationLevel.OPTIONAL,
            pattern=r'^sk-[A-Za-z0-9]+$'
        ),
    ]

    def __init__(self, environment: str = \"development\", strict: bool = True):
        self.environment = environment
        self.strict = strict
        self.missing_required: List[str] = []
        self.missing_recommended: List[str] = []
        self.missing_optional: List[str] = []
        self.invalid_secrets: Dict[str, str] = {}
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        if HAS_PROFESSIONAL_LOGGER and reporter:
            reporter.report_validation_start(self.environment)
        else:
            logger.info(f\"Validating secrets for environment: {self.environment}\")
        for requirement in self.SECRETS:
            self._validate_secret(requirement)
        self._report_results()
        has_critical_issues = bool(self.missing_required or self.invalid_secrets)
        if has_critical_issues:
            return False
        return True

    def _validate_secret(self, requirement: SecretRequirement):
        if requirement.environments and self.environment not in requirement.environments:
            return
        value = os.getenv(requirement.name)
        if value is None or value == \"\":
            self._handle_missing_secret(requirement)
            return
        validation_error = self._validate_value(value, requirement)
        if validation_error:
            self.invalid_secrets[requirement.name] = validation_error
            return
        if requirement.validator:
            if not requirement.validator(value):
                self.invalid_secrets[requirement.name] = \"Failed custom validation\"

    def _handle_missing_secret(self, requirement: SecretRequirement):
        if requirement.level == ValidationLevel.REQUIRED:
            self.missing_required.append(requirement.name)
        elif requirement.level == ValidationLevel.RECOMMENDED:
            self.missing_recommended.append(requirement.name)

    def _validate_value(self, value: str, requirement: SecretRequirement) -> Optional[str]:
        if requirement.min_length and len(value) < requirement.min_length:
            return f\"Too short (min {requirement.min_length})\"
        if requirement.pattern and not re.match(requirement.pattern, value):
            return \"Does not match required pattern\"
        return None

    def _report_results(self):
        if HAS_PROFESSIONAL_LOGGER and reporter:
            results = []
            for req in self.SECRETS:
                if req.environments and self.environment not in req.environments: continue
                is_valid = req.name not in self.missing_required and req.name not in self.invalid_secrets
                results.append((req.name, is_valid, req.description))
            reporter.report_validation_results(results, self.environment)

    def fail_fast(self):
        if not self.validate_all():
            sys.exit(1)

def validate_secrets(environment: Optional[str] = None, strict: bool = True) -> SecretsValidator:
    if environment is None:
        environment = os.getenv(\"ENVIRONMENT\", \"development\")
    validator = SecretsValidator(environment=environment, strict=strict)
    if strict: validator.fail_fast()
    else: validator.validate_all()
    return validator

def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return value if value else default

if __name__ == \"__main__\":
    validator = SecretsValidator()
    sys.exit(0 if validator.validate_all() else 1)
