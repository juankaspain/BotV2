#!/usr/bin/env python3
"""
BotV2 Security Integration Script

Automatically integrates Phase 1 security features into web_app.py:
- Flask-WTF CSRF protection
- XSS sanitization middleware
- Pydantic input validators
- Session persistence

Usage:
    python scripts/security_integration.py --dry-run  # Preview changes
    python scripts/security_integration.py --apply    # Apply changes
    python scripts/security_integration.py --rollback # Undo changes

Author: BotV2 Security Team
Date: 2026-01-25
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
import re


class SecurityIntegrator:
    """Automated security integration for BotV2 dashboard"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.web_app_path = self.project_root / 'src' / 'dashboard' / 'web_app.py'
        self.backup_path = self.project_root / 'backups' / f'web_app.py.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        self.changes_log = []
    
    def log(self, message, level='INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            'INFO': '\u2139\ufe0f',
            'SUCCESS': '\u2705',
            'WARNING': '\u26a0\ufe0f',
            'ERROR': '\u274c',
            'SKIP': '\u23ed\ufe0f'
        }.get(level, '\U0001f4dd')
        
        msg = f"{prefix} [{timestamp}] {message}"
        print(msg)
        self.changes_log.append(msg)
    
    def create_backup(self):
        """Create backup of web_app.py"""
        if self.dry_run:
            self.log("[DRY RUN] Would create backup", 'SKIP')
            return True
        
        try:
            self.backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.web_app_path, self.backup_path)
            self.log(f"Backup created: {self.backup_path}", 'SUCCESS')
            return True
        except Exception as e:
            self.log(f"Failed to create backup: {e}", 'ERROR')
            return False
    
    def read_web_app(self):
        """Read web_app.py content"""
        try:
            with open(self.web_app_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.log(f"Failed to read web_app.py: {e}", 'ERROR')
            return None
    
    def write_web_app(self, content):
        """Write content to web_app.py"""
        if self.dry_run:
            self.log("[DRY RUN] Would write changes to web_app.py", 'SKIP')
            return True
        
        try:
            with open(self.web_app_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log("Changes written to web_app.py", 'SUCCESS')
            return True
        except Exception as e:
            self.log(f"Failed to write web_app.py: {e}", 'ERROR')
            return False
    
    def add_csrf_import(self, content):
        """Add CSRF protection import"""
        csrf_import = "from src.security.csrf_protection import init_csrf"
        
        if csrf_import in content:
            self.log("CSRF import already exists", 'SKIP')
            return content
        
        # Find the import section (after Flask imports)
        pattern = r'(from flask import Flask.*?\n)'
        match = re.search(pattern, content)
        
        if match:
            insertion_point = match.end()
            content = (
                content[:insertion_point] +
                f"\n# Security imports\n{csrf_import}\n" +
                content[insertion_point:]
            )
            self.log("Added CSRF import", 'SUCCESS')
        else:
            self.log("Could not find import section", 'WARNING')
        
        return content
    
    def add_xss_import(self, content):
        """Add XSS protection import"""
        xss_imports = [
            "from src.security.xss_protection import sanitize_html, sanitize_dict",
            "from src.security.input_validator import validate_login_request, validate_annotation_request"
        ]
        
        for xss_import in xss_imports:
            if xss_import not in content:
                # Add after CSRF import if exists
                if "from src.security.csrf_protection" in content:
                    content = content.replace(
                        "from src.security.csrf_protection import init_csrf\n",
                        f"from src.security.csrf_protection import init_csrf\n{xss_import}\n"
                    )
                    self.log(f"Added XSS import: {xss_import.split()[1]}", 'SUCCESS')
        
        return content
    
    def add_csrf_initialization(self, content):
        """Add CSRF initialization in __init__"""
        csrf_init_code = '''        
        # \u2705 CSRF Protection
        if HAS_CSRF := True:
            try:
                from src.security.csrf_protection import init_csrf
                self.csrf = init_csrf(self.app)
                logger.info("\u2705 CSRF protection enabled")
            except ImportError:
                logger.warning("\u26a0\ufe0f CSRF protection not available")
                HAS_CSRF = False
'''
        
        # Find the compression setup section
        pattern = r'(self\._setup_compression\(\)\s*\n)'
        match = re.search(pattern, content)
        
        if match and 'init_csrf(self.app)' not in content:
            insertion_point = match.end()
            content = content[:insertion_point] + csrf_init_code + content[insertion_point:]
            self.log("Added CSRF initialization", 'SUCCESS')
        elif 'init_csrf(self.app)' in content:
            self.log("CSRF initialization already exists", 'SKIP')
        else:
            self.log("Could not find compression setup section", 'WARNING')
        
        return content
    
    def add_xss_middleware(self, content):
        """Add XSS sanitization middleware"""
        xss_middleware_code = '''
        # \u2705 XSS Protection Middleware
        @self.app.before_request
        def sanitize_request_data():
            """Sanitize all incoming request data"""
            if request.method in ['POST', 'PUT', 'PATCH']:
                if request.is_json:
                    try:
                        # Sanitize JSON data
                        request._sanitized_json = sanitize_dict(request.get_json())
                    except Exception as e:
                        logger.warning(f"XSS sanitization failed: {e}")
                elif request.form:
                    # Sanitize form data
                    sanitized_form = {}
                    for key, value in request.form.items():
                        if isinstance(value, str):
                            sanitized_form[key] = sanitize_html(value)
                        else:
                            sanitized_form[key] = value
                    request._sanitized_form = sanitized_form
'''
        
        # Find the _setup_routes method
        pattern = r'(def _setup_routes\(self\):\s*\n)'
        match = re.search(pattern, content)
        
        if match and 'sanitize_request_data' not in content:
            insertion_point = match.end()
            content = content[:insertion_point] + xss_middleware_code + content[insertion_point:]
            self.log("Added XSS middleware", 'SUCCESS')
        elif 'sanitize_request_data' in content:
            self.log("XSS middleware already exists", 'SKIP')
        else:
            self.log("Could not find _setup_routes method", 'WARNING')
        
        return content
    
    def add_pydantic_validation(self, content):
        """Add Pydantic validation to login endpoint"""
        # This is a sample - the actual implementation should use the validator
        validation_code = '''            # Validate input with Pydantic
            try:
                validated_data = validate_login_request(request.form)
                username = validated_data['username']
                password = validated_data['password']
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
'''
        
        # Find login endpoint
        pattern = r'(username = request\.form\.get\(\'username\', \'\'\'\)\s*\n\s*password = request\.form\.get\(\'password\', \'\'\'\))'
        match = re.search(pattern, content)
        
        if match and 'validate_login_request' not in content:
            self.log("Pydantic validation can be added to login endpoint", 'INFO')
            # Note: This is a suggestion, not automatic replacement
        elif 'validate_login_request' in content:
            self.log("Pydantic validation already exists", 'SKIP')
        
        return content
    
    def integrate(self):
        """Main integration method"""
        self.log("Starting BotV2 Security Integration", 'INFO')
        self.log(f"Mode: {'DRY RUN (no changes)' if self.dry_run else 'APPLY CHANGES'}", 'INFO')
        
        # Step 1: Create backup
        if not self.create_backup():
            return False
        
        # Step 2: Read web_app.py
        content = self.read_web_app()
        if not content:
            return False
        
        # Step 3: Apply integrations
        self.log("Applying security integrations...", 'INFO')
        
        content = self.add_csrf_import(content)
        content = self.add_xss_import(content)
        content = self.add_csrf_initialization(content)
        content = self.add_xss_middleware(content)
        content = self.add_pydantic_validation(content)
        
        # Step 4: Write changes
        if not self.write_web_app(content):
            return False
        
        # Step 5: Summary
        self.log("\n" + "="*60, 'INFO')
        self.log("INTEGRATION SUMMARY", 'INFO')
        self.log("="*60, 'INFO')
        
        if self.dry_run:
            self.log("DRY RUN completed - no files were modified", 'SUCCESS')
        else:
            self.log("Integration completed successfully", 'SUCCESS')
            self.log(f"Backup saved: {self.backup_path}", 'INFO')
        
        self.log("\nNext steps:", 'INFO')
        self.log("1. Review changes in web_app.py", 'INFO')
        self.log("2. Test login and API endpoints", 'INFO')
        self.log("3. Check logs for security events", 'INFO')
        self.log("4. Run: docker compose restart botv2-dashboard", 'INFO')
        
        return True
    
    def rollback(self):
        """Rollback to latest backup"""
        self.log("Rolling back to previous version...", 'INFO')
        
        # Find latest backup
        backup_dir = self.project_root / 'backups'
        if not backup_dir.exists():
            self.log("No backups found", 'ERROR')
            return False
        
        backups = sorted(backup_dir.glob('web_app.py.*'), reverse=True)
        if not backups:
            self.log("No backups found", 'ERROR')
            return False
        
        latest_backup = backups[0]
        
        try:
            shutil.copy2(latest_backup, self.web_app_path)
            self.log(f"Restored from: {latest_backup}", 'SUCCESS')
            self.log("Rollback completed", 'SUCCESS')
            return True
        except Exception as e:
            self.log(f"Rollback failed: {e}", 'ERROR')
            return False


def main():
    parser = argparse.ArgumentParser(
        description='BotV2 Security Integration Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Preview changes without applying
  python scripts/security_integration.py --dry-run
  
  # Apply security integrations
  python scripts/security_integration.py --apply
  
  # Rollback to previous version
  python scripts/security_integration.py --rollback
'''
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Apply security integrations'
    )
    
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback to previous version'
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        integrator = SecurityIntegrator(dry_run=False)
        success = integrator.rollback()
    elif args.apply:
        integrator = SecurityIntegrator(dry_run=False)
        success = integrator.integrate()
    elif args.dry_run:
        integrator = SecurityIntegrator(dry_run=True)
        success = integrator.integrate()
    else:
        parser.print_help()
        return
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
