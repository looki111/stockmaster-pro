from flask import Flask, Blueprint, render_template, request, redirect, session, g

app = Flask(__name__, 
            static_url_path='/static',
            static_folder='backend/static',
            template_folder='backend/templates')

app.secret_key = 'stockmaster_pro_secret_key'  # Change this to a secure random key in production

# Mock user data for demonstration
users = {
    'admin': {
        'username': 'admin',
        'password': 'admin123',
        'role': 'Administrator'
    }
}

# Mock current user for templates
class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
pos_bp = Blueprint('pos', __name__, url_prefix='/pos')
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')
clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@app.context_processor
def inject_user():
    if 'username' in session:
        return {'current_user': User(session['username'], users[session['username']]['role'])}
    return {'current_user': User('Guest', 'Guest')}

# Root route - not protected by any middleware
@app.route('/')
def index():
    """
    Root route - redirects to dashboard if logged in, otherwise redirects to login page
    This route should not be protected by any middleware and should not throw 403 errors
    """
    if 'username' in session:
        return redirect('/dashboard')  # Redirect to dashboard if logged in
    else:
        return redirect('/auth/login')  # Redirect to login page if not logged in

# Auth routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route - handles login form submission and renders login page
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect('/dashboard')  # Use direct path instead of url_for
        
        return render_template('login.html', error='Invalid username or password', lang=request.args.get('lang', 'en'))
    
    return render_template('login.html', lang=request.args.get('lang', 'en'))

@auth_bp.route('/logout')
def logout():
    """
    Logout route - clears session and redirects to login page
    """
    session.pop('username', None)
    return redirect('/')  # Use direct path instead of url_for

# Dashboard routes
@dashboard_bp.route('/')
def dashboard():
    """
    Dashboard route - shows main dashboard
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
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
def settings():
    """
    Settings route - shows settings page
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('settings.html', lang=request.args.get('lang', 'en'))

# POS routes
@pos_bp.route('/')
def index():
    """
    POS route - shows POS interface
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('pos.html', lang=request.args.get('lang', 'en'))

# Inventory routes
@inventory_bp.route('/')
def index():
    """
    Inventory index route - shows inventory overview
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('inventory.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/raw-materials')
def raw_materials():
    """
    Raw materials route - shows raw materials inventory
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('inventory/raw_materials.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/recipes')
def recipes():
    """
    Recipes route - shows recipes
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('inventory/recipes.html', lang=request.args.get('lang', 'en'))

@inventory_bp.route('/reports')
def reports():
    """
    Reports route - shows inventory reports
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('inventory/reports.html', lang=request.args.get('lang', 'en'))

# Clients routes
@clients_bp.route('/')
def index():
    """
    Clients index route - shows clients overview
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('clients.html', lang=request.args.get('lang', 'en'))

@clients_bp.route('/list')
def clients_list():
    """
    Clients list route - shows clients list
    """
    if 'username' not in session:
        return redirect('/auth/login')  # Use direct path instead of url_for
    
    return render_template('clients/list.html', lang=request.args.get('lang', 'en'))

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(pos_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(clients_bp)

# Create template directories if they don't exist
import os
os.makedirs('backend/templates/inventory', exist_ok=True)
os.makedirs('backend/templates/clients', exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
