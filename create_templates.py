"""
Script to generate remaining template files for the Temple Management System
Run this after setting up the project to create all missing templates.
"""

import os

TEMPLATES_DIR = "app/templates"

# Template definitions
TEMPLATES = {
    # Auth templates
    "auth/change_password.html": '''{% extends "base.html" %}
{% block title %}Change Password{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header"><i class="bi bi-key"></i> Change Password</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Current Password</label>
                        <input type="password" name="current_password" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label>New Password</label>
                        <input type="password" name="new_password" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label>Confirm New Password</label>
                        <input type="password" name="confirm_password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Change Password</button>
                    <a href="{{ url_for('dashboard.index') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    # Devotees templates
    "devotees/list.html": '''{% extends "base.html" %}
{% block title %}Devotees{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-6"><h2><i class="bi bi-people"></i> Devotees</h2></div>
    <div class="col-md-6 text-end">
        <a href="{{ url_for('devotees.add') }}" class="btn btn-primary">
            <i class="bi bi-plus"></i> Add Devotee
        </a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <form method="GET" class="mb-3">
            <div class="input-group">
                <input type="text" name="search" class="form-control" placeholder="Search by name, phone, or ID" value="{{ search }}">
                <button class="btn btn-primary" type="submit"><i class="bi bi-search"></i> Search</button>
            </div>
        </form>
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Phone</th><th>Nakshatra</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {% for devotee in devotees.items %}
                    <tr>
                        <td>{{ devotee.devotee_id }}</td>
                        <td>{{ devotee.full_name }}</td>
                        <td>{{ devotee.phone }}</td>
                        <td>{{ devotee.nakshatra }}</td>
                        <td>
                            <a href="{{ url_for('devotees.view', id=devotee.id) }}" class="btn btn-sm btn-primary">View</a>
                            <a href="{{ url_for('devotees.edit', id=devotee.id) }}" class="btn btn-sm btn-warning">Edit</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% if devotees.pages > 1 %}
        <nav>
            <ul class="pagination">
                {% if devotees.has_prev %}
                <li class="page-item"><a class="page-link" href="?page={{ devotees.prev_num }}">Previous</a></li>
                {% endif %}
                {% if devotees.has_next %}
                <li class="page-item"><a class="page-link" href="?page={{ devotees.next_num }}">Next</a></li>
                {% endif %}
            </ul>
        </nav>
        {% endif %}
    </div>
</div>
{% endblock %}''',

    "devotees/add.html": '''{% extends "base.html" %}
{% block title %}Add Devotee{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header"><i class="bi bi-person-plus"></i> Add New Devotee</div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Full Name *</label>
                            <input type="text" name="full_name" class="form-control" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Nakshatra</label>
                            <input type="text" name="nakshatra" class="form-control">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Phone *</label>
                            <input type="text" name="phone" class="form-control" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Email</label>
                            <input type="email" name="email" class="form-control">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label>Address</label>
                        <textarea name="address" class="form-control" rows="2"></textarea>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Gotra</label>
                            <input type="text" name="gotra" class="form-control">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label>Family Members</label>
                        <textarea name="family_members" class="form-control" rows="2" placeholder="e.g., Wife: Lakshmi, Son: Arun"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Add Devotee</button>
                    <a href="{{ url_for('devotees.list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    "devotees/view.html": '''{% extends "base.html" %}
{% block title %}{{ devotee.full_name }}{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2>{{ devotee.full_name }}</h2>
        <p class="text-muted">ID: {{ devotee.devotee_id }}</p>
    </div>
</div>
<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">Details</div>
            <div class="card-body">
                <p><strong>Phone:</strong> {{ devotee.phone }}</p>
                <p><strong>Email:</strong> {{ devotee.email or 'N/A' }}</p>
                <p><strong>Nakshatra:</strong> {{ devotee.nakshatra or 'N/A' }}</p>
                <p><strong>Gotra:</strong> {{ devotee.gotra or 'N/A' }}</p>
                <p><strong>Address:</strong> {{ devotee.address or 'N/A' }}</p>
                <p><strong>Family:</strong> {{ devotee.family_members or 'N/A' }}</p>
                <p><strong>Total Spent:</strong> {{ total_spent|currency }}</p>
                <a href="{{ url_for('devotees.edit', id=devotee.id) }}" class="btn btn-warning">Edit</a>
            </div>
        </div>
    </div>
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Billing History</div>
            <div class="card-body">
                <table class="table">
                    <thead><tr><th>Bill No</th><th>Date</th><th>Amount</th><th>Action</th></tr></thead>
                    <tbody>
                        {% for bill in bills %}
                        <tr>
                            <td>{{ bill.bill_number }}</td>
                            <td>{{ bill.bill_date|format_date }}</td>
                            <td>{{ bill.grand_total|currency }}</td>
                            <td><a href="{{ url_for('billing.view_bill', id=bill.id) }}" class="btn btn-sm btn-primary">View</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    "devotees/edit.html": '''{% extends "base.html" %}
{% block title %}Edit Devotee{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Edit Devotee - {{ devotee.devotee_id }}</div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Full Name *</label>
                            <input type="text" name="full_name" class="form-control" value="{{ devotee.full_name }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Nakshatra</label>
                            <input type="text" name="nakshatra" class="form-control" value="{{ devotee.nakshatra or '' }}">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Phone *</label>
                            <input type="text" name="phone" class="form-control" value="{{ devotee.phone }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Email</label>
                            <input type="email" name="email" class="form-control" value="{{ devotee.email or '' }}">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label>Address</label>
                        <textarea name="address" class="form-control" rows="2">{{ devotee.address or '' }}</textarea>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Gotra</label>
                            <input type="text" name="gotra" class="form-control" value="{{ devotee.gotra or '' }}">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label>Family Members</label>
                        <textarea name="family_members" class="form-control" rows="2">{{ devotee.family_members or '' }}</textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Update</button>
                    <a href="{{ url_for('devotees.view', id=devotee.id) }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',
}

# Add more template groups (this script will be extended)
TEMPLATES_CONTINUED = {
    "billing/view_bill.html": '''{% extends "base.html" %}
{% block title %}Bill {{ bill.bill_number }}{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2>Bill {{ bill.bill_number }}</h2>
        <div class="btn-group">
            <a href="{{ url_for('billing.print_receipt', id=bill.id) }}" class="btn btn-primary" target="_blank">
                <i class="bi bi-printer"></i> Print
            </a>
            <a href="{{ url_for('billing.receipt_pdf', id=bill.id) }}" class="btn btn-success">
                <i class="bi bi-file-pdf"></i> PDF
            </a>
            <a href="{{ url_for('billing.whatsapp_receipt', id=bill.id) }}" class="btn btn-success">
                <i class="bi bi-whatsapp"></i> WhatsApp
            </a>
        </div>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <h5>Devotee Details</h5>
                <p><strong>Name:</strong> {{ bill.devotee.full_name }}</p>
                <p><strong>ID:</strong> {{ bill.devotee.devotee_id }}</p>
                <p><strong>Phone:</strong> {{ bill.devotee.phone }}</p>
            </div>
            <div class="col-md-6">
                <h5>Bill Details</h5>
                <p><strong>Date:</strong> {{ bill.bill_date|format_datetime }}</p>
                <p><strong>Payment Mode:</strong> {{ bill.payment_mode }}</p>
                {% if bill.payment_reference %}
                <p><strong>Reference:</strong> {{ bill.payment_reference }}</p>
                {% endif %}
            </div>
        </div>
        <hr>
        <h5>Items</h5>
        <table class="table">
            <thead><tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr></thead>
            <tbody>
                {% for item in bill.items %}
                <tr>
                    <td>{{ item.item_name }}</td>
                    <td>{{ item.quantity }}</td>
                    <td>{{ item.unit_price|currency }}</td>
                    <td>{{ item.total_price|currency }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <div class="row">
            <div class="col-md-6"></div>
            <div class="col-md-6">
                <table class="table">
                    <tr><td>Subtotal:</td><td class="text-end">{{ bill.subtotal|currency }}</td></tr>
                    {% if bill.discount_amount > 0 %}
                    <tr><td>Discount:</td><td class="text-end text-danger">-{{ bill.discount_amount|currency }}</td></tr>
                    {% endif %}
                    {% if bill.donation_amount > 0 %}
                    <tr><td>Donation:</td><td class="text-end">{{ bill.donation_amount|currency }}</td></tr>
                    {% endif %}
                    <tr class="table-active"><th>Grand Total:</th><th class="text-end">{{ bill.grand_total|currency }}</th></tr>
                </table>
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    "billing/list_bills.html": '''{% extends "base.html" %}
{% block title %}Bills{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-6"><h2><i class="bi bi-receipt"></i> All Bills</h2></div>
    <div class="col-md-6 text-end">
        <a href="{{ url_for('billing.new_bill') }}" class="btn btn-primary">
            <i class="bi bi-plus"></i> New Bill
        </a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <form method="GET" class="mb-3">
            <div class="input-group">
                <input type="text" name="search" class="form-control" placeholder="Search by bill number or devotee" value="{{ search }}">
                <button class="btn btn-primary" type="submit"><i class="bi bi-search"></i> Search</button>
            </div>
        </form>
        <table class="table">
            <thead><tr><th>Bill No</th><th>Date</th><th>Devotee</th><th>Amount</th><th>Payment</th><th>Action</th></tr></thead>
            <tbody>
                {% for bill in bills.items %}
                <tr>
                    <td>{{ bill.bill_number }}</td>
                    <td>{{ bill.bill_date|format_datetime }}</td>
                    <td>{{ bill.devotee.full_name }}</td>
                    <td>{{ bill.grand_total|currency }}</td>
                    <td><span class="badge bg-info">{{ bill.payment_mode }}</span></td>
                    <td><a href="{{ url_for('billing.view_bill', id=bill.id) }}" class="btn btn-sm btn-primary">View</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}''',
}


def create_template(path, content):
    """Create a template file with the given content"""
    full_path = os.path.join(TEMPLATES_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    if os.path.exists(full_path):
        print(f"  ⏭️  Skipping {path} (already exists)")
        return False
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ Created {path}")
    return True


def main():
    """Generate all missing templates"""
    print("=" * 60)
    print("Temple Management System - Template Generator")
    print("=" * 60)
    print()
    
    # Combine all templates
    all_templates = {**TEMPLATES, **TEMPLATES_CONTINUED}
    
    created = 0
    skipped = 0
    
    for path, content in all_templates.items():
        if create_template(path, content):
            created += 1
        else:
            skipped += 1
    
    print()
    print("=" * 60)
    print(f"✅ Generation complete!")
    print(f"   Created: {created} templates")
    print(f"   Skipped: {skipped} templates (already exist)")
    print("=" * 60)
    print()
    print("NOTE: This script created some basic templates.")
    print("Additional templates need to be created manually:")
    print("  - Pooja services templates")
    print("  - Inventory templates")
    print("  - Reports templates")
    print("  - Settings templates")
    print()


if __name__ == "__main__":
    main()
