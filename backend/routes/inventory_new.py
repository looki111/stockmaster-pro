"""
Inventory Routes for StockMaster Pro
Handles inventory management, consumption rules, and stock reports
"""

from flask import Blueprint, render_template, request, redirect, url_for, g, session
from backend.auth.patched_token_verify import login_required

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

# Raw Materials Routes
@inventory_bp.route('/')
@login_required
def index():
    """Inventory index route"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/index.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/raw-materials')
@login_required
def raw_materials():
    """View raw materials inventory"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/raw_materials.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/recipes')
@login_required
def recipes():
    """View product recipes"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/recipes.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/reports')
@login_required
def reports():
    """View stock reports"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/stock_reports_simple.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/consumption-rules')
@login_required
def consumption_rules():
    """View consumption rules"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/consumption_rules.html', lang=request.args.get('lang', 'en'))
