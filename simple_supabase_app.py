
"""
Simple StockMaster Pro Flask Application with Supabase Authentication
"""

import os
import logging
import sys
from flask import Flask, render_template, request, redirect, jsonify, session, g
from dotenv import load_dotenv
from functools import wraps

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
    SUPABASE_URL=os.getenv('SUPABASE_URL', ''),
    SUPABASE_KEY=os.getenv('SUPABASE_KEY', ''),
    SUPABASE_JWT_SECRET=os.getenv('SUPABASE_JWT_SECRET', ''),
    FORCE_ADMIN_SECRET=os.getenv('FORCE_ADMIN_SECRET', 'stockmaster-admin-secret')
)

# Supabase authentication functions
def get_token_from_request():
    """
    Extract the JWT token from the request.
    Checks the Authorization header and session cookie.
    """
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]

    # Check session
    if 'supabase_token' in session:
        return session['supabase_token']

    # Check cookies
    token = request.cookies.get('supabase_token')
    if token:
        return token

    return None

def get_current_user():
    """
    Get the current authenticated user from the request.
    """
    # For simplicity, we'll just check if the user is in the session
    if 'user' in session:
        return session['user']

    return None

def login_required(f):
    """
    Decorator to require authentication for a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect('/auth/login')
        return f(*args, **kwargs)
    return decorated_function

# Root route - not protected by any middleware
@app.route('/')
def index():
    """
    Root route - redirects to dashboard if logged in, otherwise redirects to login page
    """
    user = get_current_user()
    if user:
        return redirect('/dashboard')  # Redirect to dashboard if logged in
    else:
        return redirect('/auth/login')  # Redirect to login page if not logged in

# Auth routes
@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """
    Login route - renders login page and handles token validation
    """
    # If already authenticated, redirect to dashboard
    user = get_current_user()
    if user:
        return redirect('/dashboard')

    # Handle POST request (token validation)
    if request.method == 'POST':
        # Check if it's a JSON request (API call)
        if request.is_json:
            data = request.get_json()
            token = data.get('token')

            if not token:
                return jsonify({'error': 'Token is required'}), 400

            # For simplicity, we'll just store the token and a mock user in the session
            session['supabase_token'] = token
            session['user'] = {
                'id': '123',
                'email': 'user@example.com',
                'is_admin': True
            }

            return jsonify({
                'success': True,
                'user': session['user']
            })

        # Handle form submission (for traditional form-based login)
        username = request.form.get('username')
        password = request.form.get('password')

        # For simplicity, we'll just check if the username and password are provided
        if username and password:
            # Mock user authentication
            session['user'] = {
                'id': '123',
                'email': username,
                'is_admin': True
            }

            return redirect('/dashboard')

        return render_template('login.html', error='Invalid username or password')

    # GET request - render login page
    return render_template('login.html')

@app.route('/auth/logout', methods=['GET', 'POST'])
def logout():
    """
    Logout route - clears session and redirects to login page
    """
    # Clear session
    session.pop('supabase_token', None)
    session.pop('user', None)

    # If it's an API call, return JSON response
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True})

    # Otherwise, redirect to login page
    return redirect('/auth/login')

# Dashboard routes
@app.route('/dashboard')
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

    return jsonify(user)

@app.route('/force-admin', methods=['POST'])
def force_admin():
    """
    Force a user to be an admin
    Requires a secret token to prevent unauthorized access
    """
    data = request.get_json()
    secret = data.get('secret')
    user_id = data.get('user_id')

    if not secret or not user_id:
        return jsonify({'error': 'Secret and user_id are required'}), 400

    if secret != app.config['FORCE_ADMIN_SECRET']:
        return jsonify({'error': 'Invalid secret'}), 401

    # For simplicity, we'll just store a mock user in the session
    session['user'] = {
        'id': user_id,
        'email': 'admin@example.com',
        'is_admin': True
    }

    return jsonify({'success': True})

# Add context processor to make current_user available in templates
@app.context_processor
def inject_user():
    user = get_current_user()
    if user:
        return {'current_user': user}
    return {'current_user': {'username': 'Guest', 'role': 'Guest'}}

# Create template directories if they don't exist
import os
os.makedirs('backend/templates/inventory', exist_ok=True)
os.makedirs('backend/templates/clients', exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)




{
  "secret": "stockmaster-admin-secret",
  "user_id": "your-user-id"
}

