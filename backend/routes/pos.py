"""
POS Routes for StockMaster Pro
Handles POS mode API endpoints
"""

from flask import Blueprint, render_template, request, redirect, url_for, g, session
from backend.auth.patched_token_verify import login_required

pos_bp = Blueprint('pos', __name__, url_prefix='/pos')

@pos_bp.route('/')
@login_required
def index():
    """Render POS interface"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # For now, simplify the POS interface until we implement proper branch management
    # Render POS template
    return render_template('pos.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')


