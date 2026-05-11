from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Devotee, Bill
from datetime import datetime
import re
import json

from app.routes.billing import MALAYALAM_NAKSHATHRAS

bp = Blueprint('devotees', __name__, url_prefix='/devotees')


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



@bp.route('/')
@login_required
def list():
    """List all devotees with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Devotee.query.filter_by(is_active=True)
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Devotee.devotee_id.ilike(search_pattern),
                Devotee.full_name.ilike(search_pattern),
                Devotee.phone.ilike(search_pattern)
            )
        )
    
    devotees = query.order_by(Devotee.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('devotees/list.html', devotees=devotees, search=search)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new devotee"""
    if request.method == 'POST':
        devotee = Devotee(
            devotee_id=generate_devotee_id(),
            full_name=request.form.get('full_name'),
            nakshatra=request.form.get('nakshatra'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            gotra=request.form.get('gotra'),
            family_members=request.form.get('family_members')
        )
        
        db.session.add(devotee)
        db.session.commit()
        
        flash(f'Devotee {devotee.devotee_id} added successfully!', 'success')
        return redirect(url_for('devotees.view', id=devotee.id))
    
    return render_template('devotees/add.html')


@bp.route('/<int:id>')
@login_required
def view(id):
    """View devotee details and billing history"""
    devotee = Devotee.query.get_or_404(id)
    
    # Get billing history
    bills = Bill.query.filter_by(
        devotee_id=devotee.id
    ).order_by(Bill.bill_date.desc()).limit(20).all()
    
    total_spent = sum(bill.grand_total for bill in devotee.bills.filter_by(is_active=True).all())
    
    return render_template('devotees/view.html', 
                         devotee=devotee, 
                         bills=bills,
                         total_spent=total_spent)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit devotee details"""
    devotee = Devotee.query.get_or_404(id)
    
    if request.method == 'POST':
        devotee.full_name = request.form.get('full_name')
        devotee.nakshatra = request.form.get('nakshatra')
        devotee.phone = request.form.get('phone')
        devotee.email = request.form.get('email')
        devotee.address = request.form.get('address')
        devotee.gotra = request.form.get('gotra')
        devotee.updated_at = datetime.utcnow()
        
        db.session.commit()
        db.flush()
        
        #Update family members in db, if any changes, create a new record in family members table with the updated details and link it to the devotee if not exist. 
        # family member is in format [{name: '', nakshathram: '' }]
        family_members = request.form.get('family_members')
        if family_members:
            try:
                family_members = json.loads(family_members)
                devotee.family_members = family_members
                db.session.commit()
            except Exception as e:
                flash('Error updating family members: ' + str(e), 'danger')
                return redirect(url_for('devotees.edit', id=devotee.id))
        
        flash('Devotee updated successfully!', 'success')
        return redirect(url_for('devotees.view', id=devotee.id))
    
    return render_template('devotees/edit.html', devotee=devotee)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete devotee"""
    if current_user.role != 'admin':
        flash('Only admins can delete devotees', 'danger')
        return redirect(url_for('devotees.list'))
    
    devotee = Devotee.query.get_or_404(id)
    devotee.is_active = False
    db.session.commit()
    
    flash('Devotee deactivated successfully!', 'success')
    return redirect(url_for('devotees.list'))


@bp.route('/search-api')
@login_required
def search_api():
    """API endpoint for devotee search (for autocomplete)"""
    term = request.args.get('term', '')
    
    if len(term) < 2:
        return jsonify([])
    
    search_pattern = f'%{term}%'
    devotees = Devotee.query.filter(
        Devotee.is_active == True,
        db.or_(
            Devotee.devotee_id.ilike(search_pattern),
            Devotee.full_name.ilike(search_pattern),
            Devotee.phone.ilike(search_pattern)
        )
    ).limit(10).all()
    
    results = [{
        'id': d.id,
        'devotee_id': d.devotee_id,
        'full_name': d.full_name,
        'phone': d.phone,
        'label': f'{d.devotee_id} - {d.full_name} ({d.phone})'
    } for d in devotees]
    
    return jsonify(results)


@bp.route('/nakshatra', methods=['GET'])
@login_required
def nakshatra_api():
    """API endpoint to get all nakshatras (for searchable select)"""
    nakshatras = [{
        'id': n['id'],
        'english_name': n['english_name'],
        'malayalam_name': n['malayalam_name'],
        'display_name': f"{n['english_name']} ({n['malayalam_name']})"
    } for n in MALAYALAM_NAKSHATHRAS]
    
    return jsonify(nakshatras)