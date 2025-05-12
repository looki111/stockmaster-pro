"""
Subscription Middleware for StockMaster Pro
Checks subscription status during authentication and request handling
"""

from functools import wraps
from flask import redirect, url_for, flash, request, g, current_app, jsonify
from flask_login import current_user
from database.subscription_models import Shop
import logging

def subscription_required(f):
    """
    Decorator to check if the user's shop has an active subscription.
    If not, redirects to the subscription renewal page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip check for admin routes and subscription-related routes
        if (request.path.startswith('/admin') or
            request.path.startswith('/subscription') or
            request.path.startswith('/auth') or
            request.path == '/'):
            return f(*args, **kwargs)

        # Skip check for static files
        if request.path.startswith('/static'):
            return f(*args, **kwargs)

        # Skip check for API endpoints that need to work regardless of subscription
        if request.path.startswith('/api/subscription'):
            return f(*args, **kwargs)

        # Check if user is authenticated
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

        # Check if user has a branch
        if not current_user.branch:
            flash('Your account is not associated with any branch', 'error')
            return redirect(url_for('auth.logout'))

        # Check if branch has a shop
        if not current_user.branch.shop_id:
            flash('Your branch is not associated with any shop', 'error')
            return redirect(url_for('auth.logout'))

        # Get shop and check subscription
        shop = Shop.query.get(current_user.branch.shop_id)
        if not shop:
            flash('Shop not found', 'error')
            return redirect(url_for('auth.logout'))

        # Check if shop has an active subscription
        if not shop.has_active_subscription:
            flash('Your subscription has expired. Please renew to continue using the system.', 'warning')
            return redirect(url_for('subscription.renew_subscription'))

        # Store shop in g for use in the request
        g.shop = shop

        return f(*args, **kwargs)

    return decorated_function

def check_subscription_limits(f):
    """
    Decorator to check if the shop has reached its subscription limits.
    Checks limits for branches, users, and products.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip check for admin routes and subscription-related routes
        if (request.path.startswith('/admin') or
            request.path.startswith('/subscription') or
            request.path.startswith('/auth') or
            request.path == '/'):
            return f(*args, **kwargs)

        # Skip check for static files
        if request.path.startswith('/static'):
            return f(*args, **kwargs)

        # Check if user is authenticated
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

        # Check if user has a branch and shop
        if not current_user.branch or not current_user.branch.shop_id:
            return f(*args, **kwargs)  # Let the subscription_required decorator handle this

        # Get shop and subscription
        shop = Shop.query.get(current_user.branch.shop_id)
        if not shop or not shop.subscription or not shop.subscription.plan:
            return f(*args, **kwargs)  # Let the subscription_required decorator handle this

        # Check limits based on the request path and method
        subscription = shop.subscription
        plan = subscription.plan

        # Check branch limit for branch creation
        if request.path.endswith('/branch/create') and request.method == 'POST':
            from database.models import Branch
            branch_count = Branch.query.filter_by(shop_id=shop.id).count()
            if branch_count >= plan.max_branches:
                flash(f'You have reached the maximum number of branches ({plan.max_branches}) allowed in your subscription plan.', 'error')
                return redirect(url_for('settings'))

        # Check user limit for user creation
        if request.path.endswith('/user/create') and request.method == 'POST':
            from database.models import User, Branch
            # Count users across all branches of the shop
            user_count = User.query.join(Branch).filter(Branch.shop_id == shop.id).count()
            if user_count >= plan.max_users:
                flash(f'You have reached the maximum number of users ({plan.max_users}) allowed in your subscription plan.', 'error')
                return redirect(url_for('settings'))

        # Check product limit for product creation
        if (request.path.endswith('/product/create') or request.path.endswith('/raw_materials')) and request.method == 'POST':
            from database.models import Product, Branch
            # Count products across all branches of the shop
            product_count = Product.query.join(Branch).filter(Branch.shop_id == shop.id).count()
            if product_count >= plan.max_products:
                flash(f'You have reached the maximum number of products ({plan.max_products}) allowed in your subscription plan.', 'error')
                return redirect(url_for('raw_materials'))

        # Check feature access based on subscription plan
        features = plan.features or {}

        # POS feature check
        if request.path.startswith('/pos') and not features.get('pos', False):
            flash('POS feature is not available in your subscription plan.', 'error')
            return redirect(url_for('dashboard'))

        # Reports feature check
        if request.path.startswith('/reports') and not features.get('reports', False):
            flash('Reports feature is not available in your subscription plan.', 'error')
            return redirect(url_for('dashboard'))

        # Marketing feature check
        if request.path.startswith('/marketing') and not features.get('marketing', False):
            flash('Marketing feature is not available in your subscription plan.', 'error')
            return redirect(url_for('dashboard'))

        # AI feature check
        if request.path.startswith('/ai') and not features.get('ai', False):
            flash('AI features are not available in your subscription plan.', 'error')
            return redirect(url_for('dashboard'))

        # API feature check
        if request.path.startswith('/api') and not features.get('api', False) and not request.path.startswith('/api/subscription'):
            return jsonify({
                'success': False,
                'error': 'API access is not available in your subscription plan.'
            }), 403

        return f(*args, **kwargs)

    return decorated_function

def apply_subscription_middleware(app):
    @app.before_request
    def check_subscription():
        # Skip check for public routes
        public_paths = [
            '/static',
            '/auth/login',
            '/auth/register',
            '/auth/logout',
            '/',
            '/favicon.ico'
        ]
        
        if any(request.path.startswith(path) for path in public_paths):
            return None
            
        # Skip check for non-authenticated users
        if not current_user.is_authenticated:
            return None
            
        try:
            # Check if user has a branch
            if not current_user.branch:
                logging.warning(f"User {current_user.username} has no branch")
                flash('Your account is not associated with any branch', 'error')
                return redirect(url_for('auth.logout'))

            # Check if branch has a shop
            if not current_user.branch.shop:
                logging.warning(f"Branch {current_user.branch.id} has no shop")
                flash('Your branch is not associated with any shop', 'error')
                return redirect(url_for('auth.logout'))

            # Check subscription
            shop = current_user.branch.shop
            if not shop.has_active_subscription:
                logging.info(f"Shop {shop.id} subscription expired")
                flash('Your subscription has expired. Please renew to continue.', 'warning')
                return redirect(url_for('subscription.renew'))

        except Exception as e:
            logging.error(f"Subscription check error: {e}")
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('auth.logout'))
