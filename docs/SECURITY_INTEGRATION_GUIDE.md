# BotV2 Security Integration Guide

**Version**: 1.0.0  
**Date**: January 25, 2026  
**Purpose**: Complete Phase 1 security integration into web_app.py

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Automatic Integration](#automatic-integration)
4. [Manual Integration](#manual-integration)
5. [Testing & Validation](#testing--validation)
6. [Rollback Procedure](#rollback-procedure)
7. [Troubleshooting](#troubleshooting)

---

## Overview

This guide completes the remaining **15% of Phase 1 security** by integrating:

- ✅ Flask-WTF CSRF protection
- ✅ XSS sanitization middleware
- ✅ Pydantic input validators
- ✅ Session persistence (optional)

**Current Status**: 85% complete  
**After Integration**: 100% complete

---

## Prerequisites

### 1. Dependencies Installed

```bash
# Verify security packages are installed
pip list | grep -E "Flask-WTF|bleach|pydantic"

# Should show:
# Flask-WTF        1.2.1
# bleach           6.1.0
# pydantic         2.5.3
```

If missing:
```bash
pip install Flask-WTF==1.2.1 bleach==6.1.0 pydantic==2.5.3
```

### 2. Files Exist

```bash
# Check security modules
ls src/security/
# Should contain:
# - csrf_protection.py
# - xss_protection.py
# - input_validator.py (NEW)
# - xss_middleware.py (NEW)
# - security_middleware.py
# - session_manager.py

# Check integration script
ls scripts/security_integration.py
```

### 3. Backup Current State

```bash
# Manual backup
cp src/dashboard/web_app.py src/dashboard/web_app.py.backup_$(date +%Y%m%d_%H%M%S)
```

---

## Automatic Integration

### Step 1: Dry Run (Preview Changes)

```bash
python scripts/security_integration.py --dry-run
```

**Expected Output**:
```
ℹ️ [2026-01-25 03:00:00] Starting BotV2 Security Integration
ℹ️ [2026-01-25 03:00:00] Mode: DRY RUN (no changes)
⏭️ [2026-01-25 03:00:00] [DRY RUN] Would create backup
✅ [2026-01-25 03:00:01] Added CSRF import
✅ [2026-01-25 03:00:01] Added XSS import
✅ [2026-01-25 03:00:01] Added CSRF initialization
✅ [2026-01-25 03:00:01] Added XSS middleware
ℹ️ [2026-01-25 03:00:01] Pydantic validation can be added to login endpoint
⏭️ [2026-01-25 03:00:01] [DRY RUN] Would write changes to web_app.py
✅ [2026-01-25 03:00:01] DRY RUN completed - no files were modified
```

### Step 2: Apply Changes

```bash
python scripts/security_integration.py --apply
```

**Expected Output**:
```
ℹ️ [2026-01-25 03:00:05] Starting BotV2 Security Integration
ℹ️ [2026-01-25 03:00:05] Mode: APPLY CHANGES
✅ [2026-01-25 03:00:05] Backup created: backups/web_app.py.20260125_030005
✅ [2026-01-25 03:00:06] Added CSRF import
✅ [2026-01-25 03:00:06] Added XSS import
✅ [2026-01-25 03:00:06] Added CSRF initialization
✅ [2026-01-25 03:00:06] Added XSS middleware
✅ [2026-01-25 03:00:06] Changes written to web_app.py
✅ [2026-01-25 03:00:06] Integration completed successfully
```

### Step 3: Restart Dashboard

```bash
docker compose restart botv2-dashboard

# Or if running locally
pkill -f "python.*web_app.py"
python src/dashboard/web_app.py
```

### Step 4: Verify Integration

```bash
# Check logs for security initialization
docker compose logs botv2-dashboard | grep -E "✅.*CSRF|✅.*XSS"

# Expected output:
# ✅ CSRF protection enabled
# ✅ XSS Protection Middleware enabled
```

---

## Manual Integration

If you prefer manual integration or the script fails:

### 1. Add Imports to web_app.py

**Location**: After Flask imports (around line 15)

```python
# Existing imports
from flask import Flask, render_template, jsonify, request, Response

# ➕ ADD THESE SECURITY IMPORTS
from src.security.csrf_protection import init_csrf
from src.security.xss_protection import sanitize_html, sanitize_dict
from src.security.xss_middleware import XSSProtectionMiddleware
from src.security.input_validator import (
    validate_login_request,
    validate_annotation_request,
    validate_market_data_request
)
```

### 2. Initialize CSRF in __init__ Method

**Location**: `ProfessionalDashboard.__init__()` after compression setup

```python
class ProfessionalDashboard:
    def __init__(self, config):
        # ... existing code ...
        
        self._setup_compression()
        
        # ➕ ADD CSRF INITIALIZATION
        try:
            self.csrf = init_csrf(self.app)
            logger.info("✅ CSRF protection enabled")
        except Exception as e:
            logger.warning(f"⚠️ CSRF initialization failed: {e}")
        
        # ➕ ADD XSS MIDDLEWARE
        self.xss_middleware = XSSProtectionMiddleware(self.app)
        
        # ... rest of __init__ ...
```

### 3. Add Input Validation to Login Endpoint

**Location**: `/login` POST handler

**BEFORE**:
```python
@self.app.route('/login', methods=['GET', 'POST'])
@self.limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # ...
```

**AFTER**:
```python
@self.app.route('/login', methods=['GET', 'POST'])
@self.limiter.limit("10 per minute")
def login():
    if request.method == 'POST':
        # ➕ ADD VALIDATION
        try:
            validated = validate_login_request(request.form)
            username = validated['username']
            password = validated['password']
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # ... rest of login logic ...
```

### 4. Add Validation to Annotation Endpoint

**Location**: `/api/annotations` POST handler

**BEFORE**:
```python
@self.app.route('/api/annotations', methods=['POST'])
def create_annotation():
    data = request.get_json()
    # ...
```

**AFTER**:
```python
@self.app.route('/api/annotations', methods=['POST'])
def create_annotation():
    # ➕ ADD VALIDATION
    try:
        validated = validate_annotation_request(request.get_json())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    # Use validated data
    annotation = {
        'chart_id': validated['chart_id'],
        'type': validated['type'],
        # ...
    }
```

### 5. Add Validation to Market Endpoints

**Location**: `/api/market/<symbol>/ohlcv`

```python
@self.app.route('/api/market/<symbol>/ohlcv')
def get_ohlcv_data(symbol):
    timeframe = request.args.get('timeframe', '1h')
    limit = int(request.args.get('limit', 100))
    
    # ➕ ADD VALIDATION
    try:
        validated = validate_market_data_request(symbol, timeframe, limit)
        symbol = validated['symbol']
        timeframe = validated['timeframe']
        limit = validated['limit']
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    # ... rest of logic ...
```

---

## Testing & Validation

### 1. CSRF Protection Test

```bash
# Test: Submit login without CSRF token (should fail)
curl -X POST http://localhost:8050/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=test"

# Expected: 403 Forbidden
# {"error": "CSRF validation failed"}
```

### 2. XSS Protection Test

```bash
# Test: Inject malicious script in annotation
curl -X POST http://localhost:8050/api/annotations \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your_session>" \
  -d '{
    "chart_id": "test",
    "type": "note",
    "x": 0,
    "y": 0,
    "text": "<script>alert('XSS')</script>"
  }'

# Expected: 400 Bad Request
# {"error": "Text contains potentially dangerous content"}
```

### 3. Input Validation Test

```bash
# Test: Invalid username format
curl -X POST http://localhost:8050/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@<script>&password=test"

# Expected: 400 Bad Request
# {"error": "Username can only contain letters, numbers, underscore, and hyphen"}
```

### 4. Functional Test

```bash
# Test: Valid login (should work)
curl -X POST http://localhost:8050/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -c cookies.txt \
  -d "username=admin&password=<your_password>&csrf_token=<token_from_page>"

# Expected: 200 OK
# {"success": true, "redirect": "/"}
```

### 5. Security Logs Verification

```bash
# Check security audit log
tail -f logs/security_audit.log

# Should see entries like:
# {"timestamp": "2026-01-25T03:00:00Z", "event_type": "auth.login.success", ...}
# {"timestamp": "2026-01-25T03:01:00Z", "event_type": "security.csrf.validated", ...}
```

---

## Rollback Procedure

### Option 1: Using Script

```bash
python scripts/security_integration.py --rollback
```

### Option 2: Manual Rollback

```bash
# Find latest backup
ls -lt backups/web_app.py.* | head -1

# Restore it
cp backups/web_app.py.20260125_030005 src/dashboard/web_app.py

# Restart dashboard
docker compose restart botv2-dashboard
```

### Option 3: Git Rollback

```bash
# If changes were committed
git log --oneline src/dashboard/web_app.py

# Revert to previous commit
git checkout <commit_hash> src/dashboard/web_app.py

# Commit revert
git commit -m "Revert security integration"
```

---

## Troubleshooting

### Issue: CSRF Token Not Found

**Symptom**: Login fails with "CSRF token not found"

**Solution**:
```python
# Check if csrf_token() is available in templates
# In login.html, verify:
<meta name="csrf-token" content="{{ csrf_token() }}">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

# If not working, check Flask-WTF initialization:
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

### Issue: XSS Middleware Not Sanitizing

**Symptom**: Malicious input still passes through

**Solution**:
```bash
# Check middleware is initialized
docker compose logs botv2-dashboard | grep "XSS Protection Middleware"

# Should see: ✅ XSS Protection Middleware enabled

# If not, manually add:
from src.security.xss_middleware import XSSProtectionMiddleware
XSSProtectionMiddleware(app)
```

### Issue: Pydantic Validation Errors

**Symptom**: All requests return 400 errors

**Solution**:
```python
# Add better error handling
try:
    validated = validate_login_request(request.form)
except ValueError as e:
    logger.warning(f"Validation failed: {e}")
    return jsonify({'error': 'Invalid input'}), 400
```

### Issue: Performance Degradation

**Symptom**: Slow response times after integration

**Solution**:
```python
# Disable XSS sanitization for specific endpoints
from src.security.xss_middleware import XSSProtectionMiddleware

middleware = XSSProtectionMiddleware(
    app,
    excluded_paths=['/health', '/metrics', '/api/market/*']
)
```

---

## Verification Checklist

After integration, verify:

- [ ] Dashboard starts without errors
- [ ] Login works with valid credentials
- [ ] Login fails with invalid credentials
- [ ] CSRF protection active (form submission works)
- [ ] XSS sanitization active (malicious input rejected)
- [ ] Input validation active (invalid formats rejected)
- [ ] Security logs capturing events
- [ ] Rate limiting still working
- [ ] WebSocket connections stable
- [ ] No performance degradation (< 20ms overhead)

---

## Next Steps

After successful integration:

1. **Monitor logs** for 24 hours
2. **Test all features** thoroughly
3. **Update documentation** with any custom changes
4. **Plan Phase 2** (MFA, OAuth, advanced monitoring)

---

## Support

If you encounter issues:

1. Check logs: `docker compose logs -f botv2-dashboard`
2. Review this guide's troubleshooting section
3. Consult `docs/SECURITY_PHASE1.md` for feature details
4. Rollback if necessary

---

**End of Guide**
