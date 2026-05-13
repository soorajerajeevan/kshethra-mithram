from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import TempleSettings, User, Priest, PoojaBooking, Bill, StockTransaction
from werkzeug.utils import secure_filename
import os
import shutil
from datetime import datetime
import json
from app.utils.dotmatrix_layout import build_receipt_lines, compute_layout_model, normalize_layout_config

bp = Blueprint('settings', __name__, url_prefix='/settings')


def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('This page requires admin privileges', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return login_required(decorated_function)


@bp.route('/')
@admin_required
def index():
    """Settings dashboard"""
    return render_template('settings/index.html')


def _preview_bill_data():
    bill = Bill.query.order_by(Bill.bill_date.desc()).first()
    if bill:
        return bill
    return None


@bp.route('/temple', methods=['GET', 'POST'])
@admin_required
def temple_settings():
    """Temple configuration"""
    if request.method == 'POST':
        # Update or create settings
        settings_keys = ['temple_name', 'temple_address', 'temple_phone', 
                        'temple_email', 'gst_number', 'receipt_footer', 'printer_type']
        
        for key in settings_keys:
            value = request.form.get(key, '')
            setting = TempleSettings.query.filter_by(key=key).first()
            
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = TempleSettings(key=key, value=value)
                db.session.add(setting)
        
        # Handle logo upload
        if 'temple_logo' in request.files:
            file = request.files['temple_logo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Create uploads folder if it doesn't exist
                upload_folder = os.path.join('app', 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                filepath = os.path.join(upload_folder, 'temple_logo.png')
                file.save(filepath)
                
                # Save logo path in settings
                logo_setting = TempleSettings.query.filter_by(key='temple_logo').first()
                if logo_setting:
                    logo_setting.value = 'temple_logo.png'
                else:
                    logo_setting = TempleSettings(key='temple_logo', value='temple_logo.png')
                    db.session.add(logo_setting)
        
        db.session.commit()
        flash('Temple settings updated successfully!', 'success')
        return redirect(url_for('settings.temple_settings'))
    
    # GET request - load current settings
    settings_dict = {}
    settings = TempleSettings.query.all()
    for setting in settings:
        settings_dict[setting.key] = setting.value
    
    return render_template('settings/temple_settings.html', settings=settings_dict)


@bp.route('/dotmatrix-layout')
@admin_required
def dotmatrix_layout_designer():
    """Dot matrix layout designer page"""
    bill = _preview_bill_data()
    if not bill:
        flash('Create at least one bill to design dot matrix layout preview.', 'warning')
        return redirect(url_for('billing.new_bill'))

    settings_map = {
        setting.key: setting.value
        for setting in TempleSettings.query.filter(
            TempleSettings.key.in_(['temple_name', 'temple_address', 'temple_phone', 'receipt_footer', 'dotmatrix6_layout_config'])
        ).all()
    }
    temple_name = settings_map.get('temple_name') or 'Sri Venkateshwara Temple'
    temple_address = settings_map.get('temple_address') or 'Temple Road, Temple City'
    temple_phone = settings_map.get('temple_phone') or '+91 1234567890'
    receipt_footer = settings_map.get('receipt_footer') or 'May the divine bless you!'
    layout_config = normalize_layout_config(settings_map.get('dotmatrix6_layout_config'))
    lines = build_receipt_lines(bill, temple_name, temple_address, temple_phone, receipt_footer)
    layout_model = compute_layout_model(lines, layout_config)

    return render_template(
        'settings/dotmatrix_layout.html',
        preview_bill=bill,
        dotmatrix_layout=layout_model,
        dotmatrix_layout_config=layout_config
    )


@bp.route('/dotmatrix-layout/config', methods=['GET'])
@admin_required
def dotmatrix_layout_config_get():
    setting = TempleSettings.query.filter_by(key='dotmatrix6_layout_config').first()
    return jsonify(normalize_layout_config(setting.value if setting else None))


@bp.route('/dotmatrix-layout/config', methods=['POST'])
@admin_required
def dotmatrix_layout_config_save():
    payload = request.get_json(silent=True) or {}
    config = normalize_layout_config(payload)
    serialized = json.dumps(config)

    setting = TempleSettings.query.filter_by(key='dotmatrix6_layout_config').first()
    if setting:
        setting.value = serialized
        setting.updated_at = datetime.utcnow()
    else:
        setting = TempleSettings(
            key='dotmatrix6_layout_config',
            value=serialized,
            description='Dot matrix 6-inch receipt canvas layout config'
        )
        db.session.add(setting)

    db.session.commit()
    return jsonify({"success": True, "config": config})


@bp.route('/users')
@admin_required
def users_list():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('settings/users_list.html', users=users)


@bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def users_add():
    """Add new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('settings.users_add'))
        
        user = User(
            username=username,
            email=request.form.get('email'),
            full_name=request.form.get('full_name'),
            role=request.form.get('role')
        )
        user.set_password(request.form.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} created successfully!', 'success')
        return redirect(url_for('settings.users_list'))
    
    return render_template('settings/users_add.html')


@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def users_edit(id):
    """Edit user"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        user.role = request.form.get('role')
        
        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('settings.users_list'))
    
    return render_template('settings/users_edit.html', user=user)


@bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@admin_required
def users_toggle_active(id):
    """Activate/deactivate user"""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('Cannot deactivate your own account!', 'danger')
        return redirect(url_for('settings.users_list'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status} successfully!', 'success')
    return redirect(url_for('settings.users_list'))


@bp.route('/priests')
@admin_required
def priests_list():
    """List all priests"""
    priests = Priest.query.order_by(Priest.name).all()
    return render_template('settings/priests_list.html', priests=priests)


@bp.route('/priests/add', methods=['GET', 'POST'])
@admin_required
def priests_add():
    """Add new priest"""
    if request.method == 'POST':
        priest = Priest(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            specialization=request.form.get('specialization')
        )
        
        db.session.add(priest)
        db.session.commit()
        
        flash(f'Priest {priest.name} added successfully!', 'success')
        return redirect(url_for('settings.priests_list'))
    
    return render_template('settings/priests_add.html')


@bp.route('/priests/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def priests_edit(id):
    """Edit priest"""
    priest = Priest.query.get_or_404(id)
    
    if request.method == 'POST':
        priest.name = request.form.get('name')
        priest.phone = request.form.get('phone')
        priest.specialization = request.form.get('specialization')
        
        db.session.commit()
        
        flash('Priest updated successfully!', 'success')
        return redirect(url_for('settings.priests_list'))
    
    return render_template('settings/priests_edit.html', priest=priest)


@bp.route('/priests/<int:id>/toggle-active', methods=['POST'])
@admin_required
def priests_toggle_active(id):
    """Activate/deactivate priest"""
    priest = Priest.query.get_or_404(id)
    priest.is_active = not priest.is_active
    db.session.commit()
    
    status = 'activated' if priest.is_active else 'deactivated'
    flash(f'Priest {status} successfully!', 'success')
    return redirect(url_for('settings.priests_list'))


@bp.route('/users/<int:id>/delete', methods=['POST'])
@admin_required
def users_delete(id):
    """Delete user if unused, else disable with warning"""
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Cannot delete your own account!', 'danger')
        return redirect(url_for('settings.users_list'))

    usage = (
        Bill.query.filter_by(created_by=user.id).count() +
        PoojaBooking.query.filter_by(created_by=user.id).count() +
        StockTransaction.query.filter_by(created_by=user.id).count()
    )
    if usage > 0:
        user.is_active = False
        db.session.commit()
        flash('User is already in use and cannot be deleted. User has been deactivated instead.', 'warning')
        return redirect(url_for('settings.users_list'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('settings.users_list'))


@bp.route('/priests/<int:id>/delete', methods=['POST'])
@admin_required
def priests_delete(id):
    """Delete priest"""
    priest = Priest.query.get_or_404(id)

    db.session.delete(priest)
    db.session.commit()
    flash('Priest deleted successfully!', 'success')
    return redirect(url_for('settings.priests_list'))


@bp.route('/backup')
@admin_required
def backup_database():
    """Download database backup"""
    # Get database path
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temple_dev.db')
    
    if not os.path.exists(db_path):
        flash('Database file not found!', 'danger')
        return redirect(url_for('settings.index'))
    
    # Create backup with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'temple_backup_{timestamp}.db'
    
    return send_file(db_path, as_attachment=True, download_name=backup_name)


@bp.route('/time-slots', methods=['GET', 'POST'])
@admin_required
def time_slots():
    """Manage time slots for pooja scheduling"""
    if request.method == 'POST':
        slots_text = request.form.get('time_slots')
        
        # Save time slots
        setting = TempleSettings.query.filter_by(key='time_slots').first()
        if setting:
            setting.value = slots_text
        else:
            setting = TempleSettings(key='time_slots', value=slots_text)
            db.session.add(setting)
        
        db.session.commit()
        flash('Time slots updated successfully!', 'success')
        return redirect(url_for('settings.time_slots'))
    
    # GET - load current time slots
    setting = TempleSettings.query.filter_by(key='time_slots').first()
    slots_text = setting.value if setting else '''06:00 AM
07:00 AM
08:00 AM
09:00 AM
10:00 AM
11:00 AM
12:00 PM
04:00 PM
05:00 PM
06:00 PM'''
    
    return render_template('settings/time_slots.html', time_slots=slots_text)
