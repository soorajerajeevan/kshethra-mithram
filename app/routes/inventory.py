from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import InventoryItem, StockTransaction
from datetime import datetime

bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@bp.route('/')
@login_required
def list():
    """List all inventory items"""
    category = request.args.get('category', '')
    low_stock = request.args.get('low_stock', '')
    
    query = InventoryItem.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if low_stock == 'yes':
        items_list = [item for item in query.all() if item.is_low_stock]
        items = type('obj', (object,), {
            'items': items_list,
            'has_prev': False,
            'has_next': False,
            'page': 1,
            'pages': 1
        })()
    else:
        page = request.args.get('page', 1, type=int)
        items = query.order_by(InventoryItem.name).paginate(
            page=page, per_page=20, error_out=False
        )
    
    categories = db.session.query(InventoryItem.category).filter(
        InventoryItem.is_active == True
    ).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    return render_template('inventory/list.html',
                         items=items,
                         categories=categories,
                         selected_category=category,
                         low_stock_filter=low_stock)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new inventory item"""
    if current_user.role not in ['admin', 'cashier']:
        flash('Permission denied', 'danger')
        return redirect(url_for('inventory.list'))
    
    if request.method == 'POST':
        # Convert prices to paise
        cost_rupees = float(request.form.get('cost_price', 0) or 0)
        selling_rupees = float(request.form.get('selling_price', 0) or 0)
        
        item = InventoryItem(
            name=request.form.get('name'),
            category=request.form.get('category'),
            unit=request.form.get('unit'),
            current_stock=float(request.form.get('current_stock', 0)),
            reorder_level=float(request.form.get('reorder_level', 0)),
            supplier=request.form.get('supplier'),
            cost_price=int(cost_rupees * 100),
            selling_price=int(selling_rupees * 100)
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Create initial stock transaction if stock > 0
        if item.current_stock > 0:
            txn = StockTransaction(
                item_id=item.id,
                transaction_type='IN',
                quantity=item.current_stock,
                reference_type='OPENING',
                notes='Opening stock',
                created_by=current_user.id
            )
            db.session.add(txn)
            db.session.commit()
        
        flash(f'Inventory item "{item.name}" added successfully!', 'success')
        return redirect(url_for('inventory.list'))
    
    return render_template('inventory/add.html')


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit inventory item"""
    if current_user.role not in ['admin', 'cashier']:
        flash('Permission denied', 'danger')
        return redirect(url_for('inventory.list'))
    
    item = InventoryItem.query.get_or_404(id)
    
    if request.method == 'POST':
        cost_rupees = float(request.form.get('cost_price', 0) or 0)
        selling_rupees = float(request.form.get('selling_price', 0) or 0)
        
        item.name = request.form.get('name')
        item.category = request.form.get('category')
        item.unit = request.form.get('unit')
        item.reorder_level = float(request.form.get('reorder_level', 0))
        item.supplier = request.form.get('supplier')
        item.cost_price = int(cost_rupees * 100)
        item.selling_price = int(selling_rupees * 100)
        
        db.session.commit()
        
        flash('Inventory item updated successfully!', 'success')
        return redirect(url_for('inventory.view', id=id))
    
    return render_template('inventory/edit.html', item=item)


@bp.route('/<int:id>')
@login_required
def view(id):
    """View inventory item details and transaction history"""
    item = InventoryItem.query.get_or_404(id)
    
    page = request.args.get('page', 1, type=int)
    transactions = StockTransaction.query.filter_by(
        item_id=item.id
    ).order_by(StockTransaction.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('inventory/view.html', item=item, transactions=transactions)


@bp.route('/<int:id>/stock-in', methods=['GET', 'POST'])
@login_required
def stock_in(id):
    """Add stock (purchase)"""
    if current_user.role not in ['admin', 'cashier']:
        flash('Permission denied', 'danger')
        return redirect(url_for('inventory.list'))
    
    item = InventoryItem.query.get_or_404(id)
    
    if request.method == 'POST':
        quantity = float(request.form.get('quantity'))
        cost_rupees = float(request.form.get('cost', 0) or 0)
        cost_paise = int(cost_rupees * 100)
        
        # Update stock
        item.current_stock += quantity
        
        # Create transaction
        txn = StockTransaction(
            item_id=item.id,
            transaction_type='IN',
            quantity=quantity,
            reference_type='PURCHASE',
            supplier=request.form.get('supplier'),
            cost=cost_paise,
            notes=request.form.get('notes'),
            created_by=current_user.id
        )
        
        db.session.add(txn)
        db.session.commit()
        
        flash(f'Stock added successfully! New stock: {item.current_stock} {item.unit}', 'success')
        return redirect(url_for('inventory.view', id=id))
    
    return render_template('inventory/stock_in.html', item=item)


@bp.route('/<int:id>/stock-out', methods=['GET', 'POST'])
@login_required
def stock_out(id):
    """Remove stock (manual adjustment)"""
    if current_user.role not in ['admin', 'cashier']:
        flash('Permission denied', 'danger')
        return redirect(url_for('inventory.list'))
    
    item = InventoryItem.query.get_or_404(id)
    
    if request.method == 'POST':
        quantity = float(request.form.get('quantity'))
        
        if quantity > item.current_stock:
            flash(f'Cannot remove {quantity} {item.unit}. Available stock: {item.current_stock} {item.unit}', 'danger')
            return redirect(url_for('inventory.stock_out', id=id))
        
        # Update stock
        item.current_stock -= quantity
        
        # Create transaction
        txn = StockTransaction(
            item_id=item.id,
            transaction_type='OUT',
            quantity=quantity,
            reference_type='ADJUSTMENT',
            notes=request.form.get('notes'),
            created_by=current_user.id
        )
        
        db.session.add(txn)
        db.session.commit()
        
        flash(f'Stock removed successfully! New stock: {item.current_stock} {item.unit}', 'success')
        return redirect(url_for('inventory.view', id=id))
    
    return render_template('inventory/stock_out.html', item=item)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft delete inventory item"""
    if current_user.role != 'admin':
        flash('Only admins can delete inventory items', 'danger')
        return redirect(url_for('inventory.list'))
    
    item = InventoryItem.query.get_or_404(id)
    item.is_active = False
    db.session.commit()
    
    flash('Inventory item deactivated successfully!', 'success')
    return redirect(url_for('inventory.list'))


@bp.route('/low-stock-report')
@login_required
def low_stock_report():
    """Report of low stock items"""
    items = [item for item in InventoryItem.query.filter_by(is_active=True).all() if item.is_low_stock]
    
    total_value = sum(item.current_stock * item.cost_price for item in items)
    
    return render_template('inventory/low_stock_report.html',
                         items=items,
                         total_value=total_value)
