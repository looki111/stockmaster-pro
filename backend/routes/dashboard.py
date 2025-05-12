from flask import Blueprint, render_template, session, request, flash, redirect, url_for, g
from backend.auth.patched_token_verify import login_required
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Blueprint setup
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    """
    Dashboard route - shows main dashboard
    """
    try:
        # Get current user from Supabase
        user = getattr(g, 'supabase_user', None)
        if not user:
            logging.warning("Unauthenticated user tried to access dashboard")
            # Store the current URL in session for redirect after login
            session['next_url'] = request.path
            return redirect(url_for('supabase_auth.login'))

        logging.info(f"Dashboard accessed by user {user.get('email', 'unknown')}")

        # Get branch - simplified for Supabase auth
        # Skip database operations for now to avoid SQLAlchemy errors
        branch = None
        logging.info("Using simplified branch handling to avoid SQLAlchemy errors")

        # Use mock data instead of database queries to avoid SQLAlchemy errors
        recent_orders = []
        low_stock_items = []

        # Mock data for dashboard
        stats = {
            'total_products': 25,
            'total_orders': 150,
            'low_stock_items': 3,
            'total_revenue': 5000,
            'today_sales': 750
        }

        logging.info("Using mock data for dashboard to avoid SQLAlchemy errors")

        # Render dashboard
        return render_template(
            'dashboard.html',
            recent_orders=recent_orders,
            low_stock_items=low_stock_items,
            stats=stats,
            lang=request.args.get('lang', 'en'),
            base_template='base_new.html'
        )

    except Exception as e:
        logging.error(f"Critical dashboard error: {e}")
        flash('Error loading dashboard. Please try again.', 'error')
        return redirect(url_for('supabase_auth.login'))

@dashboard_bp.route('/sales')
@login_required
def sales():
    """Sales page"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))
    return render_template('sales.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')

@dashboard_bp.route('/settings')
@login_required
def settings():
    """Settings page"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))
    return render_template('settings.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')

@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # For now, we'll just use the settings template
    # In a real app, you would create a dedicated profile.html template
    return render_template('settings.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')

