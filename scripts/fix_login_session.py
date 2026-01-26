#!/usr/bin/env python3
"""🔧 Fix Login Session Management

This script patches src/dashboard/web_app.py to fix the login redirect issue.

The problem:
- Session cookie not being saved before JSON response
- Missing session_id tracking
- Missing last_activity timestamp

The fix:
- Add session.modified = True to force session save
- Store session_id from session_manager
- Add last_activity timestamp
- Return message in JSON response

Usage:
    python scripts/fix_login_session.py

Author: Juan Carlos Garcia Arriero
Date: 26 Enero 2026
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def apply_fix():
    """Apply the login session fix to web_app.py"""
    
    web_app_path = project_root / 'src' / 'dashboard' / 'web_app.py'
    
    if not web_app_path.exists():
        print(f"❌ Error: {web_app_path} not found")
        return False
    
    print(f"📝 Reading {web_app_path}...")
    with open(web_app_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Original code to find and replace
    SEARCH_TEXT = """                # Verify credentials
                if self.auth.check_credentials(username, password):
                    session.permanent = True
                    session['user'] = username
                    session['login_time'] = datetime.now().isoformat()
                    
                    # 🔒 Create session
                    if HAS_SECURITY and self.session_manager:
                        self.session_manager.create_session(username)
                    
                    self.auth.record_successful_login(ip, username)
                    
                    # 📊 Track user activity
                    if HAS_METRICS and self.metrics_monitor:
                        self.metrics_monitor.record_user_activity(username)
                    
                    return jsonify({'success': True, 'redirect': '/'}), 200"""
    
    REPLACE_WITH = """                # Verify credentials
                if self.auth.check_credentials(username, password):
                    # ✅ CRITICAL: Set session data FIRST
                    session.permanent = True
                    session['user'] = username
                    session['login_time'] = datetime.now().isoformat()
                    session['last_activity'] = datetime.now().isoformat()
                    
                    # 🔒 Create session with session_manager
                    if HAS_SECURITY and self.session_manager:
                        session_id = self.session_manager.create_session(username)
                        session['session_id'] = session_id
                    
                    self.auth.record_successful_login(ip, username)
                    
                    # 📊 Track user activity
                    if HAS_METRICS and self.metrics_monitor:
                        self.metrics_monitor.record_user_activity(username)
                    
                    # ✅ Force session save before response
                    session.modified = True
                    
                    # ✅ Return JSON with success
                    return jsonify({
                        'success': True, 
                        'redirect': '/',
                        'message': 'Login successful'
                    }), 200"""
    
    if SEARCH_TEXT not in content:
        print("⚠️ Warning: Could not find exact match for code to replace.")
        print("This might mean the fix is already applied or the file has changed.")
        
        # Check if already fixed
        if "session.modified = True" in content:
            print("✅ Good news: session.modified = True is already present!")
            print("✅ The fix appears to be already applied.")
            return True
        else:
            print("❌ The code structure might have changed.")
            print("Please review the file manually.")
            return False
    
    print("🔧 Applying fix...")
    new_content = content.replace(SEARCH_TEXT, REPLACE_WITH)
    
    # Backup original file
    backup_path = web_app_path.with_suffix('.py.bak')
    print(f"💾 Creating backup at {backup_path}...")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Write fixed content
    print(f"✏️ Writing fixed content to {web_app_path}...")
    with open(web_app_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("")
    print("=" * 80)
    print("✅ FIX APPLIED SUCCESSFULLY!")
    print("=" * 80)
    print("")
    print("Changes made:")
    print("  1. ✅ Added session['last_activity'] timestamp")
    print("  2. ✅ Store session_id from session_manager.create_session()")
    print("  3. ✅ Added session.modified = True (CRITICAL FIX)")
    print("  4. ✅ Added 'message' field to JSON response")
    print("")
    print(f"Original file backed up to: {backup_path}")
    print("")
    print("Next steps:")
    print("  1. Review the changes in web_app.py")
    print("  2. Restart your dashboard server")
    print("  3. Test login functionality")
    print("  4. Commit the changes to Git:")
    print("")
    print("     git add src/dashboard/web_app.py")
    print('     git commit -m "🔧 Fix login session management"')
    print("     git push origin main")
    print("")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    print("")
    print("=" * 80)
    print("  🔧 BotV2 Login Session Fix Script")
    print("=" * 80)
    print("")
    print("This script will fix the login redirect issue in web_app.py")
    print("")
    
    try:
        success = apply_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
