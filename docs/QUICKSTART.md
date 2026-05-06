# Temple Management System - Quick Start Guide

This guide will help you get the Temple Management System up and running in just a few minutes.

## Prerequisites

- Python 3.10 or higher installed
- pip (Python package manager)
- A modern web browser (Chrome, Firefox, Safari, Edge)

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

Open terminal/command prompt in the `temple_app` folder and run:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Initialize Database with Sample Data

```bash
python run.py init_db
python run.py seed_data
```

This creates:
- Admin, Cashier, and Priest user accounts
- 10 sample pooja services
- 20 inventory items
- 3 sample devotees
- 3 priests

### Step 3: Run the Application

```bash
python run.py
```

The application will start on http://localhost:5000

## Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Cashier | cashier | cashier123 |
| Priest | priest | priest123 |

**⚠️ IMPORTANT**: Change these passwords immediately after first login!

## First Steps After Login

1. **Admin Login** → Go to Settings → Update Temple Information
2. **Add More Devotees** → Devotees → Add Devotee
3. **Create First Bill** → Click "New Bill" → Select Devotee → Add Poojas/Items → Complete
4. **View Dashboard** → See today's collection and statistics

## Common Tasks

### Create a Bill
1. Click "New Bill" in navigation
2. Select devotee (or add new)
3. Add poojas and/or retail items
4. Apply discount if needed
5. Enter payment mode
6. Click "Complete Bill"
7. Print or download PDF receipt

### Book a Pooja
1. Go to Poojas → New Booking
2. Select devotee and pooja service
3. Choose date and time slot
4. Assign priest (optional)
5. Enter advance payment
6. Submit booking

### Add Inventory Stock
1. Go to Inventory → Select Item
2. Click "Stock In"
3. Enter quantity and supplier
4. Save transaction

### Generate Reports
1. Go to Reports
2. Select report type
3. Choose date range
4. View or export to CSV

## Directory Structure

```
temple_app/
├── app/                    # Application code
│   ├── routes/            # URL routes
│   ├── templates/         # HTML templates
│   ├── static/           # CSS, JS, uploads
│   └── models.py         # Database models
├── config.py              # Configuration
├── run.py                # Application entry point
├── requirements.txt      # Dependencies
├── README.md            # Full documentation
└── QUICKSTART.md        # This file
```

## Troubleshooting

### "No module named 'flask'"
Run: `pip install -r requirements.txt`

### "Port 5000 is already in use"
Edit `run.py` and change port to 5001 or another free port

### "Database is locked"
Close any other instances of the application

### WeasyPrint PDF errors on Windows
Install GTK runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

### Reset Everything
```bash
rm temple_dev.db
python run.py init_db
python run.py seed_data
```

## Key Features to Try

1. **Dashboard** - Real-time collection stats
2. **POS Billing** - Quick multi-item billing
3. **Receipt Printing** - Thermal printer optimized
4. **WhatsApp Sharing** - Share receipts via WhatsApp
5. **Booking Calendar** - Schedule future poojas
6. **Inventory Alerts** - Automatic low-stock warnings
7. **Reports** - Collection, pooja-wise, devotee-wise
8. **User Management** - Multiple roles (Admin/Cashier/Priest)

## Production Deployment

For production use with PostgreSQL:

1. Install PostgreSQL
2. Create database: `CREATE DATABASE temple_db;`
3. Set environment variables:
   ```bash
   export FLASK_CONFIG=production
   export DATABASE_URL=postgresql://user:pass@localhost/temple_db
   export SECRET_KEY=your-secret-key-here
   ```
4. Run with Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```

## Need Help?

- Check README.md for detailed documentation
- All monetary values are in Rupee internally 
- Bill numbers never reset - maintain global sequence
- All deletions are soft (is_active flag)
- Database backed up via Settings → Backup

## Next Steps

1. **Customize** → Settings → Update temple name, address, logo
2. **Add Data** → Add your devotees, poojas, inventory items
3. **Start Billing** → Begin creating bills and bookings
4. **Generate Reports** → Track daily collections and performance

---

**🕉️ May the divine bless your temple management journey!**

For detailed documentation, see README.md
