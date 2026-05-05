from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import PoojaService, ServiceMaterial, InventoryItem, PoojaBooking, Devotee, Bill, BillItem
from datetime import datetime, date, timedelta

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
    
    query = PoojaService.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    if search:
        pattern = f'%{search}%'
        query = query.filter(PoojaService.english_name.ilike(pattern))
    
    services = query.order_by(PoojaService.malayalam_name, PoojaService.name).all()
    
    categories = db.session.query(PoojaService.category).filter(
        PoojaService.is_active == True
    ).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('poojas/services_list.html', 
                         services=services, 
                         categories=categories,
                         selected_category=category,
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
        price_paise = int(price_rupees * 100)
        
        service = PoojaService(
            english_name=request.form.get('english_name'),
            malayalam_name=request.form.get('malayalam_name'),
            name=request.form.get('malayalam_name') or request.form.get('english_name'),
            category=request.form.get('category'),
            description=request.form.get('description'),
            default_price=price_paise,
            duration_minutes=int(request.form.get('duration_minutes', 30)),
            max_bookings_per_day=int(request.form.get('max_bookings_per_day', 10)),
            requires_priest=request.form.get('requires_priest') == 'on'
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
        price_paise = int(price_rupees * 100)
        
        service.english_name = request.form.get('english_name')
        service.malayalam_name = request.form.get('malayalam_name')
        service.name = request.form.get('malayalam_name') or request.form.get('english_name')
        service.category = request.form.get('category')
        service.description = request.form.get('description')
        service.default_price = price_paise
        service.duration_minutes = int(request.form.get('duration_minutes', 30))
        service.max_bookings_per_day = int(request.form.get('max_bookings_per_day', 10))
        service.requires_priest = request.form.get('requires_priest') == 'on'
        service.is_active = request.form.get('is_active') == 'on'
        
        db.session.commit()
        
        flash('Pooja service updated successfully!', 'success')
        return redirect(url_for('poojas.services_list'))
    
    in_use, usage_counts = _service_in_use(service.id)
    return render_template('poojas/services_edit.html', service=service, in_use=in_use, usage_counts=usage_counts)


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
        devotee_id = int(request.form.get('devotee_id'))
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
        advance_rupees = float(request.form.get('advance_paid', 0) or 0)
        advance_paise = int(advance_rupees * 100)
        
        # Get custom price or use default
        custom_price = request.form.get('custom_price')
        if custom_price:
            total_paise = int(float(custom_price) * 100)
        else:
            total_paise = service.default_price
        
        balance_paise = total_paise - advance_paise
        
        booking = PoojaBooking(
            booking_number=generate_booking_number(),
            devotee_id=devotee_id,
            service_id=service_id,
            scheduled_date=scheduled_date,
            special_instructions=request.form.get('special_instructions'),
            advance_paid=advance_paise,
            total_amount=total_paise,
            balance_amount=balance_paise,
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
def bookings_complete(id):
    """Mark booking as completed and optionally generate bill"""
    booking = PoojaBooking.query.get_or_404(id)
    
    if booking.status == 'COMPLETED':
        flash('This booking is already completed!', 'warning')
        return redirect(url_for('poojas.bookings_view', id=id))
    
    booking.status = 'COMPLETED'
    booking.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Booking marked as completed!', 'success')
    
    # Ask if they want to generate bill
    generate_bill = request.form.get('generate_bill')
    if generate_bill == 'yes':
        return redirect(url_for('billing.create_from_booking', booking_id=booking.id))
    
    return redirect(url_for('poojas.bookings_view', id=id))


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
