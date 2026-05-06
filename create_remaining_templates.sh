#!/bin/bash

# Create all remaining template directories
mkdir -p app/templates/{poojas,inventory,reports,settings}

# Create simple placeholder templates for remaining modules
# These are basic templates that can be enhanced later

# Poojas templates
cat > app/templates/poojas/services_list.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Pooja Services{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-6"><h2><i class="bi bi-calendar-event"></i> Pooja Services</h2></div>
    <div class="col-md-6 text-end">
        <a href="{{ url_for('poojas.services_add') }}" class="btn btn-primary">
            <i class="bi bi-plus"></i> Add Service
        </a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Name</th><th>Category</th><th>Price</th><th>Duration</th><th>Actions</th></tr></thead>
            <tbody>
                {% for service in services %}
                <tr>
                    <td>{{ service.name }}</td>
                    <td><span class="badge bg-info">{{ service.category }}</span></td>
                    <td>{{ service.default_price|currency }}</td>
                    <td>{{ service.duration_minutes }} min</td>
                    <td>
                        <a href="{{ url_for('poojas.services_edit', id=service.id) }}" class="btn btn-sm btn-warning">Edit</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/poojas/services_add.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Add Pooja Service{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Add Pooja Service</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Pooja Name *</label>
                        <input type="text" name="name" class="form-control" required>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Category *</label>
                            <select name="category" class="form-select" required>
                                <option value="Daily Archana">Daily Archana</option>
                                <option value="Special Pooja">Special Pooja</option>
                                <option value="Homam">Homam</option>
                                <option value="Festival">Festival</option>
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Default Price (₹) *</label>
                            <input type="number" name="default_price" class="form-control" step="1" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Duration (minutes) *</label>
                            <input type="number" name="duration_minutes" class="form-control" value="30" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Max Bookings per Day *</label>
                            <input type="number" name="max_bookings_per_day" class="form-control" value="10" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label>Description</label>
                        <textarea name="description" class="form-control" rows="3"></textarea>
                    </div>
                    <div class="form-check mb-3">
                        <input type="checkbox" name="add_to_booking" class="form-check-input" id="addToBooking" checked>
                        <label class="form-check-label" for="addToBooking">Add to Booking</label>
                    </div>
                    <button type="submit" class="btn btn-primary">Add Service</button>
                    <a href="{{ url_for('poojas.services_list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

cat > app/templates/poojas/services_edit.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Edit Pooja Service{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">Edit Pooja Service - {{ service.name }}</div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label>Pooja Name *</label>
                        <input type="text" name="name" class="form-control" value="{{ service.name }}" required>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Category *</label>
                            <select name="category" class="form-select" required>
                                <option value="Daily Archana" {% if service.category == 'Daily Archana' %}selected{% endif %}>Daily Archana</option>
                                <option value="Special Pooja" {% if service.category == 'Special Pooja' %}selected{% endif %}>Special Pooja</option>
                                <option value="Homam" {% if service.category == 'Homam' %}selected{% endif %}>Homam</option>
                                <option value="Festival" {% if service.category == 'Festival' %}selected{% endif %}>Festival</option>
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Default Price (₹) *</label>
                            <input type="number" name="default_price" class="form-control" step="1" value="{{ (service.default_price)|round(2) }}" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Duration (minutes) *</label>
                            <input type="number" name="duration_minutes" class="form-control" value="{{ service.duration_minutes }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Max Bookings per Day *</label>
                            <input type="number" name="max_bookings_per_day" class="form-control" value="{{ service.max_bookings_per_day }}" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <label>Description</label>
                        <textarea name="description" class="form-control" rows="3">{{ service.description or '' }}</textarea>
                    </div>
                    <div class="form-check mb-3">
                        <input type="checkbox" name="add_to_booking" class="form-check-input" id="requiresPriest" {% if service.add_to_booking %}checked{% endif %}>
                        <label class="form-check-label" for="requiresPriest">Show In Calendar</label>
                    </div>
                    <button type="submit" class="btn btn-primary">Update Service</button>
                    <a href="{{ url_for('poojas.services_list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

echo "✓ Created pooja service templates"

# Create more templates
cat > app/templates/poojas/bookings_list.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Pooja Bookings{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-6"><h2><i class="bi bi-calendar-check"></i> Pooja Bookings</h2></div>
    <div class="col-md-6 text-end">
        <a href="{{ url_for('poojas.bookings_add') }}" class="btn btn-primary">
            <i class="bi bi-plus"></i> New Booking
        </a>
        <a href="{{ url_for('poojas.calendar') }}" class="btn btn-success">
            <i class="bi bi-calendar"></i> Calendar View
        </a>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <table class="table">
            <thead><tr><th>Booking No</th><th>Date</th><th>Devotee</th><th>Pooja</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
                {% for booking in bookings.items %}
                <tr>
                    <td>{{ booking.booking_number }}</td>
                    <td>{{ booking.scheduled_date|format_date }} {{ booking.scheduled_time }}</td>
                    <td>{{ booking.devotee.full_name }}</td>
                    <td>{{ booking.service.name }}</td>
                    <td>
                        <span class="badge 
                            {% if booking.status == 'COMPLETED' %}bg-success
                            {% elif booking.status == 'CONFIRMED' %}bg-info
                            {% elif booking.status == 'CANCELLED' %}bg-danger
                            {% else %}bg-warning{% endif %}">
                            {{ booking.status }}
                        </span>
                    </td>
                    <td><a href="{{ url_for('poojas.bookings_view', id=booking.id) }}" class="btn btn-sm btn-primary">View</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
TEMPLATE

echo "✓ Created booking list template"

cat > app/templates/poojas/bookings_add.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}New Booking{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-10">
        <div class="card">
            <div class="card-header">New Pooja Booking</div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Devotee *</label>
                            <select name="devotee_id" class="form-select" required>
                                <option value="">-- Select Devotee --</option>
                                {% for devotee in devotees %}
                                <option value="{{ devotee.id }}">{{ devotee.devotee_id }} - {{ devotee.full_name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Pooja Service *</label>
                            <select name="service_id" class="form-select" required>
                                <option value="">-- Select Service --</option>
                                {% for service in services %}
                                <option value="{{ service.id }}">{{ service.name }} - {{ service.default_price|currency }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Scheduled Date *</label>
                            <input type="date" name="scheduled_date" class="form-control" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Time Slot *</label>
                            <input type="text" name="scheduled_time" class="form-control" placeholder="09:00 AM" required>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Priest (Optional)</label>
                            <select name="priest_id" class="form-select">
                                <option value="">-- Auto Assign --</option>
                                {% for priest in priests %}
                                <option value="{{ priest.id }}">{{ priest.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Occasion</label>
                            <input type="text" name="occasion" class="form-control" placeholder="e.g., Birthday, Anniversary">
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label>Custom Price (₹) - Optional</label>
                            <input type="number" name="custom_price" class="form-control" step="1" placeholder="Leave blank for default">
                        </div>
                        <div class="col-md-6 mb-3">
                            <label>Advance Paid (₹)</label>
                            <input type="number" name="amount_paid" class="form-control" step="1" value="0">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label>Special Instructions</label>
                        <textarea name="special_instructions" class="form-control" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Create Booking</button>
                    <a href="{{ url_for('poojas.bookings_list') }}" class="btn btn-secondary">Cancel</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

echo "✓ Created booking add template"

cat > app/templates/poojas/bookings_view.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Booking {{ booking.booking_number }}{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2>Booking {{ booking.booking_number }}</h2>
        <span class="badge 
            {% if booking.status == 'COMPLETED' %}bg-success
            {% elif booking.status == 'CONFIRMED' %}bg-info
            {% elif booking.status == 'CANCELLED' %}bg-danger
            {% else %}bg-warning{% endif %}">
            {{ booking.status }}
        </span>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <div class="row">
            <div class="col-md-6">
                <h5>Devotee Details</h5>
                <p><strong>Name:</strong> {{ booking.devotee.full_name }}</p>
                <p><strong>Phone:</strong> {{ booking.devotee.phone }}</p>
                <h5>Pooja Details</h5>
                <p><strong>Service:</strong> {{ booking.service.name }}</p>
                <p><strong>Date:</strong> {{ booking.scheduled_date|format_date }}</p>
                <p><strong>Time:</strong> {{ booking.scheduled_time }}</p>
                {% if booking.priest %}
                <p><strong>Priest:</strong> {{ booking.priest.name }}</p>
                {% endif %}
            </div>
            <div class="col-md-6">
                <h5>Payment Details</h5>
                <p><strong>Total Amount:</strong> {{ booking.total_amount|currency }}</p>
                <p><strong>Advance Paid:</strong> {{ booking.amount_paid|currency }}</p>
                <p><strong>Balance:</strong> {{ booking.balance_amount|currency }}</p>
                {% if booking.occasion %}
                <p><strong>Occasion:</strong> {{ booking.occasion }}</p>
                {% endif %}
                {% if booking.special_instructions %}
                <p><strong>Instructions:</strong> {{ booking.special_instructions }}</p>
                {% endif %}
            </div>
        </div>
        <hr>
        {% if booking.status in ['BOOKED', 'CONFIRMED'] %}
        <form method="POST" action="{{ url_for('poojas.bookings_complete', id=booking.id) }}" class="d-inline">
            <input type="hidden" name="generate_bill" value="yes">
            <button type="submit" class="btn btn-success">
                <i class="bi bi-check-circle"></i> Mark Complete & Generate Bill
            </button>
        </form>
        <form method="POST" action="{{ url_for('poojas.bookings_cancel', id=booking.id) }}" class="d-inline">
            <button type="submit" class="btn btn-danger" onclick="return confirm('Cancel this booking?')">
                <i class="bi bi-x-circle"></i> Cancel Booking
            </button>
        </form>
        {% endif %}
        {% if booking.bill %}
        <a href="{{ url_for('billing.view_bill', id=booking.bill.id) }}" class="btn btn-info">
            <i class="bi bi-receipt"></i> View Bill
        </a>
        {% endif %}
    </div>
</div>
{% endblock %}
TEMPLATE

echo "✓ Created booking view template"

cat > app/templates/poojas/calendar.html << 'TEMPLATE'
{% extends "base.html" %}
{% block title %}Booking Calendar{% endblock %}
{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <h2><i class="bi bi-calendar-range"></i> Booking Calendar - {{ month }}/{{ year }}</h2>
    </div>
</div>
<div class="card">
    <div class="card-body">
        <p class="text-muted">Calendar view feature - Displaying bookings for {{ month }}/{{ year }}</p>
        <div class="alert alert-info">
            <strong>Upcoming Feature:</strong> Interactive calendar view will be available soon.
            For now, please use the <a href="{{ url_for('poojas.bookings_list') }}">bookings list</a> view.
        </div>
    </div>
</div>
{% endblock %}
TEMPLATE

echo "✓ Created calendar template"

echo ""
echo "✅ All pooja templates created successfully!"

