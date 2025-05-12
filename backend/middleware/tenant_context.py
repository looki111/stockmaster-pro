"""
Tenant Context Middleware for StockMaster Pro
Handles tenant isolation and context management
"""

from functools import wraps
from flask import g, request, redirect, url_for, flash, current_app, session
from flask_login import current_user
from backend.database.subscription_models import Shop
import threading

# Thread-local storage for tenant context
_tenant_context = threading.local()

class TenantContext:
    """
    Tenant Context Manager for StockMaster Pro
    Handles tenant isolation and context management
    """

    @staticmethod
    def get_current_tenant():
        """
        Get the current tenant (shop) from thread-local storage

        Returns:
            Shop: Current tenant (shop)
        """
        return getattr(_tenant_context, 'tenant', None)

    @staticmethod
    def set_current_tenant(tenant):
        """
        Set the current tenant (shop) in thread-local storage

        Args:
            tenant: Shop model instance
        """
        _tenant_context.tenant = tenant

    @staticmethod
    def clear_current_tenant():
        """
        Clear the current tenant (shop) from thread-local storage
        """
        if hasattr(_tenant_context, 'tenant'):
            delattr(_tenant_context, 'tenant')

    @staticmethod
    def tenant_context_middleware():
        """
        Middleware function to set tenant context for each request
        """
        def middleware():
            # Skip for static files and auth routes
            if (request.path.startswith('/static') or
                request.path.startswith('/auth') or
                request.path == '/'):
                return None

            # Check if user is authenticated
            if not current_user.is_authenticated:
                TenantContext.clear_current_tenant()
                return None

            # Check if user has a branch
            if not current_user.branch:
                TenantContext.clear_current_tenant()
                return None

            # Check if branch has a shop
            if not current_user.branch.shop_id:
                TenantContext.clear_current_tenant()
                return None

            # Get shop and set as current tenant
            shop = Shop.query.get(current_user.branch.shop_id)
            if not shop:
                TenantContext.clear_current_tenant()
                return None

            # Set current tenant in thread-local storage and Flask g
            TenantContext.set_current_tenant(shop)
            g.tenant = shop

            # Set tenant-specific session data
            if 'tenant_id' not in session or session['tenant_id'] != shop.id:
                session['tenant_id'] = shop.id
                session['tenant_name'] = shop.name
                session['tenant_primary_color'] = shop.primary_color
                session['tenant_logo'] = shop.logo

            return None

        return middleware

    @staticmethod
    def tenant_required(f):
        """
        Decorator to ensure a tenant context is available

        Args:
            f: Function to decorate

        Returns:
            Decorated function
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            tenant = TenantContext.get_current_tenant()
            if not tenant:
                flash('No tenant context available', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def tenant_filter(query, model):
        """
        Apply tenant filter to a query

        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model

        Returns:
            Filtered query
        """
        tenant = TenantContext.get_current_tenant()
        if not tenant:
            # If no tenant context, return empty query
            return query.filter(False)

        # Apply tenant filter based on model
        if hasattr(model, 'shop_id'):
            # Model has direct shop_id foreign key
            return query.filter(model.shop_id == tenant.id)
        elif hasattr(model, 'branch_id') and hasattr(model, 'branch'):
            # Model has branch_id foreign key
            return query.join(model.branch).filter(model.branch.has(shop_id=tenant.id))
        elif hasattr(model, 'user_id') and hasattr(model, 'user'):
            # Model has user_id foreign key
            return query.join(model.user).join(model.user.branch).filter(model.user.branch.has(shop_id=tenant.id))
        else:
            # No tenant relationship found, return empty query
            current_app.logger.warning(f"No tenant relationship found for model {model.__name__}")
            return query.filter(False)

    @staticmethod
    def get_tenant_branches():
        """
        Get all branches for the current tenant

        Returns:
            list: List of Branch model instances
        """
        tenant = TenantContext.get_current_tenant()
        if not tenant:
            return []

        return tenant.branches

    @staticmethod
    def get_tenant_users():
        """
        Get all users for the current tenant

        Returns:
            list: List of User model instances
        """
        tenant = TenantContext.get_current_tenant()
        if not tenant:
            return []

        from backend.database.models import User, Branch
        return User.query.join(Branch).filter(Branch.shop_id == tenant.id).all()

    @staticmethod
    def get_tenant_branding():
        """
        Get branding information for the current tenant

        Returns:
            dict: Tenant branding information
        """
        tenant = TenantContext.get_current_tenant()
        if not tenant:
            return {
                'name': 'StockMaster Pro',
                'logo': '/static/images/logo.png',
                'primary_color': '#4A90E2',
                'secondary_color': '#FFA726',
                'accent_color': '#4CAF50',
                'font_family': "'Cairo', sans-serif"
            }

        return {
            'name': tenant.name,
            'logo': tenant.logo or '/static/images/logo.png',
            'primary_color': tenant.primary_color or '#4A90E2',
            'secondary_color': tenant.secondary_color or '#FFA726',
            'accent_color': tenant.accent_color or '#4CAF50',
            'font_family': tenant.font_family or "'Cairo', sans-serif"
        }

def apply_tenant_context_middleware(app):
    """
    Apply tenant context middleware to the Flask app

    Args:
        app: Flask app
    """
    app.before_request(TenantContext.tenant_context_middleware())

    # Add tenant context to template context
    @app.context_processor
    def inject_tenant_context():
        tenant = TenantContext.get_current_tenant()
        if tenant:
            return {
                'tenant': tenant,
                'tenant_branding': TenantContext.get_tenant_branding()
            }
        return {}
