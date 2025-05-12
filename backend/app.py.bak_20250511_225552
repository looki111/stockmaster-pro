import sys
import os
print("Python executable:", sys.executable)
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())

try:
    import pandas
    print("Pandas version:", pandas.__version__)
    print("Pandas location:", pandas.__file__)
except ImportError as e:
    print("Error importing pandas:", e)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database.db_setup import db, init_db
from database.models import (
    User, Product, Sale, RawMaterial, Recipe, Order, OrderItem, Notification,
    Branch, Client, Vendor, ActivityLog, Promotion, Permission, Role
)
from datetime import datetime, timezone
from notifications import create_notification, get_notifications, mark_notification_read, mark_all_notifications_read
from utils.invoice import InvoiceGenerator
from utils.loyalty import calculate_loyalty_points
from utils.activity_logger import log_activity
from roles import init_roles_and_permissions, require_permission, get_user_permissions, DEFAULT_PERMISSIONS
import os
import json
from dotenv import load_dotenv
from flask_login import current_user
from flask_migrate import Migrate
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.clients import clients_bp
from routes.promotions import promotions_bp
from routes.subscription import subscription_bp
from middleware.subscription_middleware import apply_subscription_middleware
from routes.user_preferences import user_preferences_bp

# تحميل متغيرات البيئة
load_dotenv()

app = Flask(__name__)

# Configuration
# Make sure the instance directory exists
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key-here'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(instance_path, "stockmaster.db")}'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    TEMPLATES_AUTO_RELOAD=True,
    UPLOAD_FOLDER='static/uploads',
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
)

# Initialize extensions
init_db(app)
migrate = Migrate(app, db)
init_roles_and_permissions(app)  # Initialize default roles and permissions

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Language and theme handling
def get_current_language():
    if current_user.is_authenticated:
        return current_user.preferred_language
    return session.get('lang', 'ar')  # Default to Arabic

def get_current_theme():
    if current_user.is_authenticated:
        # Check if the theme attribute exists in the user model
        if hasattr(current_user, 'theme') and current_user.theme:
            return current_user.theme
    # Fallback to session or default to 'light'
    return session.get('theme', 'light')

@app.before_request
def before_request():
    # Always set language and theme in g for templates
    try:
        g.lang = get_current_language()
        g.theme = get_current_theme()
    except Exception as e:
        print(f"Error setting language/theme: {e}")
        g.lang = 'en'
        g.theme = 'light'

    # Skip further processing for static files and authentication endpoints
    if request.endpoint and (
        request.endpoint.startswith('static') or
        request.endpoint == 'auth.logout' or
        request.endpoint == 'auth.login' or
        'favicon' in request.path
    ):
        return

    # Update last_login for authenticated users
    if current_user.is_authenticated:
        try:
            # Only update last_login once per session
            if not session.get('login_updated'):
                current_user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                session['login_updated'] = True
        except Exception as e:
            print(f"Error updating last_login: {e}")
            db.session.rollback()

@app.context_processor
def inject_globals():
    # Get language and theme safely
    lang = getattr(g, 'lang', get_current_language())
    theme = getattr(g, 'theme', get_current_theme())

    return {
        'lang': lang,
        'theme': theme,
        'get_theme': get_current_theme,
        'current_branch': current_user.branch if current_user.is_authenticated else None,
        'user_permissions': get_user_permissions(current_user) if current_user.is_authenticated else []
    }

@app.context_processor
def inject_user_and_lang():
    return dict(user=current_user, lang=session.get('lang', 'ar'))

@app.route('/switch-lang')
@app.route('/switch_lang')
def switch_lang():
    lang = get_current_language()
    new_lang = 'en' if lang == 'ar' else 'ar'
    if current_user.is_authenticated:
        current_user.preferred_language = new_lang
        db.session.commit()
    else:
        session['lang'] = new_lang

    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'language': new_lang})

    # Si no es AJAX, redirigir como antes
    return redirect(request.referrer or url_for('landing'))

@app.route('/switch-theme')
@app.route('/switch_theme')
def switch_theme():
    theme = get_current_theme()
    new_theme = 'dark' if theme == 'light' else 'light'
    if current_user.is_authenticated:
        current_user.theme = new_theme
        db.session.commit()
    else:
        session['theme'] = new_theme

    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'theme': new_theme})

    # Si no es AJAX, redirigir como antes
    return redirect(request.referrer or url_for('landing'))

# Routes
@app.route('/')
def index():
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect('/dashboard')
    return redirect('/auth/login')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp)
