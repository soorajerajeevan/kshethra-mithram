from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Bill, PoojaBooking, InventoryItem, BillItem, PoojaService
from sqlalchemy import func
from datetime import datetime, date, timedelta

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    """Main dashboard with today's summary"""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    # Today's collection stats
    today_bills = Bill.query.filter(
        Bill.bill_date >= today_start,
        Bill.bill_date <= today_end,
        Bill.is_active == True
    ).all()
    
    total_collection = sum(bill.grand_total for bill in today_bills)
    bills_count = len(today_bills)
    
    # Payment mode breakdown
    cash_total = sum(bill.grand_total for bill in today_bills if bill.payment_mode == 'Cash')
    upi_total = sum(bill.grand_total for bill in today_bills if bill.payment_mode == 'UPI')
    card_total = sum(bill.grand_total for bill in today_bills if bill.payment_mode == 'Card')
    dd_total = sum(bill.grand_total for bill in today_bills if bill.payment_mode == 'DD')
    
    # Today's bookings
    today_bookings = PoojaBooking.query.filter(
        PoojaBooking.scheduled_date == today,
        PoojaBooking.is_active == True
    ).all()
    
    pending_bookings = [b for b in today_bookings if b.status in ['BOOKED', 'CONFIRMED']]
    completed_bookings = [b for b in today_bookings if b.status == 'COMPLETED']
    
    # Top 5 poojas by revenue today
    top_poojas = db.session.query(
        BillItem.item_name,
        func.sum(BillItem.total_price).label('revenue'),
        func.count(BillItem.id).label('count')
    ).join(Bill).filter(
        Bill.bill_date >= today_start,
        Bill.bill_date <= today_end,
        Bill.is_active == True,
        BillItem.item_type == 'POOJA'
    ).group_by(BillItem.item_name).order_by(func.sum(BillItem.total_price).desc()).limit(5).all()
    
    # Low stock alerts
    low_stock_items = InventoryItem.query.filter(
        InventoryItem.current_stock <= InventoryItem.reorder_level,
        InventoryItem.is_active == True
    ).order_by(InventoryItem.current_stock).limit(10).all()
    
    # Upcoming bookings (next 7 days)
    week_end = today + timedelta(days=7)
    upcoming_bookings = PoojaBooking.query.filter(
        PoojaBooking.scheduled_date > today,
        PoojaBooking.scheduled_date <= week_end,
        PoojaBooking.status.in_(['BOOKED', 'CONFIRMED']),
        PoojaBooking.is_active == True
    ).order_by(PoojaBooking.scheduled_date).limit(10).all()
    
    # Recent bills (last 10)
    recent_bills = Bill.query.filter(
        Bill.is_active == True
    ).order_by(Bill.bill_date.desc()).limit(10).all()
    
    return render_template('dashboard/index.html',
                         total_collection=total_collection,
                         bills_count=bills_count,
                         cash_total=cash_total,
                         upi_total=upi_total,
                         card_total=card_total,
                         dd_total=dd_total,
                         today_bookings_count=len(today_bookings),
                         pending_bookings=pending_bookings,
                         completed_bookings=completed_bookings,
                         top_poojas=top_poojas,
                         low_stock_items=low_stock_items,
                         upcoming_bookings=upcoming_bookings,
                         recent_bills=recent_bills,
                         today=today)
