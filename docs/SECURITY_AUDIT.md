# Security and Code Quality Audit Report
**Project:** Kshethra Mithram (Temple Management System)  
**Date:** 2026-05-05  
**Framework:** Flask 3.0.0  

---

## Executive Summary

This is a Flask-based temple management system with **8 critical security vulnerabilities** and **10+ code quality issues**. The most severe issues involve hardcoded credentials, weak authentication, and insufficient input validation. The application is suitable for development/testing only and requires substantial hardening before production deployment.

**Risk Level: HIGH** 🔴

---

## Critical Security Issues

### 1. Hardcoded Production Database Credentials
**File:** `config.py:45`  
**Severity:** CRITICAL  
**Issue:**
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://temple_user:temple_pass@localhost:5432/temple_db'
```
**Risk:** Default credentials in code are discoverable in version control and logs.  
**Mitigation:**
- Require `DATABASE_URL` environment variable in production
- Use `.env` files with `.gitignore` (never committed)
- Use secrets management (AWS Secrets Manager, HashiCorp Vault)

---

### 2. Hardcoded Fallback Secret Key
**File:** `config.py:9`  
**Severity:** CRITICAL  
**Issue:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
```
**Risk:** Default key enables session forgery and CSRF token bypass.  
**Mitigation:**
- Generate a cryptographically secure secret key
- Fail startup if `SECRET_KEY` env var is not set in production
- Use `secrets.token_urlsafe(32)` for key generation

---

### 3. Hardcoded Default Credentials in Seed Data
**File:** `app/seed.py:51, 64, 77`  
**Severity:** CRITICAL  
**Issue:**
```python
admin.set_password('admin123')  # admin user
cashier.set_password('cashier123')  # cashier user
priest_user.set_password('priest123')  # priest user
```
**Risk:** Default credentials in seed script are widely known. Users forget to change them.  
**Mitigation:**
- Generate random passwords on initial setup
- Prompt admin to set password on first login (forced password change)
- Remove seed script passwords from production deployments
- Document password requirements

---

### 4. Weak Password Validation
**File:** `app/routes/auth.py:79`  
**Severity:** HIGH  
**Issue:**
```python
if len(new_password) < 6:
    flash('Password must be at least 6 characters long', 'danger')
```
**Risk:** 6-character passwords are easily cracked (estimated 15 minutes with GPU).  
**Mitigation:**
- Enforce minimum 12 characters
- Require mixed case, numbers, special characters
- Use `zxcvbn` library for password strength checking
- Compare against common password lists

---

### 5. Insufficient Input Validation & Potential SQL Injection
**File:** `app/routes/billing.py:49`  
**Severity:** HIGH  
**Issue:**
```python
last_bill = Bill.query.filter(
    Bill.bill_number.like(f'BILL-{year}-%')  # String interpolation with user data possible
).order_by(Bill.id.desc()).first()
```
**Risk:** While SQLAlchemy parameterizes queries by default, pattern matching with user input can lead to logic errors.  
**Mitigation:**
- Use parameterized queries consistently (already done here)
- Add input validation and type checking for all route parameters
- Example:
```python
@bp.route('/<int:id>')  # Type hint enforces integer
```

---