app.register_blueprint(clients_bp)
app.register_blueprint(promotions_bp)
app.register_blueprint(subscription_bp)
app.register_blueprint(user_preferences_bp)

# Register POS blueprint
from routes.pos import pos_bp
app.register_blueprint(pos_bp)

# Register Inventory blueprint
from routes.inventory import inventory_bp
app.register_blueprint(inventory_bp)

# Debug: Print all registered routes at startup

def list_routes(app):
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint:30s} {methods:20s} {rule}")
        output.append(line)
    return output

# Apply middleware
apply_subscription_middleware(app)

# Apply tenant context middleware
from middleware import apply_tenant_context_middleware
apply_tenant_context_middleware(app)

@app.route('/dashboard_redirect')
@login_required
def dashboard_redirect():
    # Redirect to the dashboard blueprint route
    return redirect(url_for('dashboard.dashboard'))

@app.route('/sales')
@login_required
def sales():
    return render_template('sales.html')

@app.route('/raw_materials')
@login_required
def raw_materials():
    # Get all raw materials
    materials = RawMaterial.query.all()

    # Get low stock items
    low_stock = RawMaterial.query.filter(
        RawMaterial.quantity <= RawMaterial.alert_threshold
    ).all()

    return render_template('raw_materials.html',
                          materials=materials,
                          low_stock=low_stock)

@app.route('/raw_materials/add', methods=['GET', 'POST'])
@login_required
def add_material():
    if request.method == 'POST':
        # Create new raw material
        material = RawMaterial(
            name=request.form['name'],
            category=request.form['category'],
            quantity=float(request.form['quantity']),
            unit=request.form['unit'],
            alert_threshold=float(request.form['alert_threshold']),
            cost_per_unit=float(request.form['cost_per_unit']),
            branch_id=current_user.branch_id
        )
        db.session.add(material)
        db.session.commit()
        flash('تمت إضافة المادة الخام بنجاح', 'success')
        return redirect(url_for('inventory.raw_materials'))

    return render_template('add_material.html')

