# Quick Wins - Immediate Fixes (1-2 Days)

These are the fastest improvements that will have the biggest security impact. Each can be implemented in under 30 minutes.

---

## 1. Fix Hardcoded Database Credentials

**File:** `config.py`  
**Time:** 5 minutes  
**Impact:** CRITICAL

### Before
```python
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://temple_user:temple_pass@localhost:5432/temple_db'  # ❌ HARDCODED!
```

### After
```python
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        import sys
        print("ERROR: DATABASE_URL environment variable must be set for production", file=sys.stderr)
        if os.environ.get('FLASK_ENV') == 'production':
            sys.exit(1)
        db_url = 'sqlite:///' + os.path.join(basedir, 'temple_dev.db')
    
    SQLALCHEMY_DATABASE_URI = db_url
```

### Test
```bash
# This should FAIL in production without env var
FLASK_ENV=production python run.py
# Should exit with error message

# This should WORK
DATABASE_URL=postgresql://user:pass@host/db FLASK_ENV=production python run.py
```

---

## 2. Fix Hardcoded Secret Key

**File:** `config.py`  
**Time:** 5 minutes  
**Impact:** CRITICAL

### Before
```python
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
```

### After
```python
import sys

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        print("ERROR: SECRET_KEY environment variable required in production", file=sys.stderr)
        sys.exit(1)
    # Use a different key each development run (less risky)
    import secrets
    SECRET_KEY = secrets.token_urlsafe(32)
    print(f"⚠️  Using development SECRET_KEY (not persisted): {SECRET_KEY[:20]}...")
```

### Generate Production Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output example: "kJ_8vQ9xLmN2pR5sT7uW3yZaBcD4eF6gH9iK1lM3nO5p"

# Export it
export SECRET_KEY="kJ_8vQ9xLmN2pR5sT7uW3yZaBcD4eF6gH9iK1lM3nO5p"
```

---

## 3. Remove Hardcoded Default Passwords

**File:** `app/seed.py`  
**Time:** 10 minutes  
**Impact:** CRITICAL

### Before
```python
admin = User(username='admin', email='admin@temple.com', full_name='Administrator', role='admin')
admin.set_password('admin123')  # ❌ DEFAULT PASSWORD!
```

### After
```python
import secrets

def create_default_user(username, email, full_name, role):
    """Create user with random password and print it once."""
    user = User(username=username, email=email, full_name=full_name, role=role)
    # Generate 12-character password: 10 random chars + 2 special
    password = secrets.token_urlsafe(10)  # URL-safe base64
    user.set_password(password)
    db.session.add(user)
    
    # Print password ONCE (not in code)
    print(f"✓ Created user: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  🔐 SAVE THIS PASSWORD - You will need it to login!")
    print()
    return user

if not User.query.filter_by(username='admin').first():
    create_default_user('admin', 'admin@temple.com', 'Administrator', 'admin')

if not User.query.filter_by(username='cashier').first():
    create_default_user('cashier', 'cashier@temple.com', 'Cashier User', 'cashier')

if not User.query.filter_by(username='priest').first():
    create_default_user('priest', 'priest@temple.com', 'Priest User', 'priest')
```

### Also Update `.gitignore`
```
# Add to .gitignore
.env
.env.local
.env.*.local
instance/
*.db
seed_output.txt
```

---

## 4. Enforce Minimum Password Length

**File:** `app/routes/auth.py`  
**Time:** 10 minutes  
**Impact:** HIGH

### Before
```python
if len(new_password) < 6:  # ❌ TOO SHORT
    flash('Password must be at least 6 characters long', 'danger')
