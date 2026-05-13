from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
babel = Babel()


def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    app.config['LANGUAGES'] = ['en', 'ml']  # English, Malayalam
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    babel.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Import and register blueprints
    from app.routes import auth, billing, devotees, poojas, inventory, reports, settings, dashboard
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(billing.bp)
    app.register_blueprint(devotees.bp)
    app.register_blueprint(poojas.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(dashboard.bp)
    
    # Register template filters
    register_template_filters(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Setup locale selector
    @app.context_processor
    def inject_template_globals():
        version_file = os.environ.get('APP_VERSION_FILE', '/app/.build-version')
        app_version = os.environ.get('APP_VERSION', '').strip()
        if not app_version:
            try:
                with open(version_file, 'r', encoding='utf-8') as handle:
                    app_version = handle.read().strip()
            except OSError:
                app_version = 'dev'
        return {
            'locale': request.accept_languages.best_match(app.config['LANGUAGES']) or 'en',
            'app_version': app_version
        }
    
    return app


def register_template_filters(app):
    """Register custom Jinja2 filters"""
    from datetime import datetime
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Format paise to rupees with ₹ symbol"""
        if value is None:
            return '₹0.00'
        rupees = value
        return f'₹{rupees:,.2f}'
    
    @app.template_filter('format_date')
    def format_date_filter(value, format='%d-%b-%Y'):
        """Format datetime object"""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('format_datetime')
    def format_datetime_filter(value, format='%d-%b-%Y %I:%M %p'):
        """Format datetime with time"""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('date')
    def date_filter(value, format='%Y-%m-%d'):
        """Format date - compatible with Jinja2 3.0+"""
        if value == 'now':
            value = datetime.now()
        if isinstance(value, str):
            return value
        if value is None:
            return ''
        return value.strftime(format)


# User loader for Flask-Login
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