@app.route('/raw_materials/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_material(id):
    material = RawMaterial.query.get_or_404(id)

    if request.method == 'POST':
        material.name = request.form['name']
        material.category = request.form['category']
        material.quantity = float(request.form['quantity'])
        material.unit = request.form['unit']
        material.alert_threshold = float(request.form['alert_threshold'])
        material.cost_per_unit = float(request.form['cost_per_unit'])

        db.session.commit()
        flash('تم تحديث المادة الخام بنجاح', 'success')
        return redirect(url_for('inventory.raw_materials'))

    return render_template('edit_material.html', material=material)

@app.route('/raw_materials/delete/<int:id>', methods=['POST'])
@login_required
def delete_material(id):
    material = RawMaterial.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash('تم حذف المادة الخام بنجاح', 'success')
    return redirect(url_for('inventory.raw_materials'))

@app.route('/raw_materials/history/<int:id>')
@login_required
def material_history(id):
    material = RawMaterial.query.get_or_404(id)
    # Get history from inventory_log table (assuming it exists)
    history = []  # Replace with actual query
    return render_template('material_history.html', material=material, history=history)

@app.route('/recipes')
@login_required
def recipes():
    return render_template('recipes.html')

@app.route('/suppliers')
@login_required
def suppliers():
    return render_template('suppliers.html')

@app.route('/reports')
@login_required
def reports():
    branch = current_user.branch
    start_date = request.args.get('start_date', datetime.now(timezone.utc).date().isoformat())
    end_date = request.args.get('end_date', datetime.now(timezone.utc).date().isoformat())

    # Get sales data
    sales_data = Order.query.filter(
        Order.branch_id == branch.id,
        Order.created_at.between(start_date, end_date)
    ).all()

    # Get top products
    top_products = db.session.query(
        Product, db.func.sum(OrderItem.quantity).label('total_quantity')
    ).join(OrderItem).join(Order).filter(
        Order.branch_id == branch.id,
        Order.created_at.between(start_date, end_date)
    ).group_by(Product.id).order_by(db.desc('total_quantity')).limit(5).all()

    return render_template('reports.html',
                         sales_data=sales_data,
                         top_products=top_products,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

# API Routes for notifications
@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications_route():
    try:
        notifications = get_notifications(
            user_id=current_user.id,
            limit=20
        )

        return jsonify({
            'success': True,
            'notifications': [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.type,
                'read': n.read,
                'created_at': n.created_at.isoformat()
            } for n in notifications]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    try:
        data = request.json
        order = Order(
            invoice_number=generate_invoice_number(),
            client_id=data.get('client_id'),
            subtotal=data['subtotal'],
            tax=data['tax'],
            total=data['total'],
            payment_method=data['payment_method'],
            created_by=current_user.id,
            branch_id=current_user.branch_id,
            notes=data.get('notes')
        )

        # Add order items
        for item in data['items']:
            order_item = OrderItem(
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['total_price']
            )
            order.items.append(order_item)

            # Update product quantity
            product = Product.query.get(item['product_id'])
            product.quantity -= item['quantity']

            # Update raw materials based on recipe
            recipe = Recipe.query.filter_by(product_id=item['product_id']).all()
            for r in recipe:
                raw_material = RawMaterial.query.get(r.raw_material_id)
                raw_material.quantity -= (r.amount * item['quantity'])

                # Check if below threshold
                if raw_material.quantity <= raw_material.alert_threshold:
                    create_notification(
                        user_id=current_user.id,
                        title='Low Stock Alert',
                        message=f'{raw_material.name} is running low ({raw_material.quantity} {raw_material.unit} remaining)',
                        type='warning'
                    )

        # Calculate and add loyalty points
        if order.client_id:
            points = calculate_loyalty_points(order.total)
            order.loyalty_points_earned = points
            client = Client.query.get(order.client_id)
            client.loyalty_points += points
            client.total_spent += order.total
            client.last_visit = datetime.now(timezone.utc)

        db.session.add(order)
        db.session.commit()

        # Generate PDF invoice
        invoice = InvoiceGenerator(order)
        invoice_path = invoice.generate()

        log_activity(current_user.id, 'create', 'order', order.id)

        return jsonify({
            'success': True,
            'order_id': order.id,
            'invoice_path': invoice_path
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_invoice_number():
    # Generate a unique invoice number based on date and sequence
    today = datetime.now(timezone.utc).strftime('%Y%m%d')
    last_order = Order.query.filter(
        Order.invoice_number.like(f'{today}%')
    ).order_by(Order.invoice_number.desc()).first()

    if last_order:
        sequence = int(last_order.invoice_number[-4:]) + 1
    else:
        sequence = 1

    return f'{today}{sequence:04d}'

@app.route('/api/settings/save', methods=['POST'])
@login_required
def save_settings():
    try:
        settings = request.json
        branch = Branch.query.filter_by(id=current_user.branch_id).first()

        if not branch:
            return jsonify({'success': False, 'message': 'Branch not found'}), 404

        # Update branch settings
        branch.weight_unit = settings['general']['weight_unit']
        branch.currency = settings['general']['currency']
        branch.time_format = settings['general']['time_format']
        branch.order_types = settings['general']['order_types']
        branch.invoice_template = settings['general']['invoice']['template']
        branch.invoice_fields = settings['general']['invoice']['fields']

        # Update operational settings
        branch.pos_printer = settings['operational']['printers']['pos']
        branch.barcode_printer = settings['operational']['printers']['barcode']
        branch.device_type = settings['operational']['hardware']['device_type']
        branch.quick_pos_mode = settings['operational']['hardware']['quick_pos']
        branch.shift_closing_time = settings['operational']['shift']['closing_time']
        branch.shift_report = settings['operational']['shift']['report']

        # Update integration settings
        branch.whatsapp_api = settings['integration']['whatsapp']['api_key']
        branch.whatsapp_notifications = settings['integration']['whatsapp']['notifications']
        branch.sms_api = settings['integration']['sms']['api_key']
        branch.sms_notifications = settings['integration']['sms']['notifications']

        # Update AI settings
        branch.ai_analytics = settings['ai']['analytics']
        branch.sales_prediction = settings['ai']['sales_prediction']
        branch.inventory_prediction = settings['ai']['inventory_prediction']

        db.session.commit()

        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/settings/get', methods=['GET'])
@login_required
def get_settings():
    try:
        branch = Branch.query.filter_by(id=current_user.branch_id).first()

        if not branch:
            return jsonify({'success': False, 'message': 'Branch not found'}), 404

        settings = {
            'general': {
                'weight_unit': getattr(branch, 'weight_unit', ''),
                'currency': getattr(branch, 'currency', ''),
                'time_format': getattr(branch, 'time_format', ''),
                'order_types': getattr(branch, 'order_types', ''),
                'invoice': {
                    'template': getattr(branch, 'invoice_template', ''),
                    'fields': getattr(branch, 'invoice_fields', '')
                }
            },
            'operational': {
                'printers': {
                    'pos': getattr(branch, 'pos_printer', ''),
                    'barcode': getattr(branch, 'barcode_printer', '')
                },
                'hardware': {
                    'device_type': getattr(branch, 'device_type', ''),
                    'quick_pos': getattr(branch, 'quick_pos_mode', False)
                },
                'shift': {
                    'closing_time': getattr(branch, 'shift_closing_time', ''),
                    'report': getattr(branch, 'shift_report', '')
                }
            },
            'integration': {
                'whatsapp': {
                    'api_key': getattr(branch, 'whatsapp_api', ''),
                    'notifications': getattr(branch, 'whatsapp_notifications', False)
                },
                'sms': {
                    'api_key': getattr(branch, 'sms_api', ''),
                    'notifications': getattr(branch, 'sms_notifications', False)
                }
            },
            'ai': {
                'analytics': getattr(branch, 'ai_analytics', False),
                'sales_prediction': getattr(branch, 'sales_prediction', False),
                'inventory_prediction': getattr(branch, 'inventory_prediction', False)
            }
        }

        return jsonify({'success': True, 'settings': settings})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Role and Permission Management Routes
@app.route('/roles')
@login_required
@require_permission('manage_roles')
def roles():
    roles = Role.query.all()
    return render_template('roles.html', roles=roles)

@app.route('/roles/add', methods=['GET', 'POST'])
@login_required
@require_permission('manage_roles')
def add_role():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        permissions = request.form.getlist('permissions')

        if Role.query.filter_by(name=name).first():
            flash('هذا الدور موجود بالفعل', 'error')
            return redirect(url_for('add_role'))

        role = Role(
            name=name,
            description=description,
            is_system=False
        )

        # Add permissions
        for perm_name in permissions:
            permission = Permission.query.filter_by(name=perm_name).first()
            if permission:
                role.permissions.append(permission)

        db.session.add(role)
        db.session.commit()

        flash('تم إضافة الدور بنجاح', 'success')
        return redirect(url_for('roles'))

    # Get all available permissions grouped by module
    permissions = {}
    for module, perms in DEFAULT_PERMISSIONS.items():
        permissions[module] = [
            Permission.query.filter_by(name=perm[0]).first()
            for perm in perms
        ]

    return render_template('add_role.html', permissions=permissions)

@app.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('manage_roles')
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)

    if role.is_system:
        flash('لا يمكن تعديل الأدوار النظامية', 'error')
        return redirect(url_for('roles'))

    if request.method == 'POST':
        role.name = request.form.get('name')
        role.description = request.form.get('description')

        # Update permissions
        role.permissions = []
        for perm_name in request.form.getlist('permissions'):
            permission = Permission.query.filter_by(name=perm_name).first()
            if permission:
                role.permissions.append(permission)

        db.session.commit()
        flash('تم تحديث الدور بنجاح', 'success')
        return redirect(url_for('roles'))

    # Get all available permissions grouped by module
    permissions = {}
    for module, perms in DEFAULT_PERMISSIONS.items():
        permissions[module] = [
            Permission.query.filter_by(name=perm[0]).first()
            for perm in perms
        ]

    return render_template('edit_role.html', role=role, permissions=permissions)

@app.route('/roles/<int:role_id>/delete', methods=['POST'])
@login_required
@require_permission('manage_roles')
def delete_role(role_id):
    role = Role.query.get_or_404(role_id)

    if role.is_system:
        flash('لا يمكن حذف الأدوار النظامية', 'error')
        return redirect(url_for('roles'))

    if role.users:
        flash('لا يمكن حذف دور مرتبط بمستخدمين', 'error')
        return redirect(url_for('roles'))

    db.session.delete(role)
    db.session.commit()
    flash('تم حذف الدور بنجاح', 'success')
    return redirect(url_for('roles'))

@app.route('/users/<int:user_id>/roles', methods=['GET', 'POST'])
@login_required
@require_permission('manage_users')
def manage_user_roles(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Update user roles
        user.roles = []
        for role_id in request.form.getlist('roles'):
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)

        db.session.commit()
        flash('تم تحديث أدوار المستخدم بنجاح', 'success')
        return redirect(url_for('manage_user_roles', user_id=user_id))

    roles = Role.query.all()
    return render_template('manage_user_roles.html', user=user, roles=roles)

if __name__ == "__main__":
    print("\n--- Registered Routes ---")
    for route in list_routes(app):
        print(route)
    app.run(debug=True)