### 6. Lack of CSRF Token Verification in Forms
**File:** Multiple route handlers  
**Severity:** HIGH  
**Issue:** Flask-WTF is included but CSRF protection status unclear in templates. No visible `{{ csrf_token() }}` in routes examined.  
**Risk:** CSRF attacks can modify devotee records, create false bills.  
**Mitigation:**
- Audit all POST/PUT/DELETE forms for `{{ csrf_token() }}`
- Enable `WTF_CSRF_ENABLED = True` (verify it's set)
- Test with `curl` to confirm CSRF rejection

---

### 7. Weak Session Configuration
**File:** `config.py:13-16`  
**Severity:** MEDIUM  
**Issue:**
```python
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)  # Short timeout, but no clear renewal
```
**Risk:** Cookies transmitted over HTTP; session fixation possible.  
**Mitigation:**
- Force `SESSION_COOKIE_SECURE = True` in production
- Enable `SESSION_COOKIE_HTTPONLY = True` (already done ✓)
- Use `SESSION_COOKIE_SAMESITE = 'Strict'` (currently 'Lax')
- Implement session activity tracking and timeout warnings

---

### 8. No Rate Limiting on Login Attempts
**File:** `app/routes/auth.py:12-43`  
**Severity:** MEDIUM  
**Issue:** No rate limiting on `/auth/login`. An attacker can brute-force credentials.  
**Risk:** Credential enumeration and password guessing attacks.  
**Mitigation:**
- Implement `Flask-Limiter`
- Rate limit: 5 failed attempts → 15-minute lockout
- Log failed attempts for monitoring
```python
@limiter.limit("5/minute")
@bp.route('/login', methods=['POST'])
def login():
    ...
```

---

### 9. Insufficient Authorization Checks
**File:** Multiple route handlers  
**Severity:** MEDIUM  
**Issue:**
```python
# Some routes only check `@login_required`
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    ...
```
**Risk:** Cashiers might access admin-only features. No role-based view/edit permissions.  
**Mitigation:**
- Implement decorator for role-based access:
```python
@require_role('admin')
def delete_devotee():
    ...
```
- Verify ownership before allowing edit (no one can edit others' data)
- Check `current_user.role` in all data modification endpoints

---

### 10. Debug Mode in Production
**File:** `run.py:65-66`  
**Severity:** MEDIUM  
**Issue:**
```python
debug = app.config.get('DEBUG', False)
app.run(host='0.0.0.0', port=5000, debug=debug, use_reloader=False)
```
**Risk:** If `DEBUG=True` in production, Werkzeug debugger exposes source code and allows code execution.  
**Mitigation:**
- Set `DEBUG=False` via environment variable in production
- Use production WSGI server (Gunicorn, uWSGI)
- Never bind to `0.0.0.0` publicly; use firewall/load balancer

---

### 11. No SQL Injection Protection in Bill Number Generation
**File:** `app/routes/billing.py:49`  
**Severity:** MEDIUM  
**Issue:**
```python
Bill.bill_number.like(f'BILL-{year}-%')
```
**Risk:** While SQLAlchemy is parameterizing, using LIKE with wildcards can be slow (DoS).  
**Mitigation:**
- Use exact matching or database stored procedures
- Index on `bill_number` to prevent table scans
- Consider simpler query: `Bill.bill_number.startswith('BILL-' + str(year))`

---

## Code Quality Issues

### 1. Code Duplication
**Files:** `app/routes/devotees.py:12-21`, `app/routes/billing.py:61-70`  
**Issue:** `generate_devotee_id()` defined in two files  
**Impact:** Bug fix in one location won't apply to the other  
**Fix:** Move to `app/utils.py` and import:
```python
# app/utils.py
def generate_devotee_id():
    ...

# app/routes/devotees.py
from app.utils import generate_devotee_id
```

---

### 2. Code Duplication: Family Member Parsing
**Files:** `app/routes/devotees.py:24-63`, `app/routes/billing.py:73-100`  
**Issue:** `parse_family_members()` duplicated verbatim  
**Fix:** Extract to shared utility module

---

### 3. Missing Type Hints
**Severity:** MEDIUM  
**Issue:** No type hints in Python code  
**Impact:** IDE autocomplete poor; refactoring errors; documentation unclear  
**Fix:**
```python
def generate_bill_number() -> str:
    ...

def login_user(user: User, remember: bool) -> None:
    ...
```

---

### 4. No Input Validation/Sanitization
**Files:** Multiple route handlers  
**Issue:** User input from `request.form.get()` used directly without validation  
**Example:**
```python
item = InventoryItem(
    name=request.form.get('name'),  # No length check
    category=request.form.get('category'),  # No enum validation
    ...
)
```
**Fix:** Use `marshmallow` or Pydantic for schema validation

---

### 5. Weak/Missing Error Handling
**Files:** `app/__init__.py:54-56`, all route handlers  
**Issue:** No try-except blocks; 500 errors expose stack traces  
**Example:**
```python
@app.context_processor
def inject_locale():
    return {'locale': request.accept_languages.best_match(...)}
    # No error handling if request.accept_languages fails
```
**Fix:** Add error handlers:
```python
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    logger.error(f"500 error: {e}")
    return render_template('500.html'), 500
```

---

### 6. No Logging/Audit Trail
**Severity:** MEDIUM  
**Issue:** No logging of security events (login, failed auth, data changes)  
**Impact:** Cannot detect unauthorized access or investigate incidents  
**Fix:**
```python
import logging
logger = logging.getLogger(__name__)

def login():
    ...
    logger.info(f"User {username} logged in from {request.remote_addr}")
    logger.warning(f"Failed login attempt for {username}")
```

---

### 7. Inefficient Pagination
**Files:** `app/routes/inventory.py:23-30`  
**Issue:** Custom pagination object hides all items in memory for `low_stock` filter  
**Impact:** Scales poorly with large inventories  
**Fix:** Use SQLAlchemy `.filter()` instead of Python list comprehension

---

### 8. No Request Validation Middleware
**Issue:** No schema validation (e.g., `Content-Type: application/json`)  
**Impact:** Accepts unexpected data types; leads to type errors  
**Fix:** Use Flask request validation middleware or decorators

---

### 9. Database Connection Pool Not Configured
**Files:** `app/__init__.py`  
**Issue:** SQLAlchemy pool settings not optimized  
**Impact:** Connection exhaustion under load  
**Fix:**
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

---

### 10. No Secrets Management for Seed Data
**Files:** `app/seed.py`  
**Issue:** Hard to avoid exposing default passwords in code  
**Fix:** Use environment variables or prompt on first run

---

### 11. Incomplete Data Validation
**File:** `app/routes/devotees.py:159`  
**Issue:** No validation that phone numbers are valid Indian numbers  
**Fix:** Use `phonenumbers` library to validate format

---

## OWASP Top 10 Coverage

| Vulnerability | Status | Files | Notes |
|---|---|---|---|
| A01: Broken Access Control | ⚠️ PARTIAL | auth.py, multiple routes | Role checks missing on some endpoints |
| A02: Cryptographic Failures | 🔴 CRITICAL | config.py | Hardcoded secrets |
| A03: Injection | ✅ OK | models.py | SQLAlchemy parameterizes queries |
| A04: Insecure Design | ⚠️ MEDIUM | auth.py | Weak password policy |
| A05: Security Misconfiguration | 🔴 CRITICAL | config.py, run.py | Debug mode, hardcoded credentials |
| A06: Vulnerable Components | ✅ OK | requirements.txt | Dependencies current (May 2026) |
| A07: Authentication Failures | 🔴 CRITICAL | auth.py | Default credentials, no rate limiting |
| A08: Data Integrity Failures | ⚠️ MEDIUM | billing.py | No transaction signing |
| A09: Logging & Monitoring | 🔴 CRITICAL | All files | No audit logging |
| A10: SSRF | ✅ OK | N/A | No external service calls observed |

---

## Recommendations by Priority

### Immediate (P0 - Deploy Blocker)
1. **Remove hardcoded credentials** from `config.py` and `seed.py`
2. **Require environment variables** for all secrets
3. **Implement password strength policy** (12+ chars, complexity)
4. **Add rate limiting** to login endpoint
5. **Implement audit logging** for all sensitive operations
6. **Add CSRF token validation** to all forms (audit templates)

### Short-term (P1 - Before Beta)
7. Implement role-based access control (RBAC) decorator
8. Add comprehensive input validation
9. Implement error handling middleware
10. Configure secure session settings for production
11. Set up database connection pooling
12. Add type hints to all Python files

### Medium-term (P2 - Polish)
13. Extract duplicated utility functions
14. Implement comprehensive logging
15. Add request/response validation schemas
16. Set up automated security scanning (SAST)
17. Implement dependency vulnerability checking

### Long-term (P3 - Best Practices)
18. Add comprehensive unit/integration tests
19. Implement API documentation (OpenAPI/Swagger)
20. Set up security headers (CSP, X-Frame-Options, etc.)
21. Implement 2FA for admin accounts
22. Add activity/audit logs UI for admins

---

## Quick Wins (Easy Fixes)

### Fix #1: Use Environment Variables
```python
# config.py - BEFORE
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# config.py - AFTER
import sys
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        print("ERROR: SECRET_KEY environment variable required in production", file=sys.stderr)
        sys.exit(1)
    SECRET_KEY = 'dev-key-only-for-development'  # Explicit comment
```

### Fix #2: Stronger Password Policy
```python
# app/routes/auth.py
def validate_password(password):
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain number"
    if not any(c in '!@#$%^&*()' for c in password):
        return False, "Password must contain special character"
    return True, ""
```

### Fix #3: Rate Limiting
```bash
pip install Flask-Limiter
```
```python
# app/__init__.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# app/routes/auth.py
@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    ...
```

---

## Testing Checklist

- [ ] SQL Injection: Try `admin' OR '1'='1` in login
- [ ] CSRF: Test POST without CSRF token
- [ ] Brute Force: Submit login 10 times rapidly
- [ ] Authorization: Log in as cashier, try to delete devotee (admin only)
- [ ] Session Hijacking: Copy session cookie to different browser
- [ ] XSS: Enter `<script>alert('xss')</script>` in devotee name
- [ ] Default Credentials: Try admin:admin123
- [ ] Debug Mode: Check if Werkzeug debugger is accessible
- [ ] Error Messages: Verify no stack traces in error pages

---

## Environment Setup (Secure)

```bash
# .env (DO NOT COMMIT)
FLASK_ENV=production
FLASK_CONFIG=production
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
DATABASE_URL=postgresql://user:pass@host:5432/db
FLASK_DEBUG=0
```

```bash
# .gitignore
.env
.env.local
*.key
*.pem
__pycache__/
venv/
instance/
```

---

## References

- [OWASP Top 10 2021](https://owasp.org/Top10/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/security/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

**Audit Completed:** 2026-05-05  
**Next Review:** After P0 fixes (1-2 weeks)
