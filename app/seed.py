from app import db
from app.models import (FamilyMember, User, Devotee, PoojaService, InventoryItem, Priest, TempleSettings)
from datetime import datetime
import json


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
        ('receipt_footer', '', 'Receipt footer message'),
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
        ('PUSHPANJALI', 'പുഷ്പാഞ്ജലി', 10),
        ('DHAARA', 'ധാര', 50),
        ('KSHEERA DHARA', 'ക്ഷീരധാര', 100),
        ('NEERANJANAM', 'നീരാഞ്ജനം', 75),
        
        ('VELLA NIVEDHYAM', 'വെള്ള നിവേദ്യം', 50),
        ('PAALPAYASAM', 'പാൽപ്പായസം', 100),
        ('KOOTTU PAAYASAM', 'കൂട്ട് പായസം', 100),
        ('PIZHINJU PAYASAM', 'പിഴിഞ്ഞു പായസം', 150),
        ('KADUM PAYASAM', 'കടും പായസം', 150),
        ('NEYY PAYASAM', 'നെയ് പായസം', 160),
        ('ADA NIVEDHYAM', 'അട നിവേദ്യം', 150),
        ('OTTAYAPPAM', 'ഒറ്റയപ്പം', 200),
        ('THRIMADHURAM', 'ത്രിമധുരം', 75),
        
        ('THULABHARAM', 'തുലാഭാരം', 100),
        ('CHOROONU', 'ചോറൂണ്', 200),
        ('GANAPATHI HOMAM', 'ഗണപതി ഹോമം', 100),
        ('ASHTA DRAVYA GANAPATHI HOMAM', 'അഷ്ടദ്രവ്യ ഗണപതി ഹോമം', 500),
        ('KARUKA HOMAM', 'കറുക ഹോമം', 100),
        ('MRITHYUNJAYA HOMAM', 'മൃത്യുഞ്ജയ ഹോമം', 1500),
        
        ('EZHUTHINU IRUTHAL', 'എഴുത്തിനു ഇരുത്തൽ', 30),
        ('THAALI POOJA', 'താലി പൂജ', 10),
        ('VIVAAHAM', 'വിവാഹം', 500),
        ('PATTUM THALIYUM SAMARPPANAM', 'പട്ടും താലിയും സമർപ്പണം', 250),
        ('KETTUNIRA', 'കെട്ടുനിറ', 20),
        ('PAALOOTTU', 'പാലൂട്ട്', 30),
        
        ('PITHRU NAMASKARAM', 'പിതൃ നമസ്കാരം', 50),
        ('KOOTTA NAMASKARAM', 'കൂട്ട നമസ്കാരം', 100),
        
        ('SATHRUSAMHARA PUSHPANJALI', 'ശത്രുസംഹാര പുഷ്പാഞ്ജലി', 30),
        ('AAYURSOOKTHA PUSHPANJALI', 'ആയുർസൂക്ത പുഷ്പാഞ്ജലി', 30),
        ('PURUSHASOOKTHA PUSHPANJALI', 'പുരുഷസൂക്ത പുഷ്പാഞ്ജലി', 30),
        ('MRITHYUNJAYA PUSHPANJALI', 'മൃത്യുഞ്ജയ പുഷ്പാഞ്ജലി', 30),
        ('SWAYAMVARA PUSHPANJALI', 'സ്വയംവര പുഷ്പാഞ്ജലി', 30),
        ('BHAGYASOOKTHA PUSHPANJALI', 'ഭാഗ്യസൂക്ത പുഷ്പാഞ്ജലി', 30),
        ('AKHORA MANTHRA PUSHPANJALI', 'അഘോര മന്ത്ര പുഷ്പാഞ്ജലി', 30),
        ('UMAA MAHESWARA PUSHPANJALI', 'ഉമാമഹേശ്വര പുഷ്പാഞ്ജലി', 30),

        ('SREE RUDHRAA MANTHRA ARCHANA', 'ശ്രീ രുദ്ര മന്ത്ര അർച്ചന', 30),
        ('PAASUPATHA MANTHRA ARCHANA', 'പാശുപത മന്ത്ര അർച്ചന', 30),
        ('VIDHYAGOPALA MANTRA ARCHANA', 'വിദ്യാഗോപാല മന്ത്ര അർച്ചന', 30),
        ('SREE SOOKTHA ARCHANA', 'ശ്രീ സൂക്ത അർച്ചന', 30),
        
        ('AIKYAMATHYA SOOKTHAM', 'ഐക്യമത്യ സൂക്തം', 30),
        ('SAMVADHASOOKTHAM', 'സംവാദസൂക്തം', 30),
        
        ('YAKSHIYAMMAKKU PAALPAYASAM', 'യക്ഷിയമ്മയ്ക്ക് പാൽപ്പായസം', 100),
        ('BRAHMARAKSHASSINU PAALPAYASAM', 'ബ്രഹ്മരക്ഷസ്സിനു പാൽപ്പായസം', 100),
        ('PATHMAM ITTU PAALPAYASAM', 'പത്മം ഇട്ട് പാൽപ്പായസം', 100),
    
        ('NOOTTONNU KUDAM DHAARA', 'നൂറ്റൊന്ന് കുടം ധാര', 301),
        ('AAYIRAM KUDAM DHAARA', 'ആയിരം കുടം ധാര', 1500),
        ('KARIKKABHISHEKAM', 'കരിക്കാഭിഷേകം', 75),
        ('SANGHABHISHEKAM', 'ശംഖാഭിഷേകം', 150),
        ('BHASMA ABHISHEKAM', 'ഭസ്മ അഭിഷേകം', 100),
        
        ('108 KOOVALA MALA KONDU MRITHYUNJAYAM', '108 കൂവളമാല കൊണ്ട് മൃത്യുഞ്ജയം', 101),
        ('UMAA MAHESWARA POOJA', 'ഉമാമഹേശ്വര പൂജ', 250),
        ('YAKSHIYAMMA POOJA', 'യക്ഷിയമ്മ പൂജ', 250),
        ('JANMANAKSHATHRA POOJA', 'ജന്മനക്ഷത്ര പൂജ', 250),
        ('ORU NERATHE POOJA', 'ഒരു നേരത്തെ പൂജ', 500),
        ('ORU DHIVASATHE POOJA', 'ഒരു ദിവസത്തെ പൂജ', 1000),
        
        ('DHEEPARADHANA', 'ദീപാരാധന', 750),
        ('CHUTTUVILAKKU', 'ചുറ്റുവിളക്ക്', 3500),
        ('BHAGAVATHI SEVA', 'ഭഗവതി സേവ', 400),
        ('VAAHANA POOJA 4 WHEELER', 'വാഹന പൂജ 4 വീലർ', 500),
        ('VAAHANA POOJA 2 WHEELER', 'വാഹന പൂജ 2 വീലർ', 250),
    ]
    
    for english_name, malayalam_name, rate_rupees in poojas_data:
        if not PoojaService.query.filter_by(english_name=english_name).first():
            pooja = PoojaService(
                english_name=english_name,
                malayalam_name=malayalam_name,
                category='Special Pooja',
                description='',
                default_price=int(rate_rupees),
                duration_minutes=30,
                max_bookings_per_day=50,
                add_to_booking=True
            )
            db.session.add(pooja)
    
    print("✓ Pooja services created")
    
    # Create sample inventory items
    inventory_data = [
        
        ('എണ്ണ ', 'Pooja Items', 'nos', 100.0, 100.0, 'Kerala Pooja Traders', 10, 10),
        ('എള്ളുതിരി ', 'Pooja Items', 'nos', 1000.0, 20.0, 'Divine Supplies', 8, 10),
        ('ചന്ദനത്തിരി', 'Pooja Items', 'nos', 20.0, 100.0, 'Temple Essentials Co', 10, 10),
        ('കർപ്പൂരം', 'Pooja Items', 'nos', 50.0, 10.0, 'Shakti Traders', 10, 10),
        ('മാല', 'Pooja Items', 'bundle', 50.0, 25.0, 'Local Farmers', 20, 20),
        ('നെയ്യ്‌വിളക്ക്', 'Pooja Items', 'nos', 50.0, 10.0, 'Green Leaf Suppliers', 30, 30),
        ('നാളികേരം', 'Pooja Items', 'nos', 100.0, 20.0, 'Flower Market Co', 50, 50)
                
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
            'Sooraj',
            'ഉത്രാടം',
            '+91 9746199209',
            'sooraj@email.com',
            'Edattu, Varapptty',
            'VPTY'
        )
    ]
    
    devotee_id_start = 1
    for name, nakshatra, phone, email, address, gotra in devotees_data:
        if not Devotee.query.filter_by(phone=phone).first():
            devotee = Devotee(
                devotee_id=f'DEV-{devotee_id_start:05d}',
                full_name=name,
                nakshatra=nakshatra,
                phone=phone,
                email=email,
                address=address,
                gotra=gotra
            )
            db.session.add(devotee)
            devotee_id_start += 1
            
    # Create sample family members for the first devotee
    first_devotee = Devotee.query.first()
    if first_devotee:
        family_members = [
            ('Geethu', 'തൃക്കേട്ട'),
            ('Sulochana', 'ഉത്രം')
        ]
        for name, nakshatra in family_members:
            member = FamilyMember(
                devotee_id=first_devotee.id,
                name=name,
                nakshathram=nakshatra
            )
            db.session.add(member)
    
    print("✓ Sample devotees created")
    
    db.session.commit()
    print("\n✅ Database seeded successfully!")
    print("\nLogin credentials:")
    print("  Admin:   username=admin,   password=admin123")
    print("  Cashier: username=cashier, password=cashier123")
    print("  Priest:  username=priest,  password=priest123")
