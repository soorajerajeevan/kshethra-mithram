#!/bin/bash

# Inventory templates
cat > app/templates/inventory/list.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Inventory{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-6"><h2><i class="bi bi-box-seam"></i> Inventory</h2></div>
    <div class="col-md-6 text-end">
        <a href="{{ url_for('inventory.add') }}" class="btn btn-primary"><i class="bi bi-plus"></i> Add Item</a>
        <a href="{{ url_for('inventory.low_stock_report') }}" class="btn btn-warning"><i class="bi bi-exclamation-triangle"></i> Low Stock</a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Item</th><th>Category</th><th>Stock</th><th>Reorder Level</th><th>Selling Price</th><th>Actions</th></tr></thead>
            <tbody>
                {% for item in items.items %}
                <tr class="{% if item.is_low_stock %}table-warning{% endif %}">
                    <td>
                        {{ item.name }}
                        {% if item.is_low_stock %}<i class="bi bi-exclamation-triangle text-danger"></i>{% endif %}
                    </td>
                    <td><span class="badge bg-info">{{ item.category }}</span></td>
                    <td>{{ item.current_stock }} {{ item.unit }}</td>
                    <td>{{ item.reorder_level }} {{ item.unit }}</td>
                    <td>{{ item.selling_price|currency }}/{{ item.unit }}</td>
                    <td>
                        <a href="{{ url_for('inventory.view', id=item.id) }}" class="btn btn-sm btn-primary">View</a>
                        <a href="{{ url_for('inventory.stock_in', id=item.id) }}" class="btn btn-sm btn-success">Stock In</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/inventory/add.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Add Inventory Item{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Add Inventory Item</div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Item Name *</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Category *</label>
                            <input type="text" name="category" class="form-control" placeholder="e.g., Flowers, Prasad" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label>Unit *</label>
                            <select name="unit" class="form-select" required>
                                <option value="kg">Kilogram (kg)</option>
                                <option value="nos">Numbers (nos)</option>
                                <option value="pack">Pack</option>
                                <option value="litre">Litre</option>
                            </select>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label>Current Stock</label>
                            <input type="number" name="current_stock" class="form-control" step="1" value="0">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label>Reorder Level</label>
                            <input type="number" name="reorder_level" class="form-control" step="1" value="0">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label>Supplier</label>
                            <input type="text" name="supplier" class="form-control">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label>Cost Price (₹)</label>
                            <input type="number" name="cost_price" class="form-control" step="1" value="0">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label>Selling Price (₹)</label>
                            <input type="number" name="selling_price" class="form-control" step="1" value="0">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Add Item</button>
                    <a href="{{ url_for('inventory.list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/inventory/view.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}{{ item.name }}{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2>{{ item.name }}</h2>
    </div>
</div>
<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">Details</div>
            <div class="card-body">
                <p><strong>Category:</strong> {{ item.category }}</p>
                <p><strong>Unit:</strong> {{ item.unit }}</p>
                <p><strong>Current Stock:</strong> <span class="badge {% if item.is_low_stock %}bg-danger{% else %}bg-success{% endif %}">{{ item.current_stock }} {{ item.unit }}</span></p>
                <p><strong>Reorder Level:</strong> {{ item.reorder_level }} {{ item.unit }}</p>
                <p><strong>Supplier:</strong> {{ item.supplier }}</p>
                <p><strong>Cost Price:</strong> {{ item.cost_price|currency }}/{{ item.unit }}</p>
                <p><strong>Selling Price:</strong> {{ item.selling_price|currency }}/{{ item.unit }}</p>
                <a href="{{ url_for('inventory.edit', id=item.id) }}" class="btn btn-warning">Edit</a>
                <a href="{{ url_for('inventory.stock_in', id=item.id) }}" class="btn btn-success">Stock In</a>
                <a href="{{ url_for('inventory.stock_out', id=item.id) }}" class="btn btn-danger">Stock Out</a>
            </div>
        </div>
    </div>
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Transaction History</div>
            <div class="card-body">
                <table class="table table-sm">
                    <thead><tr><th>Date</th><th>Type</th><th>Quantity</th><th>Reference</th><th>Notes</th></tr></thead>
                    <tbody>
                        {% for txn in transactions.items %}
                        <tr>
                            <td>{{ txn.created_at|format_datetime }}</td>
                            <td>
                                <span class="badge {% if txn.transaction_type == 'IN' %}bg-success{% else %}bg-danger{% endif %}">
                                    {{ txn.transaction_type }}
                                </span>
                            </td>
                            <td>{{ txn.quantity }} {{ item.unit }}</td>
                            <td>{{ txn.reference_type }}</td>
                            <td>{{ txn.notes or '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/inventory/edit.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Edit {{ item.name }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Edit {{ item.name }}</div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Item Name *</label>
                            <input type="text" name="name" class="form-control" value="{{ item.name }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Category *</label>
                            <input type="text" name="category" class="form-control" value="{{ item.category }}" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label>Unit *</label>
                            <select name="unit" class="form-select" required>
                                <option value="kg" {% if item.unit == 'kg' %}selected{% endif %}>Kilogram (kg)</option>
                                <option value="nos" {% if item.unit == 'nos' %}selected{% endif %}>Numbers (nos)</option>
                                <option value="pack" {% if item.unit == 'pack' %}selected{% endif %}>Pack</option>
                                <option value="litre" {% if item.unit == 'litre' %}selected{% endif %}>Litre</option>
                            </select>
                        </div>
                        <div class="col-md-4 mb-3">
                            <label>Reorder Level</label>
                            <input type="number" name="reorder_level" class="form-control" step="1" value="{{ item.reorder_level }}">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label>Supplier</label>
                            <input type="text" name="supplier" class="form-control" value="{{ item.supplier or '' }}">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label>Cost Price (₹)</label>
                            <input type="number" name="cost_price" class="form-control" step="1" value="{{ (item.cost_price )|round(2) }}">
                        </div>
                        <div class="col-md-4 mb-3">
                            <label>Selling Price (₹)</label>
                            <input type="number" name="selling_price" class="form-control" step="1" value="{{ (item.selling_price)|round(2) }}">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Update</button>
                    <a href="{{ url_for('inventory.view', id=item.id) }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/inventory/stock_in.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Stock In - {{ item.name }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Stock In - {{ item.name }}</div>
            <div class="card-body">
                <p><strong>Current Stock:</strong> {{ item.current_stock }} {{ item.unit }}</p>
                <form method="POST">
                    <div class="mb-3">
                        <label>Quantity to Add *</label>
                        <input type="number" name="quantity" class="form-control" step="1" min="0.1" required autofocus>
                    </div>
                    <div class="mb-3">
                        <label>Supplier</label>
                        <input type="text" name="supplier" class="form-control" value="{{ item.supplier or '' }}">
                    </div>
                    <div class="mb-3">
                        <label>Cost (₹)</label>
                        <input type="number" name="cost" class="form-control" step="1">
                    </div>
                    <div class="mb-3">
                        <label>Notes</label>
                        <textarea name="notes" class="form-control" rows="2"></textarea>
                    </div>
                    <button type="submit" class="btn btn-success">Add Stock</button>
                    <a href="{{ url_for('inventory.view', id=item.id) }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/inventory/stock_out.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Stock Out - {{ item.name }}{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Stock Out - {{ item.name }}</div>
            <div class="card-body">
                <p><strong>Current Stock:</strong> {{ item.current_stock }} {{ item.unit }}</p>
                <form method="POST">
                    <div class="mb-3">
                        <label>Quantity to Remove *</label>
                        <input type="number" name="quantity" class="form-control" step="1" min="0.1" max="{{ item.current_stock }}" required autofocus>
                    </div>
                    <div class="mb-3">
                        <label>Reason/Notes</label>
                        <textarea name="notes" class="form-control" rows="2" placeholder="Manual adjustment, damaged, etc."></textarea>
                    </div>
                    <button type="submit" class="btn btn-danger">Remove Stock</button>
                    <a href="{{ url_for('inventory.view', id=item.id) }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/inventory/low_stock_report.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Low Stock Report{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2><i class="bi bi-exclamation-triangle text-warning"></i> Low Stock Report</h2>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <table class="table table-striped">
            <thead><tr><th>Item</th><th>Category</th><th>Current Stock</th><th>Reorder Level</th><th>Actions</th></tr></thead>
            <tbody>
                {% for item in items %}
                <tr class="table-warning">
                    <td>{{ item.name }}</td>
                    <td>{{ item.category }}</td>
                    <td><strong>{{ item.current_stock }} {{ item.unit }}</strong></td>
                    <td>{{ item.reorder_level }} {{ item.unit }}</td>
                    <td>
                        <a href="{{ url_for('inventory.stock_in', id=item.id) }}" class="btn btn-sm btn-success">
                            <i class="bi bi-plus"></i> Restock
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if items %}
        <div class="alert alert-warning">
            <strong>Action Required:</strong> {{ items|length }} items need restocking!
        </div>
        {% else %}
        <div class="alert alert-success">
            <strong>All Good!</strong> No items below reorder level.
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
TEMPLATE

echo "✅ All inventory templates created successfully!"
