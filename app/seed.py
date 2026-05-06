from app import db
from app.models import (User, Devotee, PoojaService, InventoryItem, Priest, TempleSettings)
from datetime import datetime
import json


MALAYALAM_NAKSHATHRAS = [
    "01 അശ്വതി",
    "02 ഭരണി",
    "03 കാർത്തിക",
    "04 രോഹിണി",
    "05 മകയിരം",
    "06 തിരുവാതിര",
    "07 പുണർതം",
    "08 പൂയം",
    "09 ആയില്യം",
    "10 മകം",
    "11 പൂരം",
    "12 ഉത്രം",
    "13 അത്തം",
    "14 ചിത്തിര",
    "15 ചോതി",
    "16 വിശാഖം",
    "17 അനിഴം",
    "18 തൃക്കേട്ട",
    "19 മൂലം",
    "20 പൂരാടം",
    "21 ഉത്രാടം",
    "22 തിരുവോണം",
    "23 അവിട്ടം",
    "24 ചതയം",
    "25 പൂരുരുട്ടാതി",
    "26 ഉത്രട്ടാതി",
    "27 രേവതി",
]


def seed_all():
    """Seed database with sample data"""
    print("Seeding database...")
    
    # Create admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@temple.com',
            full_name='Administrator',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("✓ Admin user created (username: admin, password: admin123)")
    
    # Create cashier user
    if not User.query.filter_by(username='cashier').first():
        cashier = User(
            username='cashier',
            email='cashier@temple.com',
            full_name='Cashier User',
            role='cashier',
            is_active=True
        )
        cashier.set_password('cashier123')
        db.session.add(cashier)
        print("✓ Cashier user created (username: cashier, password: cashier123)")
    
    # Create priest user
    if not User.query.filter_by(username='priest').first():
        priest_user = User(
            username='priest',
            email='priest@temple.com',
            full_name='Priest User',
            role='priest',
            is_active=True
        )
        priest_user.set_password('priest123')
        db.session.add(priest_user)
        print("✓ Priest user created (username: priest, password: priest123)")
    
    db.session.commit()
    
    # Create temple settings
    settings_data = [
        ('temple_name', 'Mattakkuzhi Temple', 'Temple name'),
        ('temple_address', 'Temple Road, Temple City - 123456', 'Temple address'),
        ('temple_phone', '+91 1234567890', 'Temple phone'),
        ('temple_email', 'info@temple.com', 'Temple email'),
        ('receipt_footer', '🕉️ May the divine bless you with peace and prosperity!', 'Receipt footer message'),
        ('time_slots', '06:00 AM\n07:00 AM\n08:00 AM\n09:00 AM\n10:00 AM\n11:00 AM\n12:00 PM\n04:00 PM\n05:00 PM\n06:00 PM', 'Available time slots')
    ]
    
    for key, value, desc in settings_data:
        if not TempleSettings.query.filter_by(key=key).first():
            setting = TempleSettings(key=key, value=value, description=desc)
            db.session.add(setting)
    
    print("✓ Temple settings created")
    
    # Create sample priests
    priests_data = [
        ('Swami', '+91 9876543210', 'Mel saanthi')
    ]
    
    for name, phone, spec in priests_data:
        if not Priest.query.filter_by(name=name).first():
            priest = Priest(name=name, phone=phone, specialization=spec)
            db.session.add(priest)
    
    print("✓ Priests created")
    
    # Create sample poojas (English + Malayalam + rate in rupees)
    poojas_data = [
        ('PUSHPANJALI', 'പുഷ്പാഞ്ജലി', 10), ('NAGANGALK PAALUM NOORUM', 'നാഗങ്ങള്‍ക്ക് പാലും നൂറും', 101),
        ('KETHU POOJA', 'കേതു പൂജ', 301), ('VILAKKU', 'വിളക്ക്', 10), ('RAHU POOJA', 'രാഹു പൂജ', 301),
        ('25 PERSONS', '25 പേർക്ക്', 500), ('NAGANGALKU POOJA', 'നാഗങ്ങൾക്ക് പൂജ', 201), ('NEY VILAKKU', 'നെയ്യ് വിളക്ക്', 20),
        ('AAYILYA POOJA', 'ആയില്ല്യ പൂജ', 201), ('50 PERSONS', '50 പേർക്ക്', 1000), ('SOORAYANU POOJA', 'സൂര്യന് പൂജ', 301),
        ('MAALA', 'മാല', 50), ('CHANDHRA POOJA', 'ചന്ദ്ര പൂജ', 301), ('75 PERSONS', '75 പേർക്ക്', 1500),
        ('DHARA', 'ധാര', 10), ('NAGANGALKKU THATTU', 'നാഗങ്ങൾക്ക് തട്ട്', 301), ('SAARASWATHA PUSHPANJALI', 'സാരസ്വത പുഷ്പാഞ്ജലി', 20),
        ('MRITHYUMJAYA PUSHPANJALI', 'മൃത്യുഞ്ജയ പുഷ്പാഞ്ജലി', 20), ('SAARASWATHA PUSHPANJAL', 'സാരസ്വത പുഷ്പാഞ്ജലി', 20),
        ('BHRAMA RAKSHASIN POOJA', 'ബ്രമ രക്ഷസിന് പൂജ', 101), ('100 PERSONS', '100 പേർക്ക്', 2000), ('BUDHANU POOJA', 'ബുധന് പൂജ', 301),
        ('SHUKRANU POOJA', 'ശുക്രന് പൂജ', 301), ('VIDHYASOOKTHA PUSHPANJALI', 'വിദ്യാസൂക്ത പുഷ്പാഞ്ജലി', 20),
        ('BHAGYASOOKTHA PUSHPANJALI', 'ഭാഗ്യസൂക്ത പുഷ്പാഞ്ജലി', 20), ('NEY', 'നെയ്യ്', 20), ('SHANISWARA POOJA', 'ശനീശ്വര പൂജ', 301),
        ('SWASTHIMANTHRA PUSHPANJALI', 'സ്വസ്തിമന്ത്ര പുഷ്പാഞ്ജലി', 20), ('KUMARASOOKTHA PUSHPANJALI', 'കുമാരസൂക്ത പുഷ്പാഞ്ജലി', 50),
        ('DURGAMANTHRA PUSHPANJALI', 'ദുർഗ്ഗാമന്ത്ര പുഷ്പാഞ്ജലി', 20), ('PURUSHASOOKTHA PUSHPANJALI', 'പുരുഷസൂക്ത പുഷ്പാഞ്ജലി', 20),
        ('STHREESOOKTHA PUSHPANJALI', 'സ്ത്രീസുക്ത പുഷ്പാഞ്ജലി', 20), ('SHATHRU SAMHARA PUSHPANJALI', 'ശത്രു സംഹാര പുഷ്പാഞ്ജലി', 20),
        ('ASHTOTHARA PUSHPANJALI', 'അഷ്ടോത്തര പുഷ്പാഞ്ജലി', 20), ('GANAPATHI POOJA', 'ഗണപതി പൂജ', 151),
        ('GANAPATHI HOMAM', 'ഗണപതി ഹോമം', 501), ('ELLU THIRI', 'എള്ള്‌ തിരി', 10), ('MAHARUDHRA ABHISHEKAM', 'മഹാരുദ്ര അഭിഷേകം', 2500),
        ('SWAYAMWARA PUSHPANJALI', 'സ്വയംവര പുഷ്പാഞ്ജലി', 20), ('SREERAMANU POOJA', 'ശ്രീരാമന് പൂജ', 151),
        ('HANUMANU POOJA', 'ഹനുമാന് പൂജ', 151), ('KARUKA HOMAM', 'കറുക ഹോമം', 251), ('THILA HOMAM', 'തില ഹോമം', 251),
        ('VADAMAALA', 'വടമാല', 301), ('AYYAPPANU POOJA', 'അയ്യപ്പന്‍ പൂജ', 151), ('SHIVANU POOJA', 'ശിവന് പൂജ', 151),
        ('AIKYAMATHYA PUSHPANJALI', 'ഐക്യമത്യ പുഷ്പാഞ്ജലി', 20), ('SHADABHISHEKAM', 'ഷഡാഭിഷേകം', 1500), ('PAAL ABHISHEKAM', 'പാൽ അഭിഷേകം', 51),
        ('SHARKARA PAYASAM', 'ശർക്കര പായസം', 50), ('AYYAPPASWAMIKKU NEERANJANAM', 'അയ്യപ്പസ്വാമിക്ക് നീരാഞ്ജനം', 55),
        ('VETTILAMALA', 'വെറ്റിലമാല', 101), ('MUN VILLAKU/ PIN VILLAKU', 'മുന്‍ വിളക്ക്/പിന്‍ വിളക്ക്', 20),
        ('MRITHYUNJAYA HOMAM', 'മൃത്യുഞ്ജയ ഹോമം', 1001), ('SUDHARSHANA HOMAM', 'സുദർശന ഹോമം', 751),
        ('PAAL PAYASAM', 'പാൽ പായസം', 60), ('SHANGABHISHEKAM', 'ശംഖാഭിഷേകം', 51), ('PANINEER ABHISHEKAM', 'പനിനീർ അഭിഷേകം', 101),
        ('DEVIKKU POOJA', 'ദേവിക്ക് പൂജ', 151), ('BHANESHI HOMAM', 'ബാണേശി ഹോമം', 1001), ('THRISHTUPP HOMAM', 'തൃഷ്‌ടുപ്പ് ഹോമം', 1001),
        ('DEVIKKU THATTU', 'ദേവിക്ക് തട്ട്', 20), ('ELANEER ABHISHEKAM', 'ഇളനീർ അഭിഷേകം', 101), ('PANJAMRITHA ABHISHEKAM', 'പഞ്ചാമൃത അഭിഷേകം', 151),
        ('PRATHYINGARA HOMAM', 'പ്രത്യംഗര ഹോമം', 1001), ('OTTAPPAM', 'ഒറ്റപ്പം', 201), ('NEY ABHISHEKAM', 'നെയ്യഭിഷേകം', 251),
        ('BHASMABHISHEKAM', 'ഭസ്മാഭിഷേകം', 101), ('KARUKAMALA', 'കറുകമാല', 50), ('KALABHABHISHEKAM', 'കളഭാഭിഷേകം', 201),
        ('AVAL NIVEDHYAM', 'അവൽ നിവേദ്യം', 50), ('VYAZHAM (GURU) POOJA', 'വ്യാഴം ( ഗുരു) പൂജ', 301),
        ('MUNDANAM( VELSAMARPPANNAM, ARCHANATHATT, PALABHISHEKAM INCLUDED)', 'മുണ്ഡനം( വേൽസമർപ്പണം,അർച്ചനതട്ട്, പാലഭിഷേകം ഉൾപ്പെടെ)', 453),
        ('JANMANAKSHATHRA(BIRTHDAY) POOJA', 'ജന്മനക്ഷത്ര പൂജ', 301), ('THRIMADHURAM', 'ത്രിമധുരം', 100), ('THUMADURAM', 'തുമാധുരം', 100),
        ('VELLARINIVEDHYAM', 'വെള്ളരിനിവേദ്യം', 50), ('MURUKANU VEL SAMARPANAM', 'മുരുകന് വേൽ സമർപ്പണം', 101),
        ('ARCHANATHATT', 'അർച്ചനത്തട്ട്', 50), ('MUTTIRAKKAL', 'മുട്ടിറക്കൽ', 50), ('VIVAHAM', 'വിവാഹം', 2500),
        ('VIVAHAM (SPECIAL)', 'വിവാഹം (സ്പെഷ്യൽ)', 5000), ('VISHESHAL POOJA', 'വിശേഷാൽ പൂജ', 1500), ('CHUTTU VILLAKKU', 'ചുറ്റു വിളക്ക്', 1000),
        ('AIKYAMATHYAM', 'ഐക്യമത്യം', 20), ('EZHUTHINIRUTHAL', 'എഴുത്തിനിരുത്തൽ', 151), ('ORU KUDAM PAALABHISHEKAM', 'ഒരു കുടം പാലഭിഷേകം', 500),
        ('PANAKAM', 'പാനകം', 250), ('DIVASA POOJA', 'ദിവസ പൂജ', 500), ('KARPOORA AARATHI', 'കർപ്പൂര ആരതി', 50),
        ('SHASHTI VRITHAM', 'ഷഷ്ടി വൃതം', 50), ('AAYURSOOKTHA PUSHPANJALI', 'ആയുർസൂക്ത പുഷ്പാഞ്ജലി', 50),
        ('SUBRAMANYA KAVACHA PUSHPANJALI', 'സുബ്രമണ്യ കവച പുഷ്പാഞ്ജലി', 50), ('SUBRAMANYA STHOTHRA PUSHPANJALI', 'സുബ്രമണ്യ സ്തോത്ര പുഷ്പാഞ്ജലി', 50),
        ('SAMVADHA SOOKTHA PUSHPANJALI', 'സംവാദ സൂക്ത പുഷ്പാഞ്ജലി', 20), ('KAVADIYENTHI PRADHAKSHINAM', 'കാവടിയേന്തി പ്രദക്ഷിണം', 101),
        ('CHOROONU', 'ചോറൂണ്', 201), ('NEL PARA', 'നെൽപ്പറ', 151),
    ]
    
    for english_name, malayalam_name, rate_rupees in poojas_data:
        if not PoojaService.query.filter_by(english_name=english_name).first():
            pooja = PoojaService(
                name=malayalam_name,
                english_name=english_name,
                malayalam_name=malayalam_name,
                category='Special Pooja',
                description='',
                default_price=int(rate_rupees),
                duration_minutes=30,
                max_bookings_per_day=50,
                add_to_booking=False
            )
            db.session.add(pooja)
    
    print("✓ Pooja services created")
    
    # Create sample inventory items
    inventory_data = [
        ('കർപ്പൂരം ', 'Pooja Items', 'nos', 55.0, 15.0, 'Kerala Pooja Traders', 25, 30),
        ('ചന്ദനത്തിരി ', 'Pooja Items', 'nos', 30.0, 20.0, 'Divine Supplies', 8, 10),
        ('ചന്ദനം', 'Pooja Items', 'nos', 2.0, 50.0, 'Temple Essentials Co', 100, 150),
        ('കുങ്കുമം', 'Pooja Items', 'nos', 1.0, 100.0, 'Shakti Traders', 50, 60),
        ('തുളസി ഇല', 'Pooja Items', 'bundle', 10.0, 25.0, 'Local Farmers', 30, 50),
        ('കൂവളം ഇല', 'Pooja Items', 'bundle', 12.0, 20.0, 'Green Leaf Suppliers', 25, 45),
        ('പൂവ്', 'Pooja Items', 'nos', 80.0, 30.0, 'Flower Market Co', 120, 180),
        ('നെയ്', 'Pooja Items', 'nos', 60.0, 10.0, 'Pure Ghee Traders', 500, 650),
        ('നെയ് വിളക്ക്', 'Pooja Items', 'nos', 60.0, 10.0, 'Pure Ghee Traders', 10, 15),
        ('തേങ്ങ', 'Pooja Items', 'nos', 25.0, 50.0, 'Coconut Suppliers', 30, 45),
        ('വാഴപ്പഴം', 'Pooja Items', 'nos', 40.0, 20.0, 'Fruit Vendors', 60, 90),
        ('വിളക്ക് തിരി', 'Pooja Items', 'nos', 20.0, 30.0, 'Lamp Accessories Ltd', 25, 40),
        ('എള്ളെണ്ണ', 'Pooja Items', 'nos', 70.0, 15.0, 'Oil Mills Co', 200, 280),
        ('എള്ളെണ്ണ 1L', 'Pooja Items', 'nos', 70.0, 15.0, 'Oil Mills Co', 200, 280),
        ('തെങ്ങെണ്ണ', 'Pooja Items', 'nos', 65.0, 15.0, 'Kerala Oils', 180, 250),
        ('പഞ്ചാമൃതം', 'Pooja Items', 'nos', 50.0, 10.0, 'Temple Mix Suppliers', 300, 420),
        ('അവൽ', 'Pooja Items', 'kg', 35.0, 25.0, 'Grain Suppliers', 70, 110)
    ]
    
    for name, cat, unit, stock, reorder, supplier, cost, selling in inventory_data:
        if not InventoryItem.query.filter_by(name=name).first():
            item = InventoryItem(
                name=name,
                category=cat,
                unit=unit,
                current_stock=stock,
                reorder_level=reorder,
                supplier=supplier,
                cost_price=cost,
                selling_price=selling
            )
            db.session.add(item)
    
    print("✓ Inventory items created")
    
    # Create sample devotees
    devotees_data = [
        (
            'Sooraj ER',
            MALAYALAM_NAKSHATHRAS[0],
            '+91 9876543210',
            'ramesh@email.com',
            'MG Road, City',
            'Bharadwaja',
            json.dumps([
                {'name': 'Geethu', 'nakshathram': MALAYALAM_NAKSHATHRAS[3]},
                {'name': 'Sulochana', 'nakshathram': MALAYALAM_NAKSHATHRAS[7]},
            ], ensure_ascii=False)
        ),
        (
            'Suresh Patel',
            MALAYALAM_NAKSHATHRAS[3],
            '+91 9876543211',
            'suresh@email.com',
            'Temple Street, City',
            'Kashyapa',
            json.dumps([
                {'name': 'Radha', 'nakshathram': MALAYALAM_NAKSHATHRAS[5]},
                {'name': 'Priya', 'nakshathram': MALAYALAM_NAKSHATHRAS[10]},
            ], ensure_ascii=False)
        ),
        (
            'Venkatesh Rao',
            MALAYALAM_NAKSHATHRAS[7],
            '+91 9876543212',
            'venkat@email.com',
            'Main Road, City',
            'Vishwamitra',
            json.dumps([
                {'name': 'Saraswati', 'nakshathram': MALAYALAM_NAKSHATHRAS[12]},
                {'name': 'Karthik', 'nakshathram': MALAYALAM_NAKSHATHRAS[14]},
                {'name': 'Divya', 'nakshathram': MALAYALAM_NAKSHATHRAS[26]},
            ], ensure_ascii=False)
        )
    ]
    
    devotee_id_start = 1
    for name, nakshatra, phone, email, address, gotra, family in devotees_data:
        if not Devotee.query.filter_by(phone=phone).first():
            devotee = Devotee(
                devotee_id=f'DEV-{devotee_id_start:05d}',
                full_name=name,
                nakshatra=nakshatra,
                phone=phone,
                email=email,
                address=address,
                gotra=gotra,
                family_members=family
            )
            db.session.add(devotee)
            devotee_id_start += 1
    
    print("✓ Sample devotees created")
    
    db.session.commit()
    print("\n✅ Database seeded successfully!")
    print("\nLogin credentials:")
    print("  Admin:   username=admin,   password=admin123")
    print("  Cashier: username=cashier, password=cashier123")
    print("  Priest:  username=priest,  password=priest123")
