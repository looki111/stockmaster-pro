from database.models import Permission, Role
from database.db_setup import db
from flask_login import current_user
from functools import wraps
from flask import abort

# Default permissions grouped by module
DEFAULT_PERMISSIONS = {
    'inventory': [
        ('view_inventory', 'View inventory'),
        ('edit_inventory', 'Edit inventory'),
        ('manage_inventory', 'Manage inventory'),
        ('view_raw_materials', 'View raw materials'),
        ('edit_raw_materials', 'Edit raw materials'),
        ('manage_raw_materials', 'Manage raw materials'),
        ('view_recipes', 'View recipes'),
        ('edit_recipes', 'Edit recipes'),
        ('manage_recipes', 'Manage recipes'),
        ('view_transfers', 'View transfers'),
        ('create_transfer', 'Create transfer'),
        ('approve_transfer', 'Approve transfer'),
        ('manage_transfers', 'Manage transfers')
    ],
    'sales': [
        ('view_sales', 'View sales'),
        ('create_sale', 'Create sale'),
        ('edit_sale', 'Edit sale'),
        ('delete_sale', 'Delete sale'),
        ('manage_sales', 'Manage sales'),
        ('view_orders', 'View orders'),
        ('create_order', 'Create order'),
        ('edit_order', 'Edit order'),
        ('delete_order', 'Delete order'),
        ('manage_orders', 'Manage orders')
    ],
    'products': [
        ('view_products', 'View products'),
        ('create_product', 'Create product'),
        ('edit_product', 'Edit product'),
        ('delete_product', 'Delete product'),
        ('manage_products', 'Manage products')
    ],
    'clients': [
        ('view_clients', 'View clients'),
        ('create_client', 'Create client'),
        ('edit_client', 'Edit client'),
        ('delete_client', 'Delete client'),
        ('manage_clients', 'Manage clients'),
        ('view_loyalty', 'View loyalty program'),
        ('manage_loyalty', 'Manage loyalty program')
    ],
    'vendors': [
        ('view_vendors', 'View vendors'),
        ('create_vendor', 'Create vendor'),
        ('edit_vendor', 'Edit vendor'),
        ('delete_vendor', 'Delete vendor'),
        ('manage_vendors', 'Manage vendors')
    ],
    'reports': [
        ('view_reports', 'View reports'),
        ('export_reports', 'Export reports'),
        ('manage_reports', 'Manage reports')
    ],
    'settings': [
        ('view_settings', 'View settings'),
        ('edit_settings', 'Edit settings'),
        ('manage_settings', 'Manage settings'),
        ('view_branches', 'View branches'),
        ('create_branch', 'Create branch'),
        ('edit_branch', 'Edit branch'),
        ('delete_branch', 'Delete branch'),
        ('manage_branches', 'Manage branches')
    ],
    'pos': [
        ('use_pos', 'Use POS'),
        ('manage_pos', 'Manage POS'),
        ('view_shift', 'View shift'),
        ('close_shift', 'Close shift'),
        ('manage_shifts', 'Manage shifts')
    ],
    'marketing': [
        ('view_promotions', 'View promotions'),
        ('create_promotion', 'Create promotion'),
        ('edit_promotion', 'Edit promotion'),
        ('delete_promotion', 'Delete promotion'),
        ('manage_promotions', 'Manage promotions'),
        ('view_campaigns', 'View campaigns'),
        ('create_campaign', 'Create campaign'),
        ('edit_campaign', 'Edit campaign'),
        ('delete_campaign', 'Delete campaign'),
        ('manage_campaigns', 'Manage campaigns')
    ]
}

# Default roles with their permissions
DEFAULT_ROLES = {
    'superuser': {
        'description': 'Superuser with full access',
        'is_system': True,
        'permissions': [perm[0] for perms in DEFAULT_PERMISSIONS.values() for perm in perms]
    },
    'manager': {
        'description': 'Branch manager with full branch access',
        'is_system': True,
        'permissions': [
            'view_inventory', 'edit_inventory', 'manage_inventory',
            'view_raw_materials', 'edit_raw_materials', 'manage_raw_materials',
            'view_recipes', 'edit_recipes', 'manage_recipes',
            'view_sales', 'create_sale', 'edit_sale', 'manage_sales',
            'view_orders', 'create_order', 'edit_order', 'manage_orders',
            'view_products', 'create_product', 'edit_product', 'manage_products',
            'view_clients', 'create_client', 'edit_client', 'manage_clients',
            'view_loyalty', 'manage_loyalty',
            'view_vendors', 'create_vendor', 'edit_vendor', 'manage_vendors',
            'view_reports', 'export_reports',
            'view_settings', 'edit_settings',
            'view_branches', 'edit_branch',
            'use_pos', 'manage_pos',
            'view_shift', 'close_shift', 'manage_shifts',
            'view_promotions', 'create_promotion', 'edit_promotion', 'manage_promotions',
            'view_campaigns', 'create_campaign', 'edit_campaign', 'manage_campaigns'
        ]
    },
    'cashier': {
        'description': 'Cashier with POS and basic sales access',
        'is_system': True,
        'permissions': [
            'view_inventory',
            'view_products',
            'view_sales', 'create_sale',
            'view_orders', 'create_order',
            'view_clients',
            'view_loyalty',
            'use_pos',
            'view_shift', 'close_shift'
        ]
    },
    'inventory_manager': {
        'description': 'Inventory manager with full inventory access',
        'is_system': True,
        'permissions': [
            'view_inventory', 'edit_inventory', 'manage_inventory',
            'view_raw_materials', 'edit_raw_materials', 'manage_raw_materials',
            'view_recipes', 'edit_recipes', 'manage_recipes',
            'view_products', 'create_product', 'edit_product', 'manage_products',
            'view_transfers', 'create_transfer', 'approve_transfer', 'manage_transfers',
            'view_reports', 'export_reports'
        ]
    },
    'accountant': {
        'description': 'Accountant with financial and reporting access',
        'is_system': True,
        'permissions': [
            'view_sales', 'view_orders',
            'view_reports', 'export_reports',
            'view_shift', 'close_shift',
            'view_settings'
        ]
    }
}

def init_roles_and_permissions(app):
    """Initialize default roles and permissions"""
    with app.app_context():
        # Create permissions
        for module, permissions in DEFAULT_PERMISSIONS.items():
            for perm_name, perm_desc in permissions:
                permission = Permission.query.filter_by(name=perm_name).first()
                if not permission:
                    permission = Permission(
                        name=perm_name,
                        description=perm_desc,
                        module=module
                    )
                    db.session.add(permission)

        # Create roles
        for role_name, role_data in DEFAULT_ROLES.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(
                    name=role_name,
                    description=role_data['description'],
                    is_system=role_data['is_system']
                )
                db.session.add(role)
                db.session.flush()  # Flush to get role.id

                # Add permissions to role
                for perm_name in role_data['permissions']:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)

        db.session.commit()

def require_permission(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            user_permissions = set()
            for role in current_user.roles:
                user_permissions.update([perm.name for perm in role.permissions])
            if permission_name not in user_permissions:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_permissions(user):
    """Return a set of all permission names for a user."""
    permissions = set()
    if not user or not hasattr(user, 'roles'):
        return permissions
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)
    return permissions
