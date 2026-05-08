from email import errors

from flask import Blueprint, json, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import form
from app import db
from app.models import PoojaService, ServiceMaterial, InventoryItem, PoojaBooking, Devotee, Bill, BillItem
from datetime import datetime, date, timedelta

from app.routes.devotees import generate_devotee_id
from app.utils.json_util import json_response

bp = Blueprint('poojas', __name__, url_prefix='/poojas')


def _service_usage_counts(service_id):
    return {
        'bookings': PoojaBooking.query.filter_by(service_id=service_id).count(),
        'bill_items': BillItem.query.filter_by(item_type='POOJA', item_id=service_id).count(),
        'materials': ServiceMaterial.query.filter_by(service_id=service_id).count(),
    }


def _service_in_use(service_id):
    counts = _service_usage_counts(service_id)
    return (counts['bookings'] > 0) or (counts['bill_items'] > 0), counts


# ==================== POOJA SERVICES MANAGEMENT ====================

@bp.route('/services')
@login_required
def services_list():
    """List all pooja services"""
    category = request.args.get('category', '')
    search = (request.args.get('search', '') or '').strip()
    
    # Show all services (both active and inactive) for grid management
    query = PoojaService.query
    
    if category:
        query = query.filter_by(category=category)
    if search:
        pattern = f'%{search}%'
        query = query.filter(PoojaService.english_name.ilike(pattern))
    
    services = query.order_by(PoojaService.id).all()
    jsonServ = json_response(services)

    categories = db.session.query(PoojaService.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('poojas/services_list.html', 
                         services=json_response(services).get_json(),
                         categories=json_response(categories).get_json(),
                         selected_category=json_response(category).get_json(),
                         search=search)


@bp.route('/services/add', methods=['GET', 'POST'])
@login_required
def services_add():
    """Add new pooja service"""
    if current_user.role not in ['admin']:
        flash('Only admins can add pooja services', 'danger')
        return redirect(url_for('poojas.services_list'))
    
    if request.method == 'POST':
        # Convert rupees to paise
        price_rupees = float(request.form.get('default_price', 0))
        
        service = PoojaService(
            english_name=request.form.get('english_name'),
            malayalam_name=request.form.get('malayalam_name'),
            name=request.form.get('malayalam_name') or request.form.get('english_name'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            default_price=price_rupees,
            duration_minutes=int(request.form.get('duration_minutes', 30)),
            max_bookings_per_day=int(request.form.get('max_bookings_per_day', 10)),
            add_to_booking=request.form.get('add_to_booking') == 'on'
        )
        
        db.session.add(service)
        db.session.commit()
        
        flash(f'Pooja service "{service.display_name}" added successfully!', 'success')
        return redirect(url_for('poojas.services_list'))
    
    return render_template('poojas/services_add.html')


@bp.route('/services/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def services_edit(id):
    """Edit pooja service"""
    if current_user.role not in ['admin']:
        flash('Only admins can edit pooja services', 'danger')
        return redirect(url_for('poojas.services_list'))
    
    service = PoojaService.query.get_or_404(id)
    
    if request.method == 'POST':
        price_rupees = float(request.form.get('default_price', 0))
        
        service.english_name = request.form.get('english_name')
        service.malayalam_name = request.form.get('malayalam_name')
        service.name = request.form.get('malayalam_name') or request.form.get('english_name')
        service.category = request.form.get('category')
        service.description = request.form.get('description')
        service.default_price = price_rupees
        service.duration_minutes = int(request.form.get('duration_minutes', 30))
        service.max_bookings_per_day = int(request.form.get('max_bookings_per_day', 10))
        service.add_to_booking = request.form.get('add_to_booking') == 'on'
        service.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        
        flash('Pooja service updated successfully!', 'success')
        return redirect(url_for('poojas.services_list'))
    
    in_use, usage_counts = _service_in_use(service.id)
    return render_template('poojas/services_edit.html', service=service, in_use=in_use, usage_counts=usage_counts)


@bp.route('/services/update-batch', methods=['POST'])
@login_required
def services_update_batch():
    """Batch update services from Ag-Grid"""
    if current_user.role not in ['admin']:
        return jsonify({'success': False, 'message': 'Only admins can update services'}), 403
    
    try:
        data = request.get_json()
        services_data = data.get('services', [])
        modified_ids = data.get('modified_ids', [])
        
        for service_data in services_data:
            service_id = service_data.get('id')
            
            # For new rows (id is None), create a new service
            if service_id is None:
                if service_data.get('english_name') or service_data.get('malayalam_name'):
                    new_service = PoojaService(
                        english_name=service_data.get('english_name', ''),
                        malayalam_name=service_data.get('malayalam_name', ''),
                        name=service_data.get('malayalam_name') or service_data.get('english_name'),
                        category=service_data.get('category', ''),
                        default_price=float(service_data.get('default_price', 0)),
                        duration_minutes=int(service_data.get('duration_minutes', 30)),
                        max_bookings_per_day=int(service_data.get('max_bookings_per_day', 10)),
                        add_to_booking=service_data.get('add_to_booking', True),
                        is_active=service_data.get('is_active', True)
                    )
                    db.session.add(new_service)
            else:
                # Update existing service
                service = PoojaService.query.get(service_id)
                if service and service_id in modified_ids:
                    service.english_name = service_data.get('english_name', service.english_name)
                    service.malayalam_name = service_data.get('malayalam_name', service.malayalam_name)
                    service.name = service_data.get('malayalam_name') or service_data.get('english_name') or service.name
                    service.category = service_data.get('category', service.category)
                    service.default_price = float(service_data.get('default_price', service.default_price))
                    service.duration_minutes = int(service_data.get('duration_minutes', service.duration_minutes))
                    service.max_bookings_per_day = int(service_data.get('max_bookings_per_day', service.max_bookings_per_day))
                    service.add_to_booking = service_data.get('add_to_booking', service.add_to_booking)
                    service.is_active = service_data.get('is_active', service.is_active)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Services updated successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400


@bp.route('/services/<int:id>/disable', methods=['POST'], endpoint='services_disable')
@login_required
def services_disable(id):
    """Disable pooja service"""
    if current_user.role not in ['admin']:
        flash('Only admins can disable pooja services', 'danger')
        return redirect(url_for('poojas.services_list'))

    service = PoojaService.query.get_or_404(id)
    service.is_active = False
    db.session.commit()
    flash('Pooja service disabled successfully!', 'success')
    return redirect(url_for('poojas.services_edit', id=id))


@bp.route('/services/<int:id>/delete', methods=['POST'])
@login_required
def services_delete(id):
    """Delete pooja service when unused; otherwise disable with warning"""
    if current_user.role not in ['admin']:
        flash('Only admins can delete pooja services', 'danger')
        return redirect(url_for('poojas.services_list'))
    
    service = PoojaService.query.get_or_404(id)
    mode = (request.form.get('mode') or '').strip().lower()
    if mode == 'disable':
        service.is_active = False
        db.session.commit()
        flash('Pooja service disabled successfully!', 'success')
        return redirect(url_for('poojas.services_edit', id=id))

    in_use, usage_counts = _service_in_use(service.id)
    if in_use:
        service.is_active = False
        db.session.commit()
        flash(
            f'This service is already in use (Bookings: {usage_counts["bookings"]}, Bills: {usage_counts["bill_items"]}). '
            f'It cannot be deleted and has been disabled instead.',
            'warning'
        )
        return redirect(url_for('poojas.services_edit', id=id))

    # Safe hard delete only when not used in bookings/bills.
    db.session.delete(service)
    db.session.commit()
    flash('Pooja service deleted successfully!', 'success')
    return redirect(url_for('poojas.services_list'))


# ==================== POOJA BOOKINGS ====================

def generate_booking_number():
    """Generate unique booking number"""
    year = datetime.now().year
    last_booking = PoojaBooking.query.filter(
        PoojaBooking.booking_number.like(f'BOOK-{year}-%')
    ).order_by(PoojaBooking.id.desc()).first()
    
    if last_booking:
        last_num = int(last_booking.booking_number.split('-')[2])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f'BOOK-{year}-{new_num:05d}'


@bp.route('/bookings')
@login_required
def bookings_list():
    """List all pooja bookings"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    date_filter = request.args.get('date', '')
    
    query = PoojaBooking.query.filter_by(is_active=True)
    
    if status:
        query = query.filter_by(status=status)
    
    if date_filter:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
        query = query.filter_by(scheduled_date=filter_date)
    
    bookings = query.order_by(PoojaBooking.scheduled_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('poojas/bookings_list.html', 
                         bookings=bookings,
                         status_filter=status,
                         date_filter=date_filter)


@bp.route('/bookings/add', methods=['GET', 'POST'])
@login_required
def bookings_add():
    """Add new pooja booking"""
    if request.method == 'POST':
        
        errors = []        
        # --- 1. Devotee validation ---
        devotee_raw = (request.form.get('devotee_id') or '').strip()
        if not devotee_raw:
            errors.append('Please select a devotee or enter a new devotee name.')
        elif devotee_raw.startswith('NEW::'):
            new_name = devotee_raw.replace('NEW::', '', 1).strip()
            if not new_name:
                errors.append('New devotee name cannot be empty.')
            new_phone = (request.form.get('new_devotee_phone') or '').strip()
            if not new_phone:
                errors.append('Phone number is required for a new devotee.')
        if errors:
            for err in errors:
                flash(err, 'danger')
            # Re-render the form instead of redirecting so flash messages
            # are visible immediately (redirect would lose them on some
            # setups without a proper session backend).
            return redirect(url_for('poojas.bookings_add'))
        
        if devotee_raw.startswith('NEW::'):
            new_name = devotee_raw.replace('NEW::', '', 1).strip()
            new_devotee_phone = (request.form.get('new_devotee_phone') or '').strip()
            new_devotee_house_name = (request.form.get('new_devotee_house_name') or '').strip()
       

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
        
        service_id = int(request.form.get('service_id'))
        service = PoojaService.query.get(service_id)
        
        scheduled_date = datetime.strptime(request.form.get('scheduled_date'), '%Y-%m-%d').date()
        
        # Check daily availability
        existing_bookings = PoojaBooking.query.filter_by(
            service_id=service_id,
            scheduled_date=scheduled_date,
            is_active=True
        ).filter(PoojaBooking.status.in_(['BOOKED', 'CONFIRMED'])).count()

        if existing_bookings >= service.max_bookings_per_day:
            flash('This day is fully booked for the selected service.', 'warning')
            return redirect(url_for('poojas.bookings_add'))
        
        # Parse advance payment
        advance_rupees = float(request.form.get('amount_paid', 0) or 0)
        
        # Get custom price or use default
        custom_price = request.form.get('custom_price')
        if custom_price:
            total = int(float(custom_price))
        else:
            total = service.default_price
        
        balance = total - advance_rupees
        
        booking = PoojaBooking(
            booking_number=generate_booking_number(),
            devotee_id=devotee_id,
            service_id=service_id,
            scheduled_date=scheduled_date,
            special_instructions=request.form.get('special_instructions'),
            amount_paid=advance_rupees,
            total_amount=total,
            balance_amount=balance,
            status='BOOKED',
            created_by=current_user.id
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash(f'Pooja booking {booking.booking_number} created successfully!', 'success')
        return redirect(url_for('poojas.bookings_view', id=booking.id))
    
    # GET request
    devotees = Devotee.query.filter_by(is_active=True).order_by(Devotee.full_name).all()
    services = PoojaService.query.filter_by(is_active=True).order_by(PoojaService.malayalam_name, PoojaService.name).all()
    return render_template('poojas/bookings_add.html',
                         devotees=devotees,
                         services=services)


@bp.route('/bookings/<int:id>')
@login_required
def bookings_view(id):
    """View booking details"""
    booking = PoojaBooking.query.get_or_404(id)
    return render_template('poojas/bookings_view.html', booking=booking)


@bp.route('/bookings/<int:id>/complete', methods=['POST'])
@login_required
def bookings_complete(id, payment_mode=None):
    """Mark booking as completed and optionally generate bill"""
    booking = PoojaBooking.query.get_or_404(id)
    
    if booking.status == 'COMPLETED':
        flash('This booking is already completed!', 'warning')
        return redirect(url_for('poojas.bookings_view', id=id))
    
    if booking.bill and booking.bill.payment_mode == 'Credit':
        booking.bill.payment_mode = payment_mode or 'Cash'  # Force mark as paid if credit
        booking.bill.payment_reference = f'Marked paid on completion of booking {booking.booking_number}'
        db.session.commit()
        flash('This booking was unpaid. It has now been marked as paid.', 'success')
    
    booking.status = 'COMPLETED'
    booking.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Booking marked as completed!', 'success')
    
    # Ask if they want to generate bill
    generate_bill = request.form.get('generate_bill')
    if generate_bill == 'yes':
        return redirect(url_for('billing.create_from_booking', booking_id=booking.id))
    
    return redirect(url_for('poojas.bookings_view', id=id))

@bp.route('/bookings/<int:id>/complete-only', methods=['POST'])
@login_required
def bookings_complete_only(id):
    """Mark booking as completed (no billing redirect)"""

    booking = PoojaBooking.query.get_or_404(id)

    if booking.status == 'COMPLETED':
        flash('This booking is already completed!', 'warning')

    if booking.bill and booking.bill.payment_mode == 'Credit':
        flash('This booking is unpaid. Please complete the payment first.', 'error')
        return redirect(url_for('poojas.bookings_view', id=id))
    
    booking.status = 'COMPLETED'
    booking.completed_at = datetime.utcnow()

    db.session.commit()

    flash('Booking marked as completed successfully!', 'success')

    return redirect(url_for('dashboard.index'))

@bp.route('/bookings/<int:id>/cancel', methods=['POST'])
@login_required
def bookings_cancel(id):
    """Cancel a booking"""
    booking = PoojaBooking.query.get_or_404(id)
    
    if booking.status in ['COMPLETED', 'CANCELLED']:
        flash('Cannot cancel this booking!', 'warning')
        return redirect(url_for('poojas.bookings_view', id=id))
    
    booking.status = 'CANCELLED'
    db.session.commit()
    
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('poojas.bookings_view', id=id))


@bp.route('/calendar')
@login_required
def calendar():
    """Calendar view of bookings"""
    # Get current month or specified month
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    # Get all bookings for this month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    bookings = PoojaBooking.query.filter(
        PoojaBooking.scheduled_date >= start_date,
        PoojaBooking.scheduled_date < end_date,
        PoojaBooking.is_active == True
    ).order_by(PoojaBooking.scheduled_date).all()

    # Group bookings by date
    bookings_by_date = {}
    for booking in bookings:
        date_key = booking.scheduled_date.strftime('%Y-%m-%d')
        if date_key not in bookings_by_date:
            bookings_by_date[date_key] = []
        bookings_by_date[date_key].append(booking)

    return render_template('poojas/calendar.html',
                         year=year,
                         month=month,
                         bookings_by_date=bookings_by_date)


@bp.route('/api/list')
@login_required
def api_services_list():
    """API endpoint to get all active pooja services"""
    services = PoojaService.query.filter_by(is_active=True).order_by(PoojaService.malayalam_name, PoojaService.name).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'english_name': s.english_name,
        'malayalam_name': s.malayalam_name,
        'display_name': s.display_name,
        'default_price': s.default_price,
        'category': s.category
    } for s in services])
