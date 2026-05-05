# Temple Billing & Management System

A comprehensive web-based application for managing temple operations including billing, devotee management, pooja scheduling, inventory tracking, and financial reporting.

## Features

### 🙏 Core Modules

1. **Devotee Management**
   - Register devotees with personal details (name, nakshatra, gotra, family members)
   - Auto-generated unique Devotee IDs (DEV-XXXXX)
   - Search by name, phone, or ID
   - View complete billing history

2. **Pooja Services Master**
   - Manage all temple services and poojas
   - Set pricing, duration, and capacity
   - Link required materials to inventory
   - Categorize by type (Daily Archana, Special Pooja, Homam, Festival)

3. **POS-Style Billing**
   - Quick billing interface for walk-in devotees
   - Mix poojas and retail items in single bill
   - Apply discounts (amount or percentage)
   - Accept multiple payment modes (Cash, UPI, Card, DD)
   - Generate printable/PDF receipts
   - WhatsApp receipt sharing

4. **Pooja Scheduling**
   - Book poojas for future dates
   - Calendar view of scheduled poojas
   - Slot availability checking
   - Priest assignment
   - Status tracking (Booked → Confirmed → Completed → Cancelled)

5. **Inventory Management**
   - Track stock items (flowers, prasad, pooja materials)
   - Automatic stock deduction on sales
   - Stock-in/Stock-out transactions
   - Low stock alerts
   - Inventory valuation reports

6. **Dashboard**
   - Today's collection summary
   - Payment mode breakdown
   - Scheduled poojas for the day
   - Top revenue-generating poojas
   - Low stock alerts
   - Quick action buttons

7. **Reports**
   - Collection report (daily/weekly/monthly)
   - Pooja-wise revenue analysis
   - Devotee billing history
   - Inventory consumption
   - Priest-wise statistics
   - Export to PDF and CSV

8. **Settings**
   - Temple configuration (name, address, logo)
   - User management (Admin, Cashier, Priest roles)
   - Priest management
   - Database backup
   - Time slot configuration

## Tech Stack

- **Backend**: Python 3.10+, Flask
- **Database**: SQLite (development), PostgreSQL-ready (production)
- **ORM**: SQLAlchemy
- **Frontend**: Jinja2 templates, Bootstrap 5
- **PDF Generation**: WeasyPrint
- **Authentication**: Flask-Login with bcrypt

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Step 1: Clone or Extract the Project

```bash
cd temple_app
```

### Step 2: Create Virtual Environment (Windows)

```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```cmd
pip install -r requirements.txt
```

### Step 4: Initialize Database

**Method 1: Using Python directly (Recommended for Windows)**

```cmd
python run.py init_db
python run.py seed_data
```

**Method 2: Using Flask CLI**

First, set the Flask app environment variable:
```cmd
set FLASK_APP=run.py
flask init_db
flask seed_data
```

### Step 5: Run the Application

```cmd
python run.py
```

The application will be accessible at: **http://localhost:5000**

---

## Flask CLI Commands Reference (Windows)

### Set Flask App Variable (Required for Flask CLI)

```cmd
set FLASK_APP=run.py
```

### Available Flask Commands

```cmd
# Initialize database tables
flask init_db

# Seed database with sample data
flask seed_data

# Start interactive Python shell with app context
flask shell

# Run development server
flask run

# Database migrations (if using Flask-Migrate)
flask db init
flask db migrate -m "message"
flask db upgrade
```

### Direct Python Commands (Alternative for Windows)

If you prefer not to use Flask CLI, you can run commands directly:

```cmd
# Initialize database
python run.py init_db

# Seed database with sample data
python run.py seed_data

# Run the application
python run.py
```

---

## Default Login Credentials

After running `seed_data`, you can login with:

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Cashier | cashier | cashier123 |
| Priest | priest | priest123 |

**⚠️ Important**: Change these passwords immediately in production!

---

## Environment Variables (Windows)

Configure these variables in Windows Command Prompt before running the application:

```cmd
# Set Flask configuration (development, production, testing)
set FLASK_CONFIG=development

# Set Flask app entry point (required for Flask CLI)
set FLASK_APP=run.py

