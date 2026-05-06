from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, session
from flask_login import login_required, current_user
from app import db
from app.models import Bill, BillItem, Devotee, PoojaService, InventoryItem, PoojaBooking, StockTransaction
from datetime import datetime
import re
import json
import uuid
# from weasyprint import HTML
import io

bp = Blueprint('billing', __name__, url_prefix='/billing')

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


def generate_bill_number():
    """Generate unique bill number"""
    year = datetime.now().year
    last_bill = Bill.query.filter(
        Bill.bill_number.like(f'BILL-{year}-%')
    ).order_by(Bill.id.desc()).first()
    
    if last_bill:
        last_num = int(last_bill.bill_number.split('-')[2])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f'BILL-{year}-{new_num:06d}'


def generate_devotee_id():
    """Generate unique devotee ID"""
    devotees = Devotee.query.order_by(Devotee.id.desc()).limit(200).all()
    max_num = 0
    for d in devotees:
        match = re.match(r'^DEV-(\d+)$', (d.devotee_id or '').strip(), re.IGNORECASE)
        if match:
            max_num = max(max_num, int(match.group(1)))
    new_num = max_num + 1 if max_num > 0 else 1
    return f'DEV-{new_num:05d}'


def parse_family_members(raw_value):
    """Return list[{'name': str, 'nakshathram': str}] from legacy or JSON formats."""
    if not raw_value:
        return []

    parsed = []
    text = (raw_value or '').strip()
    if not text:
        return []

    # Preferred format: JSON array of objects.
    try:
        data = json.loads(text)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    name = (item.get('name') or '').strip()
                    nak = (item.get('nakshathram') or '').strip()
                    if name:
                        parsed.append({'name': name, 'nakshathram': nak})
            if parsed:
                return parsed
    except Exception:
        pass

    # Legacy fallback: comma-separated names.
    for name in [x.strip() for x in text.split(',') if x.strip()]:
        parsed.append({'name': name, 'nakshathram': ''})
    return parsed


def dump_family_members(items):
    cleaned = []
    seen = set()
    for item in items:
        name = (item.get('name') or '').strip()
        nak = (item.get('nakshathram') or '').strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            # Keep the first entry; if no nak there, fill from later row.
            for existing in cleaned:
                if existing['name'].lower() == key and not existing.get('nakshathram') and nak:
                    existing['nakshathram'] = nak
            continue
        seen.add(key)
        cleaned.append({'name': name, 'nakshathram': nak})
    return json.dumps(cleaned, ensure_ascii=False)


