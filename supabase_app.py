"""
StockMaster Pro Flask Application with Supabase Authentication
"""

import os
import logging
from flask import Flask, render_template, request, redirect, jsonify, session, g
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__,
            static_url_path='/static',
            static_folder='backend/static',
            template_folder='backend/templates')

# Configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'stockmaster-pro-secret-key'),
    TEMPLATES_AUTO_RELOAD=True,
    SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=86400,  # 24 hours

    # Supabase Configuration
    SUPABASE_URL=os.getenv('SUPABASE_URL', ''),
    SUPABASE_KEY=os.getenv('SUPABASE_KEY', ''),
    SUPABASE_JWT_SECRET=os.getenv('SUPABASE_JWT_SECRET', ''),
    FORCE_ADMIN_SECRET=os.getenv('FORCE_ADMIN_SECRET', 'stockmaster-admin-secret')
)

# Create blueprints
from flask import Blueprint
from backend.routes.supabase_auth import supabase_auth_bp

# Create other blueprints
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
pos_bp = Blueprint('pos', __name__, url_prefix='/pos')
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')
clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

# Import Supabase auth
from backend.auth.supabase_auth import (
    get_current_user,
    login_required,
    admin_required,
    role_required
)

# Root route - not protected by any middleware
@app.route('/')
def index():
    """
    Root route - redirects to dashboard if logged in, otherwise redirects to login page
    This route should not be protected by any middleware and should not throw 403 errors
    """
    # This route is intentionally simple and not protected by any middleware
    # It should always work and never throw 403 Forbidden errors
    user = get_current_user()
    if user:
        return redirect('/dashboard')  # Redirect to dashboard if logged in
    else:
        return redirect('/auth/login')  # Redirect to login page if not logged in

@app.route('/switch_lang')
def switch_lang():
    """
    Switch language route - toggles between Arabic and English
    """
    # Get current language from session or request args
    current_lang = request.args.get('lang', session.get('lang', 'en'))

    # Toggle language
    new_lang = 'ar' if current_lang == 'en' else 'en'

    # Store in session
    session['lang'] = new_lang

    # Redirect back to the referring page or home
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect('/')

# Dashboard routes
@dashboard_bp.route('/')
@login_required
def dashboard():
    """
    Dashboard route - shows main dashboard
    """
    # Mock data for dashboard
    recent_orders = []
    low_stock_items = []
    stats = {
        'total_products': 0,
        'total_orders': 0,
        'low_stock_items': 0,
        'total_revenue': 0,
        'today_sales': 0
    }

    return render_template(
        'dashboard.html',
        recent_orders=recent_orders,
        low_stock_items=low_stock_items,
        stats=stats,
        lang=request.args.get('lang', 'en')
    )

@dashboard_bp.route('/settings')
@login_required
def settings():
    """
    Settings route - shows settings page
    """
    return render_template('settings.html', lang=request.args.get('lang', 'en'))

# POS routes
@pos_bp.route('/')
@login_required
def index():
    """
    POS route - shows POS interface
    """
    return render_template('pos.html', lang=request.args.get('lang', 'en'))

# Inventory routes
@inventory_bp.route('/')
@login_required
def index():
    """
    Inventory index route - shows inventory overview
    """
    return render_template('inventory.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/raw-materials')
@login_required
def raw_materials():
    """
    Raw materials route - shows raw materials inventory
    """
    return render_template('inventory/raw_materials.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/recipes')
@login_required
def recipes():
    """
    Recipes route - shows recipes
    """
    return render_template('inventory/recipes.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/reports')
@login_required
def reports():
    """
    Reports route - shows inventory reports
    """
    return render_template('inventory/reports.html', lang=request.args.get('lang', 'en'))

# Clients routes
@clients_bp.route('/')
@login_required
def index():
    """
    Clients index route - shows clients overview
    """
    return render_template('clients.html', lang=request.args.get('lang', 'en'))

@clients_bp.route('/list')
@login_required
def clients_list():
    """
    Clients list route - shows clients list
    """
    return render_template('clients/list.html', lang=request.args.get('lang', 'en'))

# API routes
@app.route('/api/me')
@login_required
def api_me():
    """
    API endpoint to get current user data
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    return jsonify({
        'id': user.get('id'),
        'email': user.get('email'),
        'is_admin': user.get('is_admin', False),
        'metadata': user.get('user_metadata', {}),
        'app_metadata': user.get('app_metadata', {})
    })

# Register blueprints
app.register_blueprint(supabase_auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(pos_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(clients_bp)

# Apply Supabase middleware
from backend.middleware import apply_supabase_middleware
apply_supabase_middleware(app)

# Create template directories if they don't exist
import os
os.makedirs('backend/templates/inventory', exist_ok=True)
os.makedirs('backend/templates/clients', exist_ok=True)

# Create placeholder templates for missing pages
if not os.path.exists('backend/templates/inventory/raw_materials.html'):
    with open('backend/templates/inventory/raw_materials.html', 'w') as f:
        f.write('''{% extends "base.html" %}
{% block title %}Raw Materials | StockMaster Pro{% endblock %}
{% block page_title %}Raw Materials{% endblock %}

{% block content %}
<div class="container">
    <h1>Raw Materials</h1>
    <p>This is a placeholder for the Raw Materials page.</p>
</div>
{% endblock %}''')

if not os.path.exists('backend/templates/inventory/recipes.html'):
    with open('backend/templates/inventory/recipes.html', 'w') as f:
        f.write('''{% extends "base.html" %}
{% block title %}Recipes | StockMaster Pro{% endblock %}
{% block page_title %}Recipes{% endblock %}

{% block content %}
<div class="container">
    <h1>Recipes</h1>
    <p>This is a placeholder for the Recipes page.</p>
</div>
{% endblock %}''')

if not os.path.exists('backend/templates/inventory/reports.html'):
    with open('backend/templates/inventory/reports.html', 'w') as f:
        f.write('''{% extends "base.html" %}
{% block title %}Inventory Reports | StockMaster Pro{% endblock %}
{% block page_title %}Inventory Reports{% endblock %}

{% block content %}
<div class="container">
    <h1>Inventory Reports</h1>
    <p>This is a placeholder for the Inventory Reports page.</p>
</div>
{% endblock %}''')

if not os.path.exists('backend/templates/clients/list.html'):
    with open('backend/templates/clients/list.html', 'w') as f:
        f.write('''{% extends "base.html" %}
{% block title %}Clients List | StockMaster Pro{% endblock %}
{% block page_title %}Clients List{% endblock %}

{% block content %}
<div class="container">
    <h1>Clients List</h1>
    <p>This is a placeholder for the Clients List page.</p>
</div>
{% endblock %}''')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
