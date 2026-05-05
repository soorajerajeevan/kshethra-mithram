from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """User accounts for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, cashier, priest
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Devotee(db.Model):
    """Devotee/Customer master"""
    __tablename__ = 'devotees'
    
    id = db.Column(db.Integer, primary_key=True)
    devotee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)  # DEV-00123
    full_name = db.Column(db.String(150), nullable=False, index=True)
    nakshatra = db.Column(db.String(50))
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    gotra = db.Column(db.String(100))
    family_members = db.Column(db.Text)  # JSON or comma-separated
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bills = db.relationship('Bill', backref='devotee', lazy='dynamic')
    bookings = db.relationship('PoojaBooking', backref='devotee', lazy='dynamic')
    
    def __repr__(self):
        return f'<Devotee {self.devotee_id} - {self.full_name}>'


class PoojaService(db.Model):
    """Pooja services master"""
    __tablename__ = 'pooja_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)  # legacy mirror (Malayalam display)
    english_name = db.Column(db.String(200), index=True)
    malayalam_name = db.Column(db.String(200), index=True)
    category = db.Column(db.String(100))  # Daily Archana, Special Pooja, Homam, Festival
    description = db.Column(db.Text)
    default_price = db.Column(db.Integer, nullable=False)  # in paise
    duration_minutes = db.Column(db.Integer, default=30)
    max_bookings_per_day = db.Column(db.Integer, default=10)
    add_to_booking = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    materials = db.relationship('ServiceMaterial', backref='service', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('PoojaBooking', backref='service', lazy='dynamic')

    @property
    def display_name(self):
        return self.malayalam_name or self.name or self.english_name or ''
    
    def __repr__(self):
        return f'<PoojaService {self.display_name}>'


class ServiceMaterial(db.Model):
    """Link between pooja services and inventory items"""
    __tablename__ = 'service_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('pooja_services.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)  # per pooja
    
    __table_args__ = (db.UniqueConstraint('service_id', 'inventory_id', name='_service_inventory_uc'),)


class InventoryItem(db.Model):
    """Inventory/stock management"""
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(100))  # flowers, fruits, prasad, pooja_kits, etc.
    unit = db.Column(db.String(20), nullable=False)  # kg, nos, pack, litre
    current_stock = db.Column(db.Float, default=0.0, nullable=False)
    reorder_level = db.Column(db.Float, default=0.0)
    supplier = db.Column(db.String(200))
    cost_price = db.Column(db.Integer, default=0)  # in paise per unit
    selling_price = db.Column(db.Integer, default=0)  # in paise per unit
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('StockTransaction', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    materials = db.relationship('ServiceMaterial', backref='inventory', lazy='dynamic')
    
    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_level
    
    def __repr__(self):
        return f'<InventoryItem {self.name}>'


class StockTransaction(db.Model):
    """Stock in/out transactions"""
    __tablename__ = 'stock_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_items.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # IN, OUT
    quantity = db.Column(db.Float, nullable=False)
    reference_type = db.Column(db.String(50))  # PURCHASE, SALE, POOJA, ADJUSTMENT
    reference_id = db.Column(db.Integer)  # Bill ID or Booking ID
    supplier = db.Column(db.String(200))
    cost = db.Column(db.Integer, default=0)  # in paise
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'<StockTransaction {self.transaction_type} - {self.quantity}>'


class Bill(db.Model):
    """Billing master"""
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # BILL-2024-00456
    devotee_id = db.Column(db.Integer, db.ForeignKey('devotees.id'), nullable=False)
    bill_date = db.Column(db.DateTime, default=datetime.now, nullable=False, index=True)
    subtotal = db.Column(db.Integer, nullable=False)  # in paise
    discount_amount = db.Column(db.Integer, default=0)  # in paise
    discount_percent = db.Column(db.Float, default=0.0)
    donation_amount = db.Column(db.Integer, default=0)  # in paise
    tax_amount = db.Column(db.Integer, default=0)  # in paise (for future GST)
    grand_total = db.Column(db.Integer, nullable=False)  # in paise
    payment_mode = db.Column(db.String(20), nullable=False)  # Cash, UPI, Card, DD
    payment_reference = db.Column(db.String(100))  # UPI ID, Card last 4 digits, DD number
    booking_id = db.Column(db.Integer, db.ForeignKey('pooja_bookings.id'))  # if from booking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('BillItem', backref='bill', lazy='dynamic', cascade='all, delete-orphan')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Bill {self.bill_number}>'


class BillItem(db.Model):
    """Line items in a bill"""
    __tablename__ = 'bill_items'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # POOJA, RETAIL
    item_id = db.Column(db.Integer)  # PoojaService.id or InventoryItem.id
    item_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Float, default=1.0, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)  # in paise
    total_price = db.Column(db.Integer, nullable=False)  # in paise
    
    def __repr__(self):
        return f'<BillItem {self.item_name}>'


class PoojaBooking(db.Model):
    """Future pooja bookings/scheduling"""
    __tablename__ = 'pooja_bookings'
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(50), unique=True, nullable=False, index=True)  # BOOK-2024-00123
    devotee_id = db.Column(db.Integer, db.ForeignKey('devotees.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('pooja_services.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    quantity = db.Column(db.Integer, default=1)
    special_instructions = db.Column(db.Text)
    advance_paid = db.Column(db.Integer, default=0)  # in paise
    total_amount = db.Column(db.Integer, nullable=False)  # in paise
    balance_amount = db.Column(db.Integer, default=0)  # in paise
    status = db.Column(db.String(20), default='BOOKED')  # BOOKED, CONFIRMED, COMPLETED, CANCELLED
    completed_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    bill = db.relationship('Bill', foreign_keys=[bill_id])
    
    def __repr__(self):
        return f'<PoojaBooking {self.booking_number}>'


class Priest(db.Model):
    """Priest/Pujari master"""
    __tablename__ = 'priests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(200))  # e.g., "Homam specialist"
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Priest {self.name}>'


class TempleSettings(db.Model):
    """Temple configuration settings"""
    __tablename__ = 'temple_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Setting {self.key}>'
