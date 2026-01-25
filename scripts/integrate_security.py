#!/usr/bin/env python3
"""Security Integration Script

Automatically integrates security modules into web_app.py.
Backups original file before making changes.

Usage:
    python scripts/integrate_security.py
    python scripts/integrate_security.py --dry-run  # Preview changes
    python scripts/integrate_security.py --rollback  # Restore backup
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

WEB_APP_PATH = project_root / 'src' / 'dashboard' / 'web_app.py'
BACKUP_DIR = project_root / 'backups'


def create_backup():
    """Create backup of web_app.py"""
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f'web_app_{timestamp}.py'
    
    shutil.copy2(WEB_APP_PATH, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    return backup_path


def find_latest_backup():
    """Find most recent backup"""
    if not BACKUP_DIR.exists():
        return None
    
    backups = list(BACKUP_DIR.glob('web_app_*.py'))
    if not backups:
        return None
    
    return max(backups, key=lambda p: p.stat().st_mtime)


def rollback():
    """Restore from latest backup"""
    backup = find_latest_backup()
    
    if not backup:
        print("❌ No backup found!")
        return False
    
    shutil.copy2(backup, WEB_APP_PATH)
    print(f"✅ Restored from backup: {backup}")
    return True


def read_file():
    """Read web_app.py content"""
    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        return f.read()


def write_file(content):
    """Write web_app.py content"""
    with open(WEB_APP_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def add_imports(content):
    """Add security imports"""
    # Find import section
    import_marker = 'from flask import'
    if import_marker not in content:
        print("⚠️ Could not find Flask import")
        return content
    
    # Security imports to add
    security_imports = '''
# ✅ Security Modules - Phase 1
from src.security.csrf_protection import init_csrf_protection
from src.security.xss_protection import xss_protection_middleware
from src.security.input_validator import (
    LoginRequest,
    AnnotationRequest,
    ConfigUpdateRequest,
    validate_request_data
)
'''
    
    # Check if already added
    if 'csrf_protection import' in content:
        print("ℹ️ Security imports already present")
        return content
    
    # Insert after Flask import
    insert_pos = content.find(import_marker)
    end_of_line = content.find('\n', insert_pos)
    
    new_content = (
        content[:end_of_line + 1] +
        security_imports +
        content[end_of_line + 1:]
    )
    
    print("✅ Added security imports")
    return new_content


def add_csrf_init(content):
    """Add CSRF initialization"""
    # Find __init__ method of ProfessionalDashboard
    init_marker = 'def __init__(self'
    if init_marker not in content:
        print("⚠️ Could not find __init__ method")
        return content
    
    # Check if already added
    if 'init_csrf_protection' in content:
        print("ℹ️ CSRF initialization already present")
        return content
    
    # CSRF initialization code
    csrf_init = '''
        
        # ✅ Initialize CSRF Protection
        self.csrf = init_csrf_protection(
            self.app,
            token_length=int(os.getenv('CSRF_TOKEN_LENGTH', '32')),
            token_ttl=int(os.getenv('CSRF_TOKEN_TTL', '3600'))
        )
        logger.info("✅ CSRF Protection initialized")
'''
    
    # Find where to insert (after app initialization)
    # Look for "self.app = Flask"
    app_init = content.find('self.app = Flask')
    if app_init == -1:
        print("⚠️ Could not find app initialization")
        return content
    
    # Find end of that line
    end_of_line = content.find('\n', app_init)
    
    new_content = (
        content[:end_of_line + 1] +
        csrf_init +
        content[end_of_line + 1:]
    )
    
    print("✅ Added CSRF initialization")
    return new_content


def add_xss_middleware(content):
    """Add XSS middleware initialization"""
    # Check if already added
    if 'xss_protection_middleware' in content:
        print("ℹ️ XSS middleware already present")
        return content
    
    # XSS middleware code
    xss_init = '''
        
        # ✅ Initialize XSS Protection
        if os.getenv('XSS_PROTECTION_ENABLED', 'true').lower() == 'true':
            xss_protection_middleware(
                self.app,
                strip=os.getenv('XSS_STRIP_HTML', 'false').lower() == 'true',
                detect_only=False
            )
            logger.info("✅ XSS Protection middleware enabled")
'''
    
    # Insert after CSRF init
    csrf_marker = 'CSRF Protection initialized'
    if csrf_marker not in content:
        print("⚠️ CSRF initialization not found, skipping XSS")
        return content
    
    insert_pos = content.find(csrf_marker)
    end_of_line = content.find('\n', insert_pos)
    
    new_content = (
        content[:end_of_line + 1] +
        xss_init +
        content[end_of_line + 1:]
    )
    
    print("✅ Added XSS middleware")
    return new_content


def add_env_config(content):
    """Add environment variable configuration comments"""
    env_config = '''
# ✅ Security Configuration (Environment Variables)
# Add to .env file:
#   CSRF_ENABLED=true
#   CSRF_TOKEN_LENGTH=32
#   CSRF_TOKEN_TTL=3600
#   XSS_PROTECTION_ENABLED=true
#   XSS_STRIP_HTML=false
#   RATE_LIMIT_ENABLED=true
#   FORCE_HTTPS=true  # Production only
'''
    
    # Check if already added
    if 'Security Configuration (Environment Variables)' in content:
        return content
    
    # Add at top after shebang/encoding
    lines = content.split('\n')
    insert_line = 3  # After first few lines
    
    lines.insert(insert_line, env_config)
    
    print("✅ Added environment configuration comments")
    return '\n'.join(lines)


def integrate_security(dry_run=False):
    """Main integration function"""
    print("[1m\n✨ BotV2 Security Integration Script ✨\n\u001b[0m")
    
    # Check if file exists
    if not WEB_APP_PATH.exists():
        print(f"❌ File not found: {WEB_APP_PATH}")
        return False
    
    print(f"📄 Target file: {WEB_APP_PATH}")
    
    # Create backup
    if not dry_run:
        backup_path = create_backup()
    else:
        print("ℹ️ Dry run mode - no backup created")
    
    # Read current content
    content = read_file()
    print(f"✅ Read {len(content)} bytes\n")
    
    # Apply transformations
    print("[1m🔧 Applying changes...\n\u001b[0m")
    
    original_content = content
    
    content = add_env_config(content)
    content = add_imports(content)
    content = add_csrf_init(content)
    content = add_xss_middleware(content)
    
    # Check if any changes were made
    if content == original_content:
        print("\nℹ️ No changes needed - security already integrated!")
        return True
    
    # Show diff stats
    original_lines = len(original_content.split('\n'))
    new_lines = len(content.split('\n'))
    diff = new_lines - original_lines
    
    print(f"\n📊 Stats:")
    print(f"  Original: {original_lines} lines")
    print(f"  New: {new_lines} lines")
    print(f"  Difference: +{diff} lines")
    
    if dry_run:
        print("\nℹ️ Dry run complete - no changes written")
        return True
    
    # Write changes
    write_file(content)
    print(f"\n✅ Changes written to {WEB_APP_PATH}")
    
    print("\n[1m✨ Integration Complete! ✨\u001b[0m")
    print("\n📝 Next steps:")
    print("  1. Review changes: git diff src/dashboard/web_app.py")
    print("  2. Add to .env: CSRF_ENABLED=true, XSS_PROTECTION_ENABLED=true")
    print("  3. Restart dashboard: docker compose restart botv2-dashboard")
    print("  4. Test CSRF: Try POST without token (should fail)")
    print("  5. Test XSS: Try script injection (should sanitize)")
    print(f"\n💾 Backup location: {backup_path}")
    print("   Rollback: python scripts/integrate_security.py --rollback")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Integrate security modules into web_app.py'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing'
    )
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Restore from latest backup'
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback()
        sys.exit(0 if success else 1)
    
    success = integrate_security(dry_run=args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
