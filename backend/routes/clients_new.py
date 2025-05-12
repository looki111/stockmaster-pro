"""
Clients Routes for StockMaster Pro
Handles client management
"""

from flask import Blueprint, render_template, request, redirect, url_for, g, session
from backend.auth.patched_token_verify import login_required

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@clients_bp.route('/')
@login_required
def index():
    """Clients index route - shows clients overview"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))
    
    # Simplified version without database access
    return render_template('clients.html', lang=request.args.get('lang', 'en'))
