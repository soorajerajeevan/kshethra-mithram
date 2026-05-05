import os
import sys
from app import create_app, db
from app.models import User, Devotee, PoojaService, InventoryItem, Bill, PoojaBooking

# Create app with specified config (default to development)
app = create_app(os.getenv('FLASK_CONFIG') or 'development')


@app.shell_context_processor
def make_shell_context():
    """Make database models available in Flask shell"""
    return {
        'db': db,
        'User': User,
        'Devotee': Devotee,
        'PoojaService': PoojaService,
        'InventoryItem': InventoryItem,
        'Bill': Bill,
        'PoojaBooking': PoojaBooking
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def seed_data():
    """Seed the database with sample data"""
    from app.seed import seed_all
    seed_all()
    print("Database seeded successfully!")


def handle_cli_commands():
    """Handle command-line arguments for convenience (python run.py init_db or python run.py seed_data)"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init_db':
            with app.app_context():
                db.create_all()
                print("Database initialized successfully!")
            return True
        elif command == 'seed_data':
            with app.app_context():
                from app.seed import seed_all
                seed_all()
                print("Database seeded successfully!")
            return True
    
    return False


if __name__ == '__main__':
    # Check if a CLI command was provided as argument
    if handle_cli_commands():
        sys.exit(0)
    
    # Otherwise, run the Flask development server
    debug = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=5000, debug=debug, use_reloader=False)
