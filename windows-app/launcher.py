#!/usr/bin/env python3
"""
Windows Standalone Launcher for Kshethra-Mithram

This script is the entry point for the PyInstaller-compiled .exe.
It handles:
- Detection of frozen (PyInstaller) vs development mode
- Setting up writable paths for database, uploads, and app secrets
- Initializing the Flask app and database
- Starting Flask and opening the browser
- Managing system tray icon for app control
"""

import sys
import os
import threading
import webbrowser
import time
import secrets
from pathlib import Path
from io import BytesIO


def get_base_dir():
    """Get the base directory where the app is running from."""
    if getattr(sys, 'frozen', False):
        # PyInstaller sets sys.frozen and sys._MEIPASS
        return sys._MEIPASS
    else:
        # Development mode: parent of this script's directory
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_app_data_dir():
    """Get or create the writable app data directory in %APPDATA%."""
    appdata = os.environ.get('APPDATA')
    if not appdata:
        appdata = os.path.expanduser('~')

    app_data_path = os.path.join(appdata, 'kshethra-mithram')
    os.makedirs(app_data_path, exist_ok=True)
    return app_data_path


def setup_environment():
    """Set up all environment variables and working directory."""
    base = get_base_dir()
    app_data = get_app_data_dir()

    # Change working directory to base so relative imports work
    os.chdir(base)

    # Add base directory to Python path so 'app' module can be imported
    if base not in sys.path:
        sys.path.insert(0, base)

    # Set Flask configuration
    os.environ.setdefault('FLASK_CONFIG', 'production')

    # Database: stored in %APPDATA% for persistence across app updates
    db_path = os.path.join(app_data, 'temple.db')
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

    # App secret key: generate once, persist across restarts
    secret_key_file = os.path.join(app_data, '.appkey')
    if not os.path.exists(secret_key_file):
        secret_key = secrets.token_hex(32)
        with open(secret_key_file, 'w') as f:
            f.write(secret_key)
    else:
        with open(secret_key_file, 'r') as f:
            secret_key = f.read().strip()

    os.environ['SECRET_KEY'] = secret_key

    # Upload folder: also in %APPDATA%
    uploads_dir = os.path.join(app_data, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    os.environ['UPLOAD_FOLDER'] = uploads_dir


def create_tray_icon():
    """Create a PIL Image for the tray icon."""
    from PIL import Image, ImageDraw
    
    # Create a simple temple icon: orange/yellow square with a small design
    size = (64, 64)
    image = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple temple shape (orange background with a top)
    draw.rectangle([8, 20, 56, 56], fill='#FF8C00', outline='#FF6347', width=2)
    draw.polygon([(8, 20), (32, 5), (56, 20)], fill='#FF6347', outline='#FF6347')
    
    return image


def start_tray_icon(app_ref):
    """Start the system tray icon with quit functionality."""
    try:
        from pystray import Icon, Menu, MenuItem
        
        image = create_tray_icon()
        
        def on_quit(icon, item):
            """Handle quit action from tray menu."""
            print("\nShutting down Kshethra-Mithram...")
            icon.stop()
            os._exit(0)
        
        menu = Menu(
            MenuItem('Kshethra-Mithram (Running)', None, enabled=False),
            MenuItem('---', None),
            MenuItem('Open in Browser', lambda: webbrowser.open('http://127.0.0.1:5000')),
            MenuItem('Quit', on_quit)
        )
        
        icon = Icon('kshethra-mithram', image, menu=menu)
        icon.run()
    except Exception as e:
        print(f"Warning: Could not create system tray icon: {e}")


def start_flask():
    """Create and run the Flask application."""
    from app import create_app, db
    from app.models import User

    # Create the Flask app with production config
    app = create_app('production')

    # Override upload folder config if environment variable is set
    if os.environ.get('UPLOAD_FOLDER'):
        app.config['UPLOAD_FOLDER'] = os.environ['UPLOAD_FOLDER']

    # Initialize database tables on first run
    with app.app_context():
        db.create_all()

        # Check if database is empty (no users) and seed if needed
        if User.query.first() is None:
            print("Database is empty. Seeding with initial data...")
            from app.seed import seed_all
            seed_all()
            print("Database seeded successfully!")

    # Run Flask server on localhost only (not accessible from network)
    # debug=False, use_reloader=False to avoid issues with PyInstaller
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False,
        use_debugger=False,
        threaded=True
    )


def open_browser():
    """Wait a moment for Flask to start, then open the browser."""
    time.sleep(2)
    webbrowser.open('http://127.0.0.1:5000')


if __name__ == '__main__':
    # Set up environment first
    setup_environment()

    # Start browser open in a background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Start Flask in a background thread
    flask_thread = threading.Thread(target=start_flask, daemon=False)
    flask_thread.start()

    # Start system tray icon in the main thread
    start_tray_icon(None)
