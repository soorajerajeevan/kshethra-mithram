#!/usr/bin/env python3
"""
Download CDN files locally for offline support
This script downloads Bootstrap, jQuery, Tom-Select and other dependencies
to make the application work without internet connection
"""

import os
import urllib.request
import urllib.error
from pathlib import Path

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'app', 'static')
CSS_DIR = os.path.join(STATIC_DIR, 'lib', 'css')
JS_DIR = os.path.join(STATIC_DIR, 'lib', 'js')
FONTS_DIR = os.path.join(STATIC_DIR, 'lib', 'fonts')

# Create directories
for directory in [CSS_DIR, JS_DIR, FONTS_DIR]:
    os.makedirs(directory, exist_ok=True)
    print(f"✓ Created directory: {directory}")

# Files to download
FILES_TO_DOWNLOAD = {
    # Bootstrap CSS
    CSS_DIR: {
        'bootstrap.min.css': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
        'tom-select.bootstrap5.min.css': 'https://cdn.jsdelivr.net/npm/tom-select@2.4.3/dist/css/tom-select.bootstrap5.min.css',
    },
    # Bootstrap JS
    JS_DIR: {
        'bootstrap.bundle.min.js': 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
        'jquery-3.6.0.min.js': 'https://code.jquery.com/jquery-3.6.0.min.js',
        'tom-select.complete.min.js': 'https://cdn.jsdelivr.net/npm/tom-select@2.4.3/dist/js/tom-select.complete.min.js',
    },
    # Bootstrap Icons fonts - Using unpkg CDN which has better availability
    FONTS_DIR: {
        'bootstrap-icons.woff2': 'https://unpkg.com/bootstrap-icons@1.11.0/font/bootstrap-icons.woff2',
        'bootstrap-icons.woff': 'https://unpkg.com/bootstrap-icons@1.11.0/font/bootstrap-icons.woff',
    }
}

# Bootstrap Icons CSS (special handling)
BOOTSTRAP_ICONS_CSS = 'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'

print("\n" + "="*60)
print("DOWNLOADING CDN FILES LOCALLY")
print("="*60 + "\n")

downloaded_count = 0
failed_count = 0

for directory, files in FILES_TO_DOWNLOAD.items():
    for filename, url in files.items():
        filepath = os.path.join(directory, filename)
        try:
            print(f"Downloading: {filename}...", end=" ")
            urllib.request.urlretrieve(url, filepath)
            print("✓")
            downloaded_count += 1
        except urllib.error.URLError as e:
            print(f"✗ (Error: {e})")
            failed_count += 1
        except Exception as e:
            print(f"✗ (Error: {str(e)})")
            failed_count += 1

# Download Bootstrap Icons CSS with modified paths
print(f"Downloading: bootstrap-icons.css...", end=" ")
try:
    bootstrap_icons_css_path = os.path.join(CSS_DIR, 'bootstrap-icons.css')
    urllib.request.urlretrieve(BOOTSTRAP_ICONS_CSS, bootstrap_icons_css_path)
    
    # Modify the CSS to use relative font paths
    with open(bootstrap_icons_css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Replace absolute URLs with relative paths
    css_content = css_content.replace(
        'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/',
        '../fonts/'
    )
    
    with open(bootstrap_icons_css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print("✓")
    downloaded_count += 1
except Exception as e:
    print(f"✗ (Error: {str(e)})")
    failed_count += 1

print("\n" + "="*60)
print(f"DOWNLOAD SUMMARY: {downloaded_count} successful, {failed_count} failed")
print("="*60)

if failed_count == 0:
    print("\n✓ All files downloaded successfully!")
    print("\nNext steps:")
    print("1. Update templates to use local files")
    print("2. Run the Flask app")
    print("3. All resources will now work offline!")
else:
    print(f"\n⚠ {failed_count} files failed to download. Check your internet connection and try again.")

print("\nLocal files structure:")
print(f"  CSS:   {CSS_DIR}")
print(f"  JS:    {JS_DIR}")
print(f"  Fonts: {FONTS_DIR}")
