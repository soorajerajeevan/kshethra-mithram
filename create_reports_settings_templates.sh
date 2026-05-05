#!/bin/bash

# Reports templates
cat > app/templates/reports/index.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Reports{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2><i class="bi bi-graph-up"></i> Reports Dashboard</h2>
    </div>
</div>
<div class="row g-4">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-cash-coin" style="font-size: 3rem; color: var(--temple-primary);"></i>
                <h5 class="mt-3">Collection Report</h5>
                <p class="text-muted">Daily/weekly/monthly collection analysis</p>
                <a href="{{ url_for('reports.collection_report') }}" class="btn btn-primary">View Report</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-calendar-event" style="font-size: 3rem; color: var(--temple-primary);"></i>
                <h5 class="mt-3">Pooja-wise Report</h5>
                <p class="text-muted">Revenue analysis by pooja type</p>
                <a href="{{ url_for('reports.pooja_wise_report') }}" class="btn btn-primary">View Report</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-people" style="font-size: 3rem; color: var(--temple-primary);"></i>
                <h5 class="mt-3">Devotee-wise Report</h5>
                <p class="text-muted">Devotee billing history</p>
                <a href="{{ url_for('reports.devotee_wise_report') }}" class="btn btn-primary">View Report</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-box-seam" style="font-size: 3rem; color: var(--temple-primary);"></i>
                <h5 class="mt-3">Inventory Report</h5>
                <p class="text-muted">Stock consumption analysis</p>
                <a href="{{ url_for('reports.inventory_consumption_report') }}" class="btn btn-primary">View Report</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-person-badge" style="font-size: 3rem; color: var(--temple-primary);"></i>
                <h5 class="mt-3">Priest-wise Report</h5>
                <p class="text-muted">Priest performance metrics</p>
                <a href="{{ url_for('reports.priest_wise_report') }}" class="btn btn-primary">View Report</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/reports/collection_report.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Collection Report{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2><i class="bi bi-cash-coin"></i> Collection Report</h2>
    </div>
</div>
<div class="card mb-3">
    <div class="card-body">
        <form method="GET" class="row g-3">
            <div class="col-md-4">
                <label>Start Date</label>
                <input type="date" name="start_date" class="form-control" value="{{ start_date }}">
            </div>
            <div class="col-md-4">
                <label>End Date</label>
                <input type="date" name="end_date" class="form-control" value="{{ end_date }}">
            </div>
            <div class="col-md-4">
                <label>&nbsp;</label>
                <button type="submit" class="btn btn-primary w-100">Generate Report</button>
            </div>
        </form>
    </div>
</div>
<div class="row g-3 mb-3">
    <div class="col-md-3">
        <div class="stat-card">
            <h6 class="text-muted">Total Collection</h6>
            <h3>{{ total_collection|currency }}</h3>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <h6 class="text-muted">Total Discount</h6>
            <h3 class="text-danger">{{ total_discount|currency }}</h3>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card">
            <h6 class="text-muted">Total Donation</h6>
            <h3 class="text-success">{{ total_donation|currency }}</h3>
        </div>
    </div>
</div>
<div class="card">
    <div class="card-header">
        Payment Mode Breakdown
        <a href="{{ url_for('reports.export_csv', report_type='collection', start_date=start_date, end_date=end_date) }}" class="btn btn-sm btn-success float-end">
            <i class="bi bi-download"></i> Export CSV
        </a>
    </div>
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Payment Mode</th><th>Count</th><th>Total</th></tr></thead>
            <tbody>
                {% for mode in payment_breakdown %}
                <tr>
                    <td><span class="badge bg-info">{{ mode.payment_mode }}</span></td>
                    <td>{{ mode.count }}</td>
                    <td><strong>{{ mode.total|currency }}</strong></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/reports/pooja_wise_report.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Pooja-wise Report{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2><i class="bi bi-calendar-event"></i> Pooja-wise Revenue Report</h2>
    </div>
</div>
<div class="card mb-3">
    <div class="card-body">
        <form method="GET" class="row g-3">
            <div class="col-md-5">
                <label>Start Date</label>
                <input type="date" name="start_date" class="form-control" value="{{ start_date }}">
            </div>
            <div class="col-md-5">
                <label>End Date</label>
                <input type="date" name="end_date" class="form-control" value="{{ end_date }}">
            </div>
            <div class="col-md-2">
                <label>&nbsp;</label>
                <button type="submit" class="btn btn-primary w-100">View</button>
            </div>
        </form>
    </div>
</div>
<div class="card">
    <div class="card-header">
        Pooja Statistics
        <a href="{{ url_for('reports.export_csv', report_type='pooja_wise', start_date=start_date, end_date=end_date) }}" class="btn btn-sm btn-success float-end">
            <i class="bi bi-download"></i> Export CSV
        </a>
    </div>
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Pooja Name</th><th>Count</th><th>Revenue</th><th>Avg per Pooja</th></tr></thead>
            <tbody>
                {% for stat in pooja_stats %}
                <tr>
                    <td>{{ stat.item_name }}</td>
                    <td>{{ stat.count }}</td>
                    <td><strong>{{ stat.revenue|currency }}</strong></td>
                    <td>{{ (stat.revenue / stat.count)|currency }}</td>
                </tr>
                {% endfor %}
            </tbody>
            <tfoot>
                <tr class="table-active">
                    <th>Total</th>
                    <th>{{ total_count }}</th>
                    <th>{{ total_revenue|currency }}</th>
                    <th></th>
                </tr>
            </tfoot>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/reports/devotee_wise_report.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Devotee-wise Report{% endblock %}
{% block content %}
<h2><i class="bi bi-people"></i> Devotee-wise Report</h2>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>ID</th><th>Name</th><th>Phone</th><th>Visits</th><th>Total Spent</th></tr></thead>
            <tbody>
                {% for stat in devotee_stats %}
                <tr>
                    <td>{{ stat.devotee_id }}</td>
                    <td>{{ stat.full_name }}</td>
                    <td>{{ stat.phone }}</td>
                    <td>{{ stat.visit_count }}</td>
                    <td><strong>{{ stat.total_spent|currency }}</strong></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/reports/inventory_consumption_report.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Inventory Consumption Report{% endblock %}
{% block content %}
<h2><i class="bi bi-box-seam"></i> Inventory Consumption Report</h2>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Item</th><th>Stock In</th><th>Stock Out</th><th>Net</th></tr></thead>
            <tbody>
                {% for txn in transactions %}
                <tr>
                    <td>{{ txn.name }}</td>
                    <td class="text-success">+{{ txn.stock_in }} {{ txn.unit }}</td>
                    <td class="text-danger">-{{ txn.stock_out }} {{ txn.unit }}</td>
                    <td>{{ (txn.stock_in - txn.stock_out) }} {{ txn.unit }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/reports/priest_wise_report.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Priest-wise Report{% endblock %}
{% block content %}
<h2><i class="bi bi-person-badge"></i> Priest-wise Report</h2>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Priest</th><th>Bookings</th><th>Total Revenue</th><th>Avg per Booking</th></tr></thead>
            <tbody>
                {% for stat in priest_stats %}
                <tr>
                    <td>{{ stat.name }}</td>
                    <td>{{ stat.booking_count }}</td>
                    <td>{{ stat.total_revenue|currency }}</td>
                    <td>{{ (stat.total_revenue / stat.booking_count)|currency if stat.booking_count > 0 else '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

# Settings templates
cat > app/templates/settings/index.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Settings{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2><i class="bi bi-gear"></i> Settings</h2>
    </div>
</div>
<div class="row g-4">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-building" style="font-size: 3rem;"></i>
                <h5 class="mt-3">Temple Settings</h5>
                <a href="{{ url_for('settings.temple_settings') }}" class="btn btn-primary">Configure</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-people" style="font-size: 3rem;"></i>
                <h5 class="mt-3">Users</h5>
                <a href="{{ url_for('settings.users_list') }}" class="btn btn-primary">Manage</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-person-badge" style="font-size: 3rem;"></i>
                <h5 class="mt-3">Priests</h5>
                <a href="{{ url_for('settings.priests_list') }}" class="btn btn-primary">Manage</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-clock" style="font-size: 3rem;"></i>
                <h5 class="mt-3">Time Slots</h5>
                <a href="{{ url_for('settings.time_slots') }}" class="btn btn-primary">Configure</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body text-center">
                <i class="bi bi-download" style="font-size: 3rem;"></i>
                <h5 class="mt-3">Backup Database</h5>
                <a href="{{ url_for('settings.backup_database') }}" class="btn btn-success">Download</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/temple_settings.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Temple Settings{% endblock %}
{% block content %}
<h2><i class="bi bi-building"></i> Temple Settings</h2>
<div class="card">
    <div class="card-body">
        <form method="POST" enctype="multipart/form-data">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label>Temple Name</label>
                    <input type="text" name="temple_name" class="form-control" value="{{ settings.get('temple_name', '') }}">
                </div>
                <div class="col-md-6 mb-3">
                    <label>Phone</label>
                    <input type="text" name="temple_phone" class="form-control" value="{{ settings.get('temple_phone', '') }}">
                </div>
            </div>
            <div class="mb-3">
                <label>Address</label>
                <textarea name="temple_address" class="form-control" rows="2">{{ settings.get('temple_address', '') }}</textarea>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label>Email</label>
                    <input type="email" name="temple_email" class="form-control" value="{{ settings.get('temple_email', '') }}">
                </div>
                <div class="col-md-6 mb-3">
                    <label>GST Number</label>
                    <input type="text" name="gst_number" class="form-control" value="{{ settings.get('gst_number', '') }}">
                </div>
            </div>
            <div class="mb-3">
                <label>Receipt Footer Message</label>
                <textarea name="receipt_footer" class="form-control" rows="2">{{ settings.get('receipt_footer', '') }}</textarea>
            </div>
            <div class="mb-3">
                <label>Temple Logo</label>
                <input type="file" name="temple_logo" class="form-control" accept="image/*">
            </div>
            <button type="submit" class="btn btn-primary">Save Settings</button>
        </form>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/users_list.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Users{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-6"><h2><i class="bi bi-people"></i> Users</h2></div>
    <div class="col-md-6 text-end">
        <a href="{{ url_for('settings.users_add') }}" class="btn btn-primary"><i class="bi bi-plus"></i> Add User</a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Username</th><th>Full Name</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.username }}</td>
                    <td>{{ user.full_name }}</td>
                    <td><span class="badge bg-info">{{ user.role }}</span></td>
                    <td>
                        <span class="badge {% if user.is_active %}bg-success{% else %}bg-danger{% endif %}">
                            {% if user.is_active %}Active{% else %}Inactive{% endif %}
                        </span>
                    </td>
                    <td>
                        <a href="{{ url_for('settings.users_edit', id=user.id) }}" class="btn btn-sm btn-warning">Edit</a>
                        <form method="POST" action="{{ url_for('settings.users_toggle_active', id=user.id) }}" class="d-inline">
                            <button type="submit" class="btn btn-sm {% if user.is_active %}btn-danger{% else %}btn-success{% endif %}">
                                {% if user.is_active %}Deactivate{% else %}Activate{% endif %}
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/users_add.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Add User{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Add User</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Username *</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label>Email *</label>
                        <input type="email" name="email" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label>Full Name *</label>
                        <input type="text" name="full_name" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label>Role *</label>
                        <select name="role" class="form-select" required>
                            <option value="admin">Admin</option>
                            <option value="cashier">Cashier</option>
                            <option value="priest">Priest</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label>Password *</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Create User</button>
                    <a href="{{ url_for('settings.users_list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/users_edit.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Edit User{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Edit User - {{ user.username }}</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Email *</label>
                        <input type="email" name="email" class="form-control" value="{{ user.email }}" required>
                    </div>
                    <div class="mb-3">
                        <label>Full Name *</label>
                        <input type="text" name="full_name" class="form-control" value="{{ user.full_name }}" required>
                    </div>
                    <div class="mb-3">
                        <label>Role *</label>
                        <select name="role" class="form-select" required>
                            <option value="admin" {% if user.role == 'admin' %}selected{% endif %}>Admin</option>
                            <option value="cashier" {% if user.role == 'cashier' %}selected{% endif %}>Cashier</option>
                            <option value="priest" {% if user.role == 'priest' %}selected{% endif %}>Priest</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label>New Password (leave blank to keep current)</label>
                        <input type="password" name="password" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary">Update User</button>
                    <a href="{{ url_for('settings.users_list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/priests_list.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Priests{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-6"><h2><i class="bi bi-person-badge"></i> Priests</h2></div>
    <div class="col-md-6 text-end">
        <a href="{{ url_for('settings.priests_add') }}" class="btn btn-primary"><i class="bi bi-plus"></i> Add Priest</a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Name</th><th>Phone</th><th>Specialization</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
                {% for priest in priests %}
                <tr>
                    <td>{{ priest.name }}</td>
                    <td>{{ priest.phone }}</td>
                    <td>{{ priest.specialization }}</td>
                    <td>
                        <span class="badge {% if priest.is_active %}bg-success{% else %}bg-danger{% endif %}">
                            {% if priest.is_active %}Active{% else %}Inactive{% endif %}
                        </span>
                    </td>
                    <td>
                        <a href="{{ url_for('settings.priests_edit', id=priest.id) }}" class="btn btn-sm btn-warning">Edit</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/priests_add.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Add Priest{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Add Priest</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Name *</label>
                        <input type="text" name="name" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label>Phone</label>
                        <input type="text" name="phone" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label>Specialization</label>
                        <input type="text" name="specialization" class="form-control" placeholder="e.g., Homam specialist">
                    </div>
                    <button type="submit" class="btn btn-primary">Add Priest</button>
                    <a href="{{ url_for('settings.priests_list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/priests_edit.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Edit Priest{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">Edit Priest - {{ priest.name }}</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Name *</label>
                        <input type="text" name="name" class="form-control" value="{{ priest.name }}" required>
                    </div>
                    <div class="mb-3">
                        <label>Phone</label>
                        <input type="text" name="phone" class="form-control" value="{{ priest.phone or '' }}">
                    </div>
                    <div class="mb-3">
                        <label>Specialization</label>
                        <input type="text" name="specialization" class="form-control" value="{{ priest.specialization or '' }}">
                    </div>
                    <button type="submit" class="btn btn-primary">Update Priest</button>
                    <a href="{{ url_for('settings.priests_list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/settings/time_slots.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Time Slots{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Configure Time Slots</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Available Time Slots (one per line)</label>
                        <textarea name="time_slots" class="form-control" rows="15" required>{{ time_slots }}</textarea>
                        <small class="text-muted">Example: 09:00 AM, 10:00 AM, 11:00 AM</small>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Time Slots</button>
                    <a href="{{ url_for('settings.index') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

echo "✅ All reports and settings templates created successfully!"
