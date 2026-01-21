#!/usr/bin/env python3
"""
BotV2 Security Verification Script

Verifies that all required security configurations are in place
before starting the trading system.

Usage:
    python scripts/verify_security.py
    
Exit codes:
    0 - All checks passed
    1 - Critical security issue found
    2 - Warning, some optional configs missing
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
import hashlib

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Required variables (CRITICAL - must be set)
REQUIRED_VARS = [
    ('DASHBOARD_PASSWORD', 'Dashboard authentication password'),
    ('POSTGRES_PASSWORD', 'PostgreSQL database password'),
]

# Important variables (HIGH - should be set for production)
IMPORTANT_VARS = [
    ('POLYMARKET_API_KEY', 'Polymarket exchange API key'),
    ('POSTGRES_USER', 'PostgreSQL username'),
    ('POSTGRES_DB', 'PostgreSQL database name'),
]

# Optional variables (MEDIUM - enhance functionality)
OPTIONAL_VARS = [
    ('DASHBOARD_USERNAME', 'Dashboard username (default: admin)'),
    ('TELEGRAM_BOT_TOKEN', 'Telegram bot for notifications'),
    ('SLACK_WEBHOOK_URL', 'Slack webhook for alerts'),
    ('POSTGRES_HOST', 'PostgreSQL host (default: localhost)'),
    ('POSTGRES_PORT', 'PostgreSQL port (default: 5432)'),
]

# Weak passwords to check against
WEAK_PASSWORDS = [
    'password',
    '12345678',
    'admin123',
    'botv2',
    'trading',
    'secret',
    'passw0rd',
    '123456',
]


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header():
    """Print script header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}" + "="*60 + Colors.ENDC)
    print(f"{Colors.BOLD}🔍 BotV2 Security Verification{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}" + "="*60 + Colors.ENDC + "\n")


def check_required_vars() -> Tuple[bool, List[str]]:
    """Check required environment variables"""
    print(f"{Colors.BOLD}[1/6] Checking Required Variables (CRITICAL){Colors.ENDC}")
    print("-" * 60)
    
    missing = []
    for var, description in REQUIRED_VARS:
        value = os.getenv(var)
        if not value:
            print(f"{Colors.FAIL}❌ {var}: NOT SET{Colors.ENDC}")
            print(f"   Description: {description}")
            missing.append(var)
        else:
            print(f"{Colors.OKGREEN}✅ {var}: Configured{Colors.ENDC}")
    
    print()
    return len(missing) == 0, missing


def check_important_vars() -> Tuple[bool, List[str]]:
    """Check important environment variables"""
    print(f"{Colors.BOLD}[2/6] Checking Important Variables (HIGH){Colors.ENDC}")
    print("-" * 60)
    
    missing = []
    for var, description in IMPORTANT_VARS:
        value = os.getenv(var)
        if not value:
            print(f"{Colors.WARNING}⚠️  {var}: Not set{Colors.ENDC}")
            print(f"   Description: {description}")
            missing.append(var)
        else:
            print(f"{Colors.OKGREEN}✅ {var}: Configured{Colors.ENDC}")
    
    print()
    return len(missing) == 0, missing


def check_optional_vars() -> List[str]:
    """Check optional environment variables"""
    print(f"{Colors.BOLD}[3/6] Checking Optional Variables (MEDIUM){Colors.ENDC}")
    print("-" * 60)
    
    missing = []
    for var, description in OPTIONAL_VARS:
        value = os.getenv(var)
        if value:
            print(f"{Colors.OKGREEN}✅ {var}: Configured{Colors.ENDC}")
        else:
            print(f"{Colors.OKCYAN}ℹ️  {var}: Not set (optional){Colors.ENDC}")
            print(f"   Description: {description}")
            missing.append(var)
    
    print()
    return missing


