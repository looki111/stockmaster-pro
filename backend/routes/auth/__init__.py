"""
Authentication routes for StockMaster Pro
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/test-supabase')
def test_supabase():
    """Test Supabase connection"""
    return render_template('test_supabase.html') 