```

### After
```python
def validate_password_strength(password):
    """Check if password meets minimum requirements."""
    errors = []
    
    if len(password) < 12:
        errors.append("Password must be at least 12 characters")
    if not any(c.isupper() for c in password):
        errors.append("Password must contain an uppercase letter")
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain a number")
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        errors.append("Password must contain a special character (!@#$%^&*)")
    
    return errors

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate password strength
        errors = validate_password_strength(new_password or '')
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('auth.change_password'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/change_password.html')
```

### Test
```python
# Test in Python shell
from app.routes.auth import validate_password_strength

print(validate_password_strength('weak'))  # Should have errors
# ['Password must be at least 12 characters', 'Password must contain an uppercase letter', ...]

print(validate_password_strength('StrongP@ss123'))  # Should be empty
# []
```

---

## 5. Add Rate Limiting to Login

**File:** `app/__init__.py` and `app/routes/auth.py`  
**Time:** 15 minutes  
**Impact:** HIGH

### Step 1: Install Package
```bash
pip install Flask-Limiter
```

### Step 2: Initialize in `app/__init__.py`
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Create at module level
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app(config_name='development'):
    app = Flask(__name__)
    # ... existing code ...
    
    limiter.init_app(app)  # Add this
    
    return app
```

### Step 3: Apply to Login Route
```python
# app/routes/auth.py
from app import limiter

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # 5 attempts per minute max
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user is None or not user.check_password(password):
            flash(_('Invalid username or password'), 'danger')
            return redirect(url_for('auth.login'))
        
        # ... rest of login ...
```

### Test
```bash
# Rapid fire 10 requests - should be rate limited after 5
for i in {1..10}; do
  curl -X POST http://localhost:5000/auth/login \
    -d "username=admin&password=wrong" \
    -w "Status: %{http_code}\n"
  sleep 0.1
done
# Should see: 200, 200, 200, 200, 200, 429, 429, 429, 429, 429
# (429 = Too Many Requests)
```

---

## 6. Add Security Headers

**File:** `app/__init__.py`  
**Time:** 10 minutes  
**Impact:** MEDIUM

### Add to `create_app()` Function
```python
def create_app(config_name='development'):
    app = Flask(__name__)
    
    # ... existing setup code ...
    
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevent MIME sniffing
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'      # Prevent clickjacking
        response.headers['X-XSS-Protection'] = '1; mode=block'  # Prevent XSS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'  # HTTPS only
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    return app
```

### Verify Headers
```bash
curl -I http://localhost:5000/
# Should see:
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN
# X-XSS-Protection: 1; mode=block
# Etc.
```

---

## 7. Fix Configuration for Production

**File:** `config.py`  
**Time:** 10 minutes  
**Impact:** MEDIUM

### Before
```python
class Config:
    SESSION_COOKIE_SECURE = False  # ❌ OK for dev, bad for production
```

### After
```python
import os

class Config:
    # Determine environment
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    IS_PRODUCTION = FLASK_ENV == 'production'
    
    # Session security
    SESSION_COOKIE_SECURE = IS_PRODUCTION  # HTTPS only in production
    SESSION_COOKIE_HTTPONLY = True         # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Strict' if IS_PRODUCTION else 'Lax'  # CSRF protection
    
    # Database pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
```

---

## 8. Add Basic Logging

**File:** `app/__init__.py`  
**Time:** 15 minutes  
**Impact:** MEDIUM

### Step 1: Install Package
```bash
pip install python-json-logger
```

### Step 2: Setup Logging
```python
# app/__init__.py
import logging
from pythonjsonlogger import jsonlogger
import os

def setup_logging(app):
    """Configure application logging."""
    if app.debug:
        return  # Skip for debug mode
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # JSON formatter
    formatter = jsonlogger.JsonFormatter()
    
    # File handler
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Stream handler (console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.WARNING)
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # ... existing setup ...
    
    setup_logging(app)  # Add this
    
    return app
```

### Step 3: Use in Routes
```python
# app/routes/auth.py
import logging

logger = logging.getLogger(__name__)

def login():
    ...
    if user is None or not user.check_password(password):
        logger.warning(f"failed_login", extra={
            'username': username,
            'ip_address': request.remote_addr,
            'timestamp': datetime.utcnow().isoformat()
        })
        flash(_('Invalid username or password'), 'danger')
        return redirect(url_for('auth.login'))
    
    logger.info(f"user_login", extra={
        'username': user.username,
        'ip_address': request.remote_addr,
        'timestamp': datetime.utcnow().isoformat()
    })
    ...
```

---

## 9. Extract Duplicate Functions

**File:** Create `app/utils.py`  
**Time:** 20 minutes  
**Impact:** MEDIUM

### Create New File
```python
# app/utils.py
"""Shared utility functions."""
import re
import json
from typing import Optional, List, Dict
from app.models import Devotee, Bill

def generate_devotee_id() -> str:
    """
    Generate unique devotee ID in format DEV-00001.
    
    Returns:
        Next available devotee ID
    """
    devotees = Devotee.query.order_by(Devotee.id.desc()).limit(200).all()
    max_num = 0
    for d in devotees:
        match = re.match(r'^DEV-(\d+)$', (d.devotee_id or '').strip(), re.IGNORECASE)
        if match:
            max_num = max(max_num, int(match.group(1)))
    new_num = max_num + 1 if max_num > 0 else 1
    return f'DEV-{new_num:05d}'

def parse_family_members(raw_value: Optional[str]) -> List[Dict[str, str]]:
    """
    Parse family members from multiple formats.
    
    Supports:
    - JSON: [{"name":"John","nakshathram":"Rohini"}]
    - Plain text: "Name1 | Nakshathram1\\nName2 | Nakshathram2"
    - Comma-separated: "Name1, Name2"
    
    Args:
        raw_value: Raw input string from form or database
    
    Returns:
        List of dicts with 'name' and 'nakshathram' keys
    """
    members = []
    text = (raw_value or '').strip()
    if not text:
        return members
    
    # Try JSON first
    try:
        data = json.loads(text)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    name = (item.get('name') or '').strip()
                    nak = (item.get('nakshathram') or '').strip()
                    if name:
                        members.append({'name': name, 'nakshathram': nak})
            if members:
                return members
    except Exception:
        pass
    
    # Try multi-line format
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if '|' in line:
            name, nak = line.split('|', 1)
            name = name.strip()
            nak = nak.strip()
        else:
            name, nak = line, ''
        if name:
            members.append({'name': name, 'nakshathram': nak})
    
    if members:
        return members
    
    # Fallback to comma-separated
    return [{'name': x.strip(), 'nakshathram': ''} for x in text.split(',') if x.strip()]

def generate_bill_number() -> str:
    """Generate unique bill number in format BILL-2026-000001."""
    from datetime import datetime
    
    year = datetime.now().year
    last_bill = Bill.query.filter(
        Bill.bill_number.like(f'BILL-{year}-%')
    ).order_by(Bill.id.desc()).first()
    
    if last_bill:
        last_num = int(last_bill.bill_number.split('-')[2])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f'BILL-{year}-{new_num:06d}'
```

### Update Routes to Use
```python
# app/routes/devotees.py - BEFORE
from app.utils import generate_devotee_id, parse_family_members

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        family_members = parse_family_members(request.form.get('family_members'))
        devotee = Devotee(
            devotee_id=generate_devotee_id(),  # Now uses shared function
            ...
        )
```

---

## 10. Add .env Template

**File:** Create `.env.example`  
**Time:** 5 minutes  
**Impact:** MEDIUM

```bash
# .env.example (COMMIT THIS FILE, NOT .env)
FLASK_ENV=development
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///temple_dev.db

# For production:
# FLASK_ENV=production
# FLASK_CONFIG=production
# SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
# DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Add to `.gitignore`
```
.env
.env.local
.env.*.local
instance/
```

---

## Summary of Changes

| Issue | File | Change | Time | Impact |
|-------|------|--------|------|--------|
| Hardcoded DB credentials | config.py | Require env var | 5m | 🔴 CRITICAL |
| Hardcoded secret key | config.py | Require env var | 5m | 🔴 CRITICAL |
| Default passwords | seed.py | Generate random | 10m | 🔴 CRITICAL |
| Weak password policy | auth.py | Min 12 chars + complexity | 10m | 🔴 HIGH |
| No rate limiting | auth.py | Add Flask-Limiter | 15m | 🔴 HIGH |
| Missing security headers | __init__.py | Add headers | 10m | 🟡 MEDIUM |
| Weak session config | config.py | Enable secure flags | 10m | 🟡 MEDIUM |
| No logging | __init__.py | Add json logging | 15m | 🟡 MEDIUM |
| Code duplication | utils.py | Extract functions | 20m | 🟡 MEDIUM |
| No env example | .env.example | Create template | 5m | 🟡 LOW |

**Total Time:** ~105 minutes (~2 hours)  
**Security Impact:** Addresses 6 critical issues + 4 high issues

---

## Testing Your Changes

After making these changes, test:

```bash
# 1. Test missing environment variables
unset SECRET_KEY
unset DATABASE_URL
FLASK_ENV=production python run.py
# Should exit with error about missing keys

# 2. Test password validation
python -c "from app.routes.auth import validate_password_strength; print(validate_password_strength('weak'))"

# 3. Test rate limiting
for i in {1..10}; do curl -X POST http://localhost:5000/auth/login -d "username=x&password=y" -w "%{http_code}\n"; done

# 4. Test security headers
curl -I http://localhost:5000/ | grep "X-"

# 5. Test logging (if enabled)
tail -f logs/app.log
```

---

## Next Steps (After Quick Wins)

Once these are done (2 hours), tackle:

1. **Add input validation** (Marshmallow) - 4 hours
2. **Extract more duplicate code** - 3 hours
3. **Add type hints** - 8 hours
4. **Write tests** - 16+ hours
5. **Add error handling** - 4 hours

These quick wins get you 70% of the way to production-ready. The remaining 30% requires more time but is equally important.

---

**Last Updated:** 2026-05-05