def check_password_strength() -> Tuple[bool, List[str]]:
    """Check password strength"""
    print(f"{Colors.BOLD}[4/6] Checking Password Strength{Colors.ENDC}")
    print("-" * 60)
    
    weak_found = []
    
    # Check dashboard password
    dashboard_pass = os.getenv('DASHBOARD_PASSWORD')
    if dashboard_pass:
        # Check length
        if len(dashboard_pass) < 12:
            print(f"{Colors.WARNING}⚠️  DASHBOARD_PASSWORD: Too short (< 12 chars){Colors.ENDC}")
            print(f"   Current length: {len(dashboard_pass)} characters")
            print(f"   Recommended: At least 16 characters")
            weak_found.append('DASHBOARD_PASSWORD (length)')
        else:
            print(f"{Colors.OKGREEN}✅ DASHBOARD_PASSWORD: Length OK ({len(dashboard_pass)} chars){Colors.ENDC}")
        
        # Check against common weak passwords
        password_lower = dashboard_pass.lower()
        for weak in WEAK_PASSWORDS:
            if weak in password_lower:
                print(f"{Colors.FAIL}❌ DASHBOARD_PASSWORD: Contains weak pattern '{weak}'{Colors.ENDC}")
                weak_found.append(f'DASHBOARD_PASSWORD (pattern: {weak})')
                break
        else:
            print(f"{Colors.OKGREEN}✅ DASHBOARD_PASSWORD: No weak patterns detected{Colors.ENDC}")
        
        # Check complexity
        has_upper = any(c.isupper() for c in dashboard_pass)
        has_lower = any(c.islower() for c in dashboard_pass)
        has_digit = any(c.isdigit() for c in dashboard_pass)
        has_special = any(not c.isalnum() for c in dashboard_pass)
        
        complexity_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if complexity_score < 3:
            print(f"{Colors.WARNING}⚠️  DASHBOARD_PASSWORD: Low complexity (score: {complexity_score}/4){Colors.ENDC}")
            print(f"   Recommend: Use uppercase, lowercase, digits, and special chars")
            weak_found.append('DASHBOARD_PASSWORD (complexity)')
        else:
            print(f"{Colors.OKGREEN}✅ DASHBOARD_PASSWORD: Good complexity (score: {complexity_score}/4){Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ DASHBOARD_PASSWORD: Not set (already reported){Colors.ENDC}")
    
    print()
    return len(weak_found) == 0, weak_found


def check_gitignore() -> bool:
    """Check if .env is in .gitignore"""
    print(f"{Colors.BOLD}[5/6] Checking .gitignore Configuration{Colors.ENDC}")
    print("-" * 60)
    
    gitignore_path = Path('.gitignore')
    
    if not gitignore_path.exists():
        print(f"{Colors.WARNING}⚠️  .gitignore: File not found{Colors.ENDC}")
        print(f"   Create .gitignore to prevent committing secrets")
        return False
    
    with open(gitignore_path, 'r') as f:
        content = f.read()
    
    has_env = '.env' in content
    has_secrets = any(pattern in content for pattern in ['*.key', '*.pem', 'secrets'])
    
    if has_env:
        print(f"{Colors.OKGREEN}✅ .gitignore: .env is ignored{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ .gitignore: .env is NOT ignored{Colors.ENDC}")
        print(f"   Add '.env' to .gitignore immediately!")
    
    if has_secrets:
        print(f"{Colors.OKGREEN}✅ .gitignore: Secret files are ignored{Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}⚠️  .gitignore: Consider adding *.key, *.pem, secrets/{Colors.ENDC}")
    
    print()
    return has_env


def check_env_file() -> bool:
    """Check if .env file exists and has proper permissions"""
    print(f"{Colors.BOLD}[6/6] Checking .env File Security{Colors.ENDC}")
    print("-" * 60)
    
    env_path = Path('.env')
    
    if not env_path.exists():
        print(f"{Colors.WARNING}⚠️  .env: File not found{Colors.ENDC}")
        print(f"   Consider creating .env for easier credential management")
        return True  # Not critical if using export
    
    print(f"{Colors.OKGREEN}✅ .env: File exists{Colors.ENDC}")
    
    # Check permissions (Unix only)
    if sys.platform != 'win32':
        import stat
        mode = os.stat(env_path).st_mode
        permissions = stat.filemode(mode)
        
        # Check if readable by others
        if mode & stat.S_IROTH:
            print(f"{Colors.FAIL}❌ .env: Too permissive ({permissions}){Colors.ENDC}")
            print(f"   Run: chmod 600 .env")
            return False
        else:
            print(f"{Colors.OKGREEN}✅ .env: Permissions OK ({permissions}){Colors.ENDC}")
    
    print()
    return True


