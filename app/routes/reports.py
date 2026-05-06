from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from app import db
from app.models import Bill, BillItem, PoojaBooking, InventoryItem, StockTransaction, Devotee
from sqlalchemy import func
from datetime import datetime, date, timedelta
import csv
import io

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('/')
@login_required
def index():
    """Reports dashboard"""
    return render_template('reports/index.html')


@bp.route('/collection', methods=['GET', 'POST'])
@login_required
def collection_report():
    """Collection report by date range"""
    # Default to today
    today = date.today()
    start_date = request.args.get('start_date', today.strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    end_dt = datetime.combine(end_dt.date(), datetime.max.time())
    
    # Get bills in date range
    bills = Bill.query.filter(
        Bill.bill_date >= start_dt,
        Bill.bill_date <= end_dt,
        Bill.is_active == True
    ).order_by(Bill.bill_date.desc()).all()
    
    # Calculate totals
    total_collection = sum(bill.grand_total for bill in bills)
    total_discount = sum(bill.discount_amount for bill in bills)
    total_donation = sum(bill.donation_amount for bill in bills)
    
    # Payment mode breakdown
    payment_breakdown = db.session.query(
        Bill.payment_mode,
        func.sum(Bill.grand_total).label('total'),
        func.count(Bill.id).label('count')
    ).filter(
        Bill.bill_date >= start_dt,
        Bill.bill_date <= end_dt,
        Bill.is_active == True
    ).group_by(Bill.payment_mode).all()
    
    # Daily breakdown
    daily_breakdown = db.session.query(
        func.date(Bill.bill_date).label('date'),
        func.sum(Bill.grand_total).label('total'),
        func.count(Bill.id).label('count')
    ).filter(
        Bill.bill_date >= start_dt,
        Bill.bill_date <= end_dt,
        Bill.is_active == True
    ).group_by(func.date(Bill.bill_date)).all()
    
    return render_template('reports/collection_report.html',
                         bills=bills,
                         start_date=start_date,
                         end_date=end_date,
                         total_collection=total_collection,
                         total_discount=total_discount,
                         total_donation=total_donation,
                         payment_breakdown=payment_breakdown,
                         daily_breakdown=daily_breakdown)


@bp.route('/pooja-wise', methods=['GET', 'POST'])
@login_required
def pooja_wise_report():
    """Pooja-wise revenue report"""
    today = date.today()
    start_date = request.args.get('start_date', today.strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    end_dt = datetime.combine(end_dt.date(), datetime.max.time())
    
    # Pooja-wise breakdown
    pooja_stats = db.session.query(
        BillItem.item_name,
        func.sum(BillItem.total_price).label('revenue'),
        func.count(BillItem.id).label('count')
    ).join(Bill).filter(
        Bill.bill_date >= start_dt,
        Bill.bill_date <= end_dt,
        Bill.is_active == True,
        BillItem.item_type == 'POOJA'
    ).group_by(BillItem.item_name).order_by(func.sum(BillItem.total_price).desc()).all()
    
    total_revenue = sum(stat.revenue for stat in pooja_stats)
    total_count = sum(stat.count for stat in pooja_stats)
    
    return render_template('reports/pooja_wise_report.html',
                         pooja_stats=pooja_stats,
                         start_date=start_date,
                         end_date=end_date,
                         total_revenue=total_revenue,
                         total_count=total_count)


@bp.route('/devotee-wise', methods=['GET', 'POST'])
@login_required
def devotee_wise_report():
    """Devotee-wise billing history"""
    today = date.today()
    start_date = request.args.get('start_date', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    end_dt = datetime.combine(end_dt.date(), datetime.max.time())
    
    # Devotee-wise breakdown
    devotee_stats = db.session.query(
        Devotee.id,
        Devotee.devotee_id,
        Devotee.full_name,
        Devotee.phone,
        func.sum(Bill.grand_total).label('total_spent'),
        func.count(Bill.id).label('visit_count')
    ).join(Bill).filter(
        Bill.bill_date >= start_dt,
        Bill.bill_date <= end_dt,
        Bill.is_active == True
    ).group_by(Devotee.id).order_by(func.sum(Bill.grand_total).desc()).limit(100).all()
    
    return render_template('reports/devotee_wise_report.html',
                         devotee_stats=devotee_stats,
                         start_date=start_date,
                         end_date=end_date)


@bp.route('/inventory-consumption', methods=['GET', 'POST'])
@login_required
def inventory_consumption_report():
    """Inventory consumption report"""
    today = date.today()
    start_date = request.args.get('start_date', (today - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    end_dt = datetime.combine(end_dt.date(), datetime.max.time())
    
    # Get all stock transactions
    transactions = db.session.query(
        InventoryItem.name,
        InventoryItem.unit,
        func.sum(func.case(
            (StockTransaction.transaction_type == 'IN', StockTransaction.quantity),
            else_=0
        )).label('stock_in'),
        func.sum(func.case(
            (StockTransaction.transaction_type == 'OUT', StockTransaction.quantity),
            else_=0
        )).label('stock_out')
    ).join(StockTransaction).filter(
        StockTransaction.created_at >= start_dt,
        StockTransaction.created_at <= end_dt
    ).group_by(InventoryItem.id).all()
    
    return render_template('reports/inventory_consumption_report.html',
                         transactions=transactions,
                         start_date=start_date,
                         end_date=end_date)


@bp.route('/priest-wise', methods=['GET', 'POST'])
@login_required
def priest_wise_report():
    """Priest-wise pooja count report"""
    today = date.today()
    start_date = request.args.get('start_date', today.strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    from app.models import Priest
    
    # Priest-wise stats
    priest_stats = db.session.query(
        Priest.id,
        Priest.name,
        func.count(PoojaBooking.id).label('booking_count'),
        func.sum(PoojaBooking.total_amount).label('total_revenue')
    ).join(PoojaBooking).filter(
        PoojaBooking.scheduled_date >= start_dt.date(),
        PoojaBooking.scheduled_date <= end_dt.date(),
        PoojaBooking.is_active == True
    ).group_by(Priest.id).all()
    
    return render_template('reports/priest_wise_report.html',
                         priest_stats=priest_stats,
                         start_date=start_date,
                         end_date=end_date)


@bp.route('/export-csv/<report_type>')
@login_required
def export_csv(report_type):
    """Export report to CSV"""
    today = date.today()
    start_date = request.args.get('start_date', today.strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    end_dt = datetime.combine(end_dt.date(), datetime.max.time())
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == 'collection':
        bills = Bill.query.filter(
            Bill.bill_date >= start_dt,
            Bill.bill_date <= end_dt,
            Bill.is_active == True
        ).order_by(Bill.bill_date.desc()).all()
        
        # Write header
        writer.writerow(['Bill Number', 'Date', 'Devotee', 'Subtotal (₹)', 'Discount (₹)', 
                        'Donation (₹)', 'Total (₹)', 'Payment Mode'])
        
        # Write data
        for bill in bills:
            writer.writerow([
                bill.bill_number,
                bill.bill_date.strftime('%d-%b-%Y %I:%M %p'),
                bill.devotee.full_name,
                bill.subtotal ,
                bill.discount_amount ,
                bill.donation_amount ,
                bill.grand_total ,
                bill.payment_mode
            ])
    
    elif report_type == 'pooja_wise':
        pooja_stats = db.session.query(
            BillItem.item_name,
            func.sum(BillItem.total_price).label('revenue'),
            func.count(BillItem.id).label('count')
        ).join(Bill).filter(
            Bill.bill_date >= start_dt,
            Bill.bill_date <= end_dt,
            Bill.is_active == True,
            BillItem.item_type == 'POOJA'
        ).group_by(BillItem.item_name).order_by(func.sum(BillItem.total_price).desc()).all()
        
        writer.writerow(['Pooja Name', 'Count', 'Revenue (₹)'])
        
        for stat in pooja_stats:
            writer.writerow([
                stat.item_name,
                stat.count,
                stat.revenue 
            ])
    
    # Prepare response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report_{start_date}_to_{end_date}.csv'
    
    return response
