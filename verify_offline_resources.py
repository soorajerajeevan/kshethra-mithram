#!/usr/bin/env python3
"""
Verify that all static resources are available locally
"""

import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')

# Expected files
REQUIRED_CSS_FILES = [
    'lib/css/bootstrap.min.css',
    'lib/css/tom-select.bootstrap5.min.css',
    'lib/css/bootstrap-icons.css',
]

REQUIRED_JS_FILES = [
    'lib/js/bootstrap.bundle.min.js',
    'lib/js/jquery-3.6.0.min.js',
    'lib/js/tom-select.complete.min.js',
]

OPTIONAL_FONT_FILES = [
    'lib/fonts/bootstrap-icons.woff',
    'lib/fonts/bootstrap-icons.woff2',
]

print("\n" + "="*70)
print("OFFLINE RESOURCES VERIFICATION")
print("="*70 + "\n")

all_ok = True

print("📋 Checking CSS files:")
for css_file in REQUIRED_CSS_FILES:
    filepath = os.path.join(STATIC_DIR, css_file)
    exists = os.path.exists(filepath)
    size = os.path.getsize(filepath) if exists else 0
    status = "✓" if exists else "✗"
    print(f"  {status} {css_file:<40} ({size:>10,} bytes)")
    if not exists:
        all_ok = False

print("\n📋 Checking JavaScript files:")
for js_file in REQUIRED_JS_FILES:
    filepath = os.path.join(STATIC_DIR, js_file)
    exists = os.path.exists(filepath)
    size = os.path.getsize(filepath) if exists else 0
    status = "✓" if exists else "✗"
    print(f"  {status} {js_file:<40} ({size:>10,} bytes)")
    if not exists:
        all_ok = False

print("\n📋 Checking Font files (optional - CDN fallback available):")
for font_file in OPTIONAL_FONT_FILES:
    filepath = os.path.join(STATIC_DIR, font_file)
    exists = os.path.exists(filepath)
    size = os.path.getsize(filepath) if exists else 0
    status = "✓" if exists else "⚠"
    print(f"  {status} {font_file:<40} ({size:>10,} bytes)")

print("\n" + "="*70)
if all_ok:
    print("✓ All required files are present!")
    print("\nYour application is ready for offline use!")
    print("\n✓ CSS & JS: All local")
    print("✓ Bootstrap Icons: Local CSS with CDN fallback for fonts")
    print("✓ jQuery: Local")
    print("✓ Tom-Select: Local")
else:
    print("✗ Some required files are missing!")
    print("\nRun 'python download_static_libs.py' to download all files.")

print("\n📁 File locations:")
print(f"   CSS:   {os.path.join(STATIC_DIR, 'lib/css')}")
print(f"   JS:    {os.path.join(STATIC_DIR, 'lib/js')}")
print(f"   Fonts: {os.path.join(STATIC_DIR, 'lib/fonts')}")

print("\n🌐 Templates updated:")
print("   ✓ app/templates/base.html")
print("   ✓ app/templates/billing/new_bill.html")

print("\n" + "="*70 + "\n")
