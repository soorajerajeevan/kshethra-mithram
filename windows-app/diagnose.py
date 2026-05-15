#!/usr/bin/env python3
"""Diagnostic script to verify the environment is set up correctly."""

import sys
import os

print("=" * 70)
print("KSHETHRA-MITHRAM LAUNCHER DIAGNOSTIC")
print("=" * 70)
print()

# Get the base directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Project root: {base_dir}")
print(f"Current directory: {os.getcwd()}")
print()

# Check if app folder exists
app_dir = os.path.join(base_dir, 'app')
print(f"App directory exists: {os.path.isdir(app_dir)}")
print(f"App __init__.py exists: {os.path.isfile(os.path.join(app_dir, '__init__.py'))}")
print()

# Add base to path
sys.path.insert(0, base_dir)
os.chdir(base_dir)

# Try to import dependencies
print("Checking required packages...")
print("-" * 70)

packages = [
    'flask',
    'flask_sqlalchemy',
    'flask_migrate',
    'flask_login',
    'flask_babel',
    'flask_wtf',
    'bcrypt',
    'email_validator',
    'weasyprint',
]

all_ok = True
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✓ {pkg}")
    except ImportError as e:
        print(f"✗ {pkg}: {e}")
        all_ok = False

print()
print("-" * 70)

if not all_ok:
    print("ERROR: Some required packages are missing!")
    print()
    print("Fix by running:")
    print(f"  pip install -r {os.path.join(base_dir, 'requirements.txt')}")
    print()
    sys.exit(1)

# Try to import the app module
print("Attempting to import app module...")
print("-" * 70)
try:
    from app import create_app
    print("✓ Successfully imported create_app from app")
    print(f"  create_app location: {create_app.__module__}")
    print()
    print("✓ ENVIRONMENT OK - You can run the launcher")
except ImportError as e:
    print(f"✗ Failed to import app: {e}")
    print()
    print("Debugging info:")
    print(f"  sys.path[0]: {sys.path[0]}")
    print(f"  Files in app/: {os.listdir(app_dir) if os.path.isdir(app_dir) else 'N/A'}")
    sys.exit(1)

print()