# Optional: Database URL (uses SQLite by default)
set DATABASE_URL=sqlite:///temple.db
```

---

## Troubleshooting

### Issue: "No such command 'seed_data'"

**Solution 1**: Set the Flask app first, then run the command:
```cmd
set FLASK_APP=run.py
flask seed_data
```

**Solution 2**: Use Python directly (no environment variable needed):
```cmd
python run.py seed_data
```

### Issue: Database file not created

**Solution**: Initialize the database first:
```cmd
python run.py init_db
```

### Issue: "ModuleNotFoundError" when running commands

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Flask CLI commands not recognized

**Solution**: Set the FLASK_APP environment variable:
```cmd
set FLASK_APP=run.py
flask init_db
flask seed_data
```

---

## Production Deployment (Windows Server)

For production deployment on Windows, use a production-grade WSGI server:

### Using Waitress (Windows-Recommended)

```cmd
pip install waitress
waitress-serve --port=5000 run:app
```

### Required Production Environment Variables

```cmd
set FLASK_CONFIG=production
set SECRET_KEY=your-secure-random-key-here
set DATABASE_URL=postgresql://user:password@localhost/temple_db
```

**Note**: Ensure `SECRET_KEY` is a strong, random string in production.

---

## User Roles & Permissions

### Admin
- Full access to all features
- User management
- Settings configuration
- Database backup
- All reports

### Cashier
- Create bills and receipts
- Manage devotees
- View reports
- Process payments
- Book poojas
- Inventory management (stock in/out)
- View reports

### Priest
- View scheduled poojas
- Mark poojas as completed
- View devotee details

## Configuration

### Development Mode (Default)

The application runs in development mode by default with SQLite database.

### Production Mode

1. Set environment variable:
   ```bash
   export FLASK_CONFIG=production
   ```

2. Configure PostgreSQL database:
   ```bash
   export DATABASE_URL="postgresql://username:password@host:port/database"
   ```

3. Set secret key:
   ```bash
   export SECRET_KEY="your-secret-key-here"
   ```

4. Run with production server (e.g., Gunicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

## Database Migrations

If you make changes to models:

```bash
# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Key Features Explained

### Bill Number Generation
- Format: `BILL-YYYY-XXXXXX`
- Never resets; maintains global sequence
- Example: `BILL-2024-000123`

### Monetary Values
- Stored as integers (paise) to avoid floating-point errors
- Displayed as ₹ with 2 decimal places
- Example: 10000 paise = ₹100.00

### Soft Deletes
- All deletions are soft (is_active flag)
- No data is permanently removed
- Can be recovered if needed

### Receipt Printing
- Optimized for 80mm thermal printers
- Print-friendly CSS
- PDF download option
- WhatsApp sharing capability

## Sample Data Included

- **Poojas**: 10 common temple services (Ganapathi Pooja, Satyanarayana Pooja, Rudrabhishek, etc.)
- **Inventory**: 20 items (flowers, prasad, pooja materials)
- **Devotees**: 3 sample devotees with complete details
- **Priests**: 3 priests with specializations

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `POST /auth/change-password` - Change password

### Devotees
- `GET /devotees/` - List devotees
- `POST /devotees/add` - Add devotee
- `GET /devotees/<id>` - View devotee
- `POST /devotees/<id>/edit` - Edit devotee

### Billing
- `POST /billing/new` - Create bill
- `GET /billing/<id>` - View bill
- `GET /billing/<id>/receipt` - Print receipt
- `GET /billing/<id>/receipt-pdf` - Download PDF

### Poojas
- `GET /poojas/services` - List services
- `GET /poojas/bookings` - List bookings
- `POST /poojas/bookings/add` - Create booking
- `GET /poojas/calendar` - Calendar view

## File Structure

```
temple_app/
├── app/
│   ├── __init__.py           # App factory
│   ├── models.py             # Database models
│   ├── seed.py               # Seed data script
│   ├── routes/               # Route blueprints
│   │   ├── auth.py
│   │   ├── billing.py
│   │   ├── dashboard.py
│   │   ├── devotees.py
│   │   ├── inventory.py
│   │   ├── poojas.py
│   │   ├── reports.py
│   │   └── settings.py
│   ├── templates/            # Jinja2 templates
│   └── static/              # CSS, JS, uploads
├── migrations/              # Database migrations
├── config.py               # Configuration
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### Database Issues

**Error: "No such table"**
```bash
python run.py init_db
```

**Reset database**
```bash
rm temple_dev.db
python run.py init_db
python run.py seed_data
```

### Port Already in Use

Change port in `run.py`:
```python
app.run(host='0.0.0.0', port=5001)
```

### WeasyPrint Installation Issues

**Windows**: Install GTK+ runtime from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

**Linux**: 
```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0
```

## Cloud Deployment

### AWS Deployment

1. Use RDS for PostgreSQL database
2. Configure environment variables
3. Use Elastic Beanstalk or EC2
4. Set up S3 for file uploads

### Google Cloud Platform

1. Use Cloud SQL for PostgreSQL
2. Deploy to App Engine or Cloud Run
3. Use Cloud Storage for uploads

### Azure

1. Use Azure Database for PostgreSQL
2. Deploy to App Service
3. Use Blob Storage for uploads

## Security Considerations

- Change default passwords
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Implement rate limiting
- Regular database backups
- Keep dependencies updated

## Support & Contribution

For issues, feature requests, or contributions:
1. Document the issue clearly
2. Provide steps to reproduce
3. Include system information

## License

This project is provided as-is for temple management purposes.

## Acknowledgments

Built with ❤️ for efficient temple operations management.

---

🕉️ **May the divine bless all users of this system!**