def _safe_float(value, default=0.0):
    """Safely parse a float from form input."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    """Safely parse an int from form input."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def validate_new_bill_form(form):
    """Validate the new bill form data.

    Returns (errors, devotee_raw, pooja_count, retail_count) where *errors*
    is a list of human-readable error strings.  An empty list means the form
    passed validation.
    """
    errors = []

    # --- 1. Devotee validation ---
    devotee_raw = (form.get('devotee_id') or '').strip()
    if not devotee_raw:
        errors.append('Please select a devotee or enter a new devotee name.')
    elif devotee_raw.startswith('NEW::'):
        new_name = devotee_raw.replace('NEW::', '', 1).strip()
        if not new_name:
            errors.append('New devotee name cannot be empty.')
        new_phone = (form.get('new_devotee_phone') or '').strip()
        if not new_phone:
            errors.append('Phone number is required for a new devotee.')
    else:
        if not devotee_raw.isdigit():
            errors.append('Invalid devotee selection.')
        else:
            devotee = Devotee.query.get(int(devotee_raw))
            if not devotee:
                errors.append('Selected devotee not found.')

    # --- 2. Pooja items validation (at least one required) ---
    pooja_count = _safe_int(form.get('pooja_count'), 0)
    valid_pooja_count = 0

    for i in range(pooja_count):
        service_id = (form.get(f'pooja_service_{i}') or '').strip()
        if not service_id:
            continue  # empty row, skip

        valid_pooja_count += 1
        row_label = f'Pooja row {valid_pooja_count}'

        if not service_id.isdigit():
            errors.append(f'{row_label}: Invalid pooja service selected.')
        else:
            service = PoojaService.query.get(int(service_id))
            if not service:
                errors.append(f'{row_label}: Selected pooja service does not exist.')

        devotee_name = (form.get(f'pooja_devotee_name_{i}') or '').strip()
        if not devotee_name:
            errors.append(f'{row_label}: Devotee name is required.')

        nakshathram = (form.get(f'pooja_nakshathram_{i}') or '').strip()
        if not nakshathram:
            errors.append(f'{row_label}: Nakshathram is required.')

        qty_raw = form.get(f'pooja_quantity_{i}')
        qty = _safe_float(qty_raw)
        if qty <= 0:
            errors.append(f'{row_label}: Quantity must be a positive number.')

        price_raw = form.get(f'pooja_price_{i}')
        price = _safe_float(price_raw)
        if price < 0:
            errors.append(f'{row_label}: Amount cannot be negative.')

    if valid_pooja_count == 0:
        errors.append('At least one pooja item is required.')

    # --- 3. Retail items validation (optional, but validate if present) ---
    retail_count = _safe_int(form.get('retail_count'), 0)
    for i in range(retail_count):
        item_id = (form.get(f'retail_item_{i}') or '').strip()
        if not item_id:
            continue  # empty row, skip

        row_label = f'Retail item row {i + 1}'

        if not item_id.isdigit():
            errors.append(f'{row_label}: Invalid item selected.')
        else:
            item = InventoryItem.query.get(int(item_id))
            if not item:
                errors.append(f'{row_label}: Selected item does not exist.')

        qty_raw = form.get(f'retail_quantity_{i}')
        qty = _safe_float(qty_raw)
        if qty <= 0:
            errors.append(f'{row_label}: Quantity must be a positive number.')

        price_raw = form.get(f'retail_price_{i}')
        price = _safe_float(price_raw)
        if price < 0:
            errors.append(f'{row_label}: Price cannot be negative.')

    # --- 4. Discount & donation validation ---
    discount_value_raw = form.get('discount_value')
    discount_value = _safe_float(discount_value_raw, 0.0)
    if discount_value < 0:
        errors.append('Discount amount cannot be negative.')

    discount_type = form.get('discount_type', 'amount')
    if discount_type == 'percent' and discount_value > 100:
        errors.append('Discount percentage cannot exceed 100%.')

    donation_raw = form.get('donation')
    donation = _safe_float(donation_raw, 0.0)
    if donation < 0:
        errors.append('Donation amount cannot be negative.')

    # --- 5. Payment mode ---
    payment_mode = (form.get('payment_mode') or '').strip()
    if payment_mode not in ('Cash', 'UPI', 'Credit'):
        errors.append('Please select a valid payment mode.')

    return errors


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_bill():
    """Create new bill (POS style)"""
    if request.method == 'POST':
        form_token = (request.form.get('submission_token') or '').strip()
        session_token = session.get('new_bill_submission_token', '')
        if not form_token or not session_token or form_token != session_token:
            flash('Duplicate/expired submission prevented. Please submit the bill again.', 'warning')
            return redirect(url_for('billing.new_bill'))

        # ── Validate ──
        errors = validate_new_bill_form(request.form)
        if errors:
            for err in errors:
                flash(err, 'danger')
            # Re-render the form instead of redirecting so flash messages
            # are visible immediately (redirect would lose them on some
            # setups without a proper session backend).
            return redirect(url_for('billing.new_bill'))

        # One-time submission token to prevent refresh/back duplicate POST.
        session.pop('new_bill_submission_token', None)

        devotee_raw = (request.form.get('devotee_id') or '').strip()
        new_devotee_phone = (request.form.get('new_devotee_phone') or '').strip()
        new_devotee_house_name = (request.form.get('new_devotee_house_name') or '').strip()
        family_member_map = {}

        if devotee_raw.startswith('NEW::'):
            new_name = devotee_raw.replace('NEW::', '', 1).strip()

            devotee = Devotee(
                devotee_id=generate_devotee_id(),
                full_name=new_name,
                phone=new_devotee_phone,
                gotra=new_devotee_house_name,
                is_active=True
            )
            db.session.add(devotee)
            db.session.flush()
            devotee_id = devotee.id
        else:
            devotee_id = int(devotee_raw)
            devotee = Devotee.query.get(devotee_id)

        # Parse items from form (can have multiple poojas and retail items)
        items_data = []
        pooja_bookings=[]

        # Get all pooja items
        pooja_count = _safe_int(request.form.get('pooja_count'), 0)
        for i in range(pooja_count):
            service_id = request.form.get(f'pooja_service_{i}')
            if service_id:
                service = PoojaService.query.get(int(service_id))
                if not service:
                    continue
                pooja_devotee_name = (request.form.get(f'pooja_devotee_name_{i}') or '').strip()
                pooja_nakshathram = (request.form.get(f'pooja_nakshathram_{i}') or '').strip()
                pooja_date = (request.form.get(f'pooja_date_{i}') or '').strip()
                quantity = max(_safe_float(request.form.get(f'pooja_quantity_{i}'), 1), 1)
                if pooja_devotee_name:
                    key = pooja_devotee_name.lower()
                    if key not in family_member_map:
                        family_member_map[key] = {
                            'name': pooja_devotee_name,
                            'nakshathram': pooja_nakshathram
                        }
                    elif not family_member_map[key].get('nakshathram') and pooja_nakshathram:
                        family_member_map[key]['nakshathram'] = pooja_nakshathram
                custom_price = request.form.get(f'pooja_price_{i}')
                price_paise = int(_safe_float(custom_price)) if custom_price else service.default_price
                total_price = int(price_paise * quantity)

                item_name_parts = [service.display_name]
                if pooja_devotee_name:
                    item_name_parts.append(f'for {pooja_devotee_name}')
                if pooja_nakshathram:
                    item_name_parts.append(f'({pooja_nakshathram})')
                item_name = ' '.join(item_name_parts)

                items_data.append({
                    'type': 'POOJA',
                    'service_id': service.id,
                    'name': item_name,
                    'quantity': quantity,
                    'unit_price': price_paise,
                    'total_price': total_price,
                    'service': service
                })


        # Get all retail items
        retail_count = _safe_int(request.form.get('retail_count'), 0)
        for i in range(retail_count):
            item_id = request.form.get(f'retail_item_{i}')
            if item_id:
                item = InventoryItem.query.get(int(item_id))
                if not item:
                    continue
                quantity = _safe_float(request.form.get(f'retail_quantity_{i}'), 1)
                custom_price = request.form.get(f'retail_price_{i}')
                unit_price = int(_safe_float(custom_price)) if custom_price else item.selling_price
                total_price = int(unit_price * quantity)

                items_data.append({
                    'type': 'RETAIL',
                    'service_id': item.id,
                    'name': item.name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price,
                    'service': item
                })

        # Calculate totals
        subtotal = sum(item['total_price'] for item in items_data)

        # Parse discount
        discount_type = request.form.get('discount_type', 'amount')
        discount_value = _safe_float(request.form.get('discount_value'), 0)

        if discount_type == 'percent':
            discount_amount = int(subtotal * discount_value)
            discount_percent = discount_value
        else:
            discount_amount = int(discount_value)
            discount_percent = (discount_amount / subtotal) if subtotal > 0 else 0

        # Parse donation
        donation_rupees = int(_safe_float(request.form.get('donation'), 0))

        grand_total = subtotal - discount_amount + donation_rupees
        amount_paid = 0
        if request.form.get('payment_mode') != 'Credit':
            amount_paid = grand_total
        
        # Create bill
        bill = Bill(
            bill_number=generate_bill_number(),
            devotee_id=devotee_id,
            subtotal=subtotal,
            discount_amount=discount_amount,
            discount_percent=discount_percent,
            donation_amount=donation_rupees,
            grand_total=grand_total,
            amount_paid=amount_paid,
            payment_mode=request.form.get('payment_mode'),
            payment_reference=request.form.get('payment_reference'),
            created_by=current_user.id,
            notes=request.form.get('notes')
        )

        db.session.add(bill)
        db.session.flush()  # Get bill.id

        # Save pooja devotee names as family members for this devotee.
        if devotee:
            existing = parse_family_members(devotee.family_members)
            existing_map = {(x['name'] or '').strip().lower(): x for x in existing if (x.get('name') or '').strip()}
            for key, value in family_member_map.items():
                if key in existing_map:
                    if value.get('nakshathram'):
                        existing_map[key]['nakshathram'] = value['nakshathram']
                else:
                    existing_map[key] = {'name': value['name'], 'nakshathram': value.get('nakshathram', '')}
            devotee.family_members = dump_family_members(list(existing_map.values()))

        # Add bill items
        for item_data in items_data:
            bill_item = BillItem(
                bill_id=bill.id,
                item_type=item_data['type'],
                item_id=item_data['service_id'],
                item_name=item_data['name'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(bill_item)
            db.session.flush()
            # Update inventory for retail items
            if item_data['type'] == 'RETAIL':
                inventory = InventoryItem.query.get(item_data['service_id'])
                inventory.current_stock -= item_data['quantity']

                # Create stock transaction
                stock_txn = StockTransaction(
                    item_id=item_data['service_id'],
                    transaction_type='OUT',
                    quantity=item_data['quantity'],
                    reference_type='SALE',
                    reference_id=bill.id,
                    created_by=current_user.id
                )
                db.session.add(stock_txn)

            # Save Pooja Booking to datebase after bill is created to get the bill.id for reference
            
            # Add Pooja details to Pooja Booking for relavant poojas
            item_service = item_data.get('service')
            
            amount_paid = 0
            if request.form.get('payment_mode') != 'Credit':
                amount_paid = grand_total
            amount_paid = item_data['total_price'] if request.form.get('payment_mode') != 'Credit' else 0
            
            if item_data['type'] == 'POOJA' and item_service and item_service.add_to_booking:
                booking = PoojaBooking(
                    booking_number='temp',
                    bill_id=bill.id,
                    devotee_id=devotee_id,
                    service_id=item_data['service_id'],
                    scheduled_date=datetime.strptime(pooja_date, '%Y-%m-%d') if pooja_date else None,
                    booking_date=datetime.utcnow(),
                    special_instructions=bill.notes,
                    quantity=bill_item.quantity,
                    total_amount=bill_item.total_price,
                    amount_paid=amount_paid,
                    status='BOOKED',
                    created_by=current_user.id
                )
                db.session.add(booking)
                db.session.flush()
                booking.booking_number = f'PB-{datetime.utcnow():%Y%m%d}-{booking.id:03d}'
           
            db.session.commit()

        flash(f'Bill {bill.bill_number} created successfully!', 'success')
        return redirect(url_for('billing.view_bill', id=bill.id))
    
    # GET request - show billing form
    devotees = Devotee.query.filter_by(is_active=True).order_by(Devotee.full_name).all()
    poojas = PoojaService.query.filter_by(is_active=True).order_by(PoojaService.malayalam_name, PoojaService.name).all()
    retail_items = InventoryItem.query.filter_by(is_active=True).order_by(InventoryItem.name).all()

    # Build JSON-serializable copies for use in the template's <script> block.
    poojas_json = [
        {
            'id': p.id,
            'name': p.display_name,
            'english_name': p.english_name or '',
            'malayalam_name': p.malayalam_name or p.name,
            'default_price': int(p.default_price or 0),
        }
        for p in poojas
    ]
    retail_items_json = [
        {
            'id': r.id,
            'name': r.name,
            'selling_price': int(r.selling_price or 0),
            'current_stock': float(r.current_stock or 0),
        }
        for r in retail_items
    ]
    devotees_json = [
        {
            'id': d.id,
            'devotee_id': d.devotee_id,
            'full_name': d.full_name,
            'phone': d.phone or '',
            'nakshatra': d.nakshatra or '',
            'family_members': parse_family_members(d.family_members),
        }
        for d in devotees
    ]
    nakshathram_values = set(MALAYALAM_NAKSHATHRAS)
    for d in devotees:
        if (d.nakshatra or '').strip():
            nakshathram_values.add(d.nakshatra.strip())
        for fm in parse_family_members(d.family_members):
            if (fm.get('nakshathram') or '').strip():
                nakshathram_values.add(fm['nakshathram'].strip())

    def _naksh_sort_key(value):
        m = re.match(r'^\s*(\d+)', value or '')
        if m:
            return (0, int(m.group(1)), value)
        return (1, 999, value or '')

    nakshathrams_json = sorted(nakshathram_values, key=_naksh_sort_key)
    submission_token = str(uuid.uuid4())
    session['new_bill_submission_token'] = submission_token

    return render_template('billing/new_bill.html',
                         devotees=devotees,
                         poojas=poojas,
                         retail_items=retail_items,
                         poojas_json=poojas_json,
                         retail_items_json=retail_items_json,
                         devotees_json=devotees_json,
                         nakshathrams_json=nakshathrams_json,
                         submission_token=submission_token)


@bp.route('/create-from-booking/<int:booking_id>')
@login_required
def create_from_booking(booking_id):
    """Create bill from a completed booking"""
    booking = PoojaBooking.query.get_or_404(booking_id)
    
    if booking.bill:
        flash('Bill already created for this booking!', 'warning')
        return redirect(url_for('billing.view_bill', id=booking.bill.id))
    
    # Create bill
    bill = Bill(
        bill_number=generate_bill_number(),
        devotee_id=booking.devotee_id,
        subtotal=booking.total_amount,
        discount_amount=0,
        donation_amount=0,
        grand_total=booking.balance_amount,
        amount_paid=booking.amount_paid,
        payment_mode='Cash',  # Default, can be edited
        booking_id=booking.id,
        created_by=current_user.id,
        notes=f'From booking {booking.booking_number}'
    )
    
    db.session.add(bill)
    db.session.flush()
    
    # Add bill item
    bill_item = BillItem(
        bill_id=bill.id,
        item_type='POOJA',
        item_id=booking.service_id,
        item_name=booking.service.display_name,
        quantity=1,
        unit_price=booking.total_amount,
        total_price=booking.total_amount
    )
    db.session.add(bill_item)
    
    db.session.commit()
    
    flash(f'Bill {bill.bill_number} created from booking!', 'success')
    return redirect(url_for('billing.view_bill', id=bill.id))


@bp.route('/<int:id>')
@login_required
def view_bill(id):
    """View bill details"""
    bill = Bill.query.get_or_404(id)
    is_paid = bill.payment_mode == 'Credit' and bill.grand_total - bill.amount_paid == 0
    return render_template('billing/view_bill.html', bill=bill, is_paid=is_paid)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bill(id):
    """Edit a bill's master details and line items (uses same form as new_bill)"""
    bill = Bill.query.get_or_404(id)

    if request.method == 'POST':
        devotee_id_raw = (request.form.get('devotee_id') or '').strip()
        if not devotee_id_raw.isdigit():
            flash('Please select a valid devotee', 'warning')
            return redirect(url_for('billing.edit_bill', id=id))
        devotee = Devotee.query.get(int(devotee_id_raw))
        if not devotee:
            flash('Selected devotee not found', 'warning')
            return redirect(url_for('billing.edit_bill', id=id))

        bill.payment_mode = request.form.get('payment_mode')
        bill.payment_reference = request.form.get('payment_reference')
        bill.notes = request.form.get('notes')

        # Update bill items from form data
        items_data = []
        
        # Get all pooja items
        pooja_count = int(request.form.get('pooja_count', 0))
        for i in range(pooja_count):
            service_id = request.form.get(f'pooja_service_{i}')
            if service_id:
                service = PoojaService.query.get(int(service_id))
                if not service:
                    continue
                pooja_devotee_name = (request.form.get(f'pooja_devotee_name_{i}') or '').strip()
                pooja_nakshathram = (request.form.get(f'pooja_nakshathram_{i}') or '').strip()
                quantity = max(float(request.form.get(f'pooja_quantity_{i}', 1) or 1), 1)
                custom_price = request.form.get(f'pooja_price_{i}')
                price_paise = int(float(custom_price)) if custom_price else service.default_price
                total_price = int(price_paise * quantity)

                item_name_parts = [service.display_name]
                if pooja_devotee_name:
                    item_name_parts.append(f'for {pooja_devotee_name}')
                if pooja_nakshathram:
                    item_name_parts.append(f'({pooja_nakshathram})')
                item_name = ' '.join(item_name_parts)
                
                items_data.append({
                    'type': 'POOJA',
                    'id': service.id,
                    'name': item_name,
                    'quantity': quantity,
                    'unit_price': price_paise,
                    'total_price': total_price
                })
        
        # Get all retail items
        retail_count = int(request.form.get('retail_count', 0))
        for i in range(retail_count):
            item_id = request.form.get(f'retail_item_{i}')
            if item_id:
                item = InventoryItem.query.get(int(item_id))
                if not item:
                    continue
                quantity = float(request.form.get(f'retail_quantity_{i}', 1))
                custom_price = request.form.get(f'retail_price_{i}')
                unit_price = int(float(custom_price)) if custom_price else item.selling_price
                total_price = int(unit_price * quantity)
                
                items_data.append({
                    'type': 'RETAIL',
                    'id': item.id,
                    'name': item.name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price
                })
        
        if not items_data:
            flash('Please add at least one item to the bill', 'warning')
            return redirect(url_for('billing.edit_bill', id=id))
        
        # Delete old items
        BillItem.query.filter_by(bill_id=bill.id).delete()
        
        # Calculate totals
        subtotal = sum(item['total_price'] for item in items_data)
        
        # Parse discount
        discount_type = request.form.get('discount_type', 'amount')
        discount_value = float(request.form.get('discount_value', 0) or 0)
        
        if discount_type == 'percent':
            discount_amount = int(subtotal * discount_value )
            discount_percent = discount_value
        else:
            discount_amount = int(discount_value)
            discount_percent = (discount_amount / subtotal) if subtotal > 0 else 0
        
        # Parse donation
        donation_rupees = float(request.form.get('donation', 0) or 0)
        donation_paise = int(donation_rupees)
        
        bill.subtotal = subtotal
        bill.discount_amount = discount_amount
        bill.discount_percent = discount_percent
        bill.donation_amount = donation_paise
        bill.grand_total = subtotal - discount_amount + donation_paise
        
        # Add updated bill items
        for item_data in items_data:
            bill_item = BillItem(
                bill_id=bill.id,
                item_type=item_data['type'],
                item_id=item_data['id'],
                item_name=item_data['name'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(bill_item)

        db.session.commit()
        flash(f'Bill {bill.bill_number} updated successfully!', 'success')
        return redirect(url_for('billing.view_bill', id=bill.id))

    # GET request - render form with existing bill data
    devotees = Devotee.query.filter_by(is_active=True).order_by(Devotee.full_name).all()
    poojas = PoojaService.query.filter_by(is_active=True).order_by(PoojaService.malayalam_name).all()
    retail_items = InventoryItem.query.filter_by(is_active=True).order_by(InventoryItem.name).all()
    
    # Prepare JSON data for template
    poojas_json = json.dumps([{
        'id': p.id,
        'name': p.name,
        'malayalam_name': p.malayalam_name,
        'english_name': p.english_name,
        'display_name': p.display_name,
        'default_price': p.default_price
    } for p in poojas], ensure_ascii=False)
    
    retail_items_json = json.dumps([{
        'id': r.id,
        'name': r.name,
        'selling_price': r.selling_price
    } for r in retail_items], ensure_ascii=False)
    
    devotees_json = json.dumps([{
        'id': d.id,
        'devotee_id': d.devotee_id,
        'full_name': d.full_name,
        'phone': d.phone,
        'family_members': parse_family_members(d.family_members)
    } for d in devotees], ensure_ascii=False)
    
    nakshathrams_json = json.dumps(MALAYALAM_NAKSHATHRAS, ensure_ascii=False)
    
    # Convert bill items to edit format
    bill_json = json.dumps({
        'id': bill.id,
        'bill_number': bill.bill_number,
        'devotee_id': bill.devotee_id,
        'payment_mode': bill.payment_mode,
        'discount_type': 'percent' if bill.discount_percent > 0 else 'amount',
        'discount_value': bill.discount_percent if bill.discount_percent > 0 else bill.discount_amount ,
        'donation_amount': bill.donation_amount ,
        'payment_reference': bill.payment_reference,
        'notes': bill.notes,
        'items': [{
            'id': item.id,
            'type': item.item_type,
            'name': item.item_name,
            'quantity': item.quantity,
            'unit_price': item.unit_price ,
            'total_price': item.total_price 
        } for item in bill.items]
    }, ensure_ascii=False)
    
    return render_template('billing/new_bill.html', 
                           bill=bill,
                           bill_json=bill_json,
                           devotees=devotees,
                           poojas=poojas,
                           retail_items=retail_items,
                           poojas_json=poojas_json,
                           retail_items_json=retail_items_json,
                           devotees_json=devotees_json,
                           nakshathrams_json=nakshathrams_json)


@bp.route('/<int:id>/receipt')
@login_required
def print_receipt(id):
    """Generate printable receipt"""
    from flask import request
    bill = Bill.query.get_or_404(id)
    
    # Get printer type from query parameter or use default
    printer_type = request.args.get('printer_type', 'thermal')
    
    # Get temple settings
    from app.models import TempleSettings
    temple_name = TempleSettings.query.filter_by(key='temple_name').first()
    temple_address = TempleSettings.query.filter_by(key='temple_address').first()
    temple_phone = TempleSettings.query.filter_by(key='temple_phone').first()
    receipt_footer = TempleSettings.query.filter_by(key='receipt_footer').first()
    
    temple_name = temple_name.value if temple_name else 'Sri Venkateshwara Temple'
    temple_address = temple_address.value if temple_address else 'Temple Road, Temple City'
    temple_phone = temple_phone.value if temple_phone else '+91 1234567890'
    receipt_footer = receipt_footer.value if receipt_footer else 'May the divine bless you!'
    
    # Select appropriate template based on printer type
    if printer_type == 'dotmatrix6':
        template = 'billing/receipt_dotmatrix6.html'
    else:
        template = 'billing/receipt.html'
    
    html_content = render_template(template,
                                   bill=bill,
                                   temple_name=temple_name,
                                   temple_address=temple_address,
                                   temple_phone=temple_phone,
                                   receipt_footer=receipt_footer)
    
    return html_content


@bp.route('/<int:id>/receipt-pdf')
@login_required
def receipt_pdf(id):
    """Generate PDF receipt"""
    bill = Bill.query.get_or_404(id)
    
    from app.models import TempleSettings
    temple_name = TempleSettings.query.filter_by(key='temple_name').first()
    temple_address = TempleSettings.query.filter_by(key='temple_address').first()
    temple_phone = TempleSettings.query.filter_by(key='temple_phone').first()
    receipt_footer = TempleSettings.query.filter_by(key='receipt_footer').first()
    
    temple_name = temple_name.value if temple_name else 'Sri Venkateshwara Temple'
    temple_address = temple_address.value if temple_address else 'Temple Road, Temple City'
    temple_phone = temple_phone.value if temple_phone else '+91 1234567890'
    receipt_footer = receipt_footer.value if receipt_footer else 'May the divine bless you!'
    
    html_content = render_template('billing/receipt.html',
                                   bill=bill,
                                   temple_name=temple_name,
                                   temple_address=temple_address,
                                   temple_phone=temple_phone,
                                   receipt_footer=receipt_footer)
    
    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=receipt_{bill.bill_number}.pdf'
    
    return response


@bp.route('/<int:id>/whatsapp')
@login_required
def whatsapp_receipt(id):
    """Generate WhatsApp message link for receipt"""
    bill = Bill.query.get_or_404(id)
    
    if not bill.devotee.phone:
        flash('Devotee phone number not available!', 'warning')
        return redirect(url_for('billing.view_bill', id=id))
    
    # Clean phone number
    phone = bill.devotee.phone.replace('+', '').replace(' ', '').replace('-', '')
    
    # Create message
    message = f'''🙏 *{bill.devotee.full_name}*

Bill No: {bill.bill_number}
Date: {bill.bill_date.strftime('%d-%b-%Y %I:%M %p')}

*Items:*
'''
    
    for item in bill.items:
        price = item.total_price 
        message += f'• {item.item_name}: ₹{price:.2f}\n'
    
    subtotal = bill.subtotal 
    discount = bill.discount_amount 
    donation = bill.donation_amount 
    total = bill.grand_total 
    
    message += f'\n*Subtotal:* ₹{subtotal:.2f}'
    
    if bill.discount_amount > 0:
        message += f'\n*Discount:* -₹{discount:.2f}'
    
    if bill.donation_amount > 0:
        message += f'\n*Donation:* ₹{donation:.2f}'
    
    message += f'\n*Grand Total:* ₹{total:.2f}'
    message += f'\n*Payment:* {bill.payment_mode}'
    
    message += '\n\n🕉️ May the divine bless you!'
    
    # Create WhatsApp URL
    import urllib.parse
    wa_url = f'https://wa.me/{phone}?text={urllib.parse.quote(message)}'
    
    return redirect(wa_url)


@bp.route('/list')
@login_required
def list_bills():
    """List all bills"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Bill.query.filter_by(is_active=True)
    
    if search:
        search_pattern = f'%{search}%'
        query = query.join(Devotee).filter(
            db.or_(
                Bill.bill_number.ilike(search_pattern),
                Devotee.full_name.ilike(search_pattern),
                Devotee.phone.ilike(search_pattern)
            )
        )
    
    bills = query.order_by(Bill.bill_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('billing/list_bills.html', bills=bills, search=search)