def generate_report(checks: dict) -> int:
    """Generate final security report"""
    print(f"{Colors.BOLD}{Colors.HEADER}" + "="*60 + Colors.ENDC)
    print(f"{Colors.BOLD}SECURITY VERIFICATION REPORT{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}" + "="*60 + Colors.ENDC + "\n")
    
    # Count issues
    critical_issues = len(checks['required_missing'])
    high_issues = len(checks['important_missing'])
    medium_issues = len(checks['weak_passwords'])
    low_issues = 0
    if not checks['gitignore_ok']:
        low_issues += 1
    if not checks['env_file_ok']:
        low_issues += 1
    
    total_issues = critical_issues + high_issues + medium_issues + low_issues
    
    # Print summary
    print(f"Total Issues Found: {total_issues}")
    print(f"  - Critical (P0): {critical_issues}")
    print(f"  - High (P1): {high_issues}")
    print(f"  - Medium (P2): {medium_issues}")
    print(f"  - Low (P3): {low_issues}")
    print()
    
    # Print details
    if critical_issues > 0:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ CRITICAL ISSUES (Must fix before starting):{Colors.ENDC}")
        for var in checks['required_missing']:
            print(f"   - {var} is not set")
        print()
    
    if high_issues > 0:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  HIGH PRIORITY (Fix for production):{Colors.ENDC}")
        for var in checks['important_missing']:
            print(f"   - {var} is not set")
        print()
    
    if medium_issues > 0:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  MEDIUM PRIORITY (Improve security):{Colors.ENDC}")
        for issue in checks['weak_passwords']:
            print(f"   - {issue}")
        print()
    
    # Overall verdict
    if critical_issues > 0:
        print(f"{Colors.FAIL}{Colors.BOLD}❌ SECURITY CHECK FAILED{Colors.ENDC}")
        print(f"\nCritical security issues found. Fix them before starting BotV2!")
        print(f"\nRecommended actions:")
        for var in checks['required_missing']:
            print(f"  export {var}=\"your_secure_value\"")
        return 1
    
    elif high_issues > 0 or medium_issues > 0:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  SECURITY CHECK PASSED WITH WARNINGS{Colors.ENDC}")
        print(f"\nYou can start BotV2, but fix these issues for production:")
        if high_issues > 0:
            print(f"\nHigh priority:")
            for var in checks['important_missing']:
                print(f"  export {var}=\"your_value\"")
        if medium_issues > 0:
            print(f"\nMedium priority:")
            print(f"  - Use stronger passwords (16+ chars, mixed case, digits, special)")
        return 2
    
    else:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ SECURITY CHECK PASSED{Colors.ENDC}")
        print(f"\nAll security checks passed. BotV2 is ready to start!")
        print(f"{Colors.OKGREEN}🚀 You can now run: python src/main.py{Colors.ENDC}")
        return 0


def main():
    """Main execution"""
    print_header()
    
    # Run all checks
    checks = {
        'required_ok': False,
        'required_missing': [],
        'important_ok': False,
        'important_missing': [],
        'optional_missing': [],
        'passwords_ok': False,
        'weak_passwords': [],
        'gitignore_ok': False,
        'env_file_ok': False,
    }
    
    checks['required_ok'], checks['required_missing'] = check_required_vars()
    checks['important_ok'], checks['important_missing'] = check_important_vars()
    checks['optional_missing'] = check_optional_vars()
    checks['passwords_ok'], checks['weak_passwords'] = check_password_strength()
    checks['gitignore_ok'] = check_gitignore()
    checks['env_file_ok'] = check_env_file()
    
    # Generate report and exit
    exit_code = generate_report(checks)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
