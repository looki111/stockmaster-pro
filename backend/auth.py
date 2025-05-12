# auth logic here

from functools import wraps
from flask import abort, current_app
from flask_login import current_user

def require_permission(permission_name):
    """Decorator to require a specific permission for a route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not current_user.has_permission(permission_name):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_module_permission(module_name):
    """Decorator to require any permission in a module for a route"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            if not current_user.has_module_permission(module_name):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_branch_access(branch_id):
    """Decorator to require access to a specific branch"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            # Superuser has access to all branches
            if current_user.is_superuser:
                return f(*args, **kwargs)
            
            # Check if user belongs to the branch
            if current_user.branch_id != branch_id:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_role(role_name):
    """Decorator to require a specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            
            # Check if user has the required role
            has_role = any(role.name == role_name for role in current_user.roles)
            if not has_role and not current_user.is_superuser:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_permissions(user):
    """Get all permissions for a user"""
    if user.is_superuser:
        # Superuser has all permissions
        from roles import DEFAULT_PERMISSIONS
        return [perm[0] for module in DEFAULT_PERMISSIONS.values() for perm in module]
    
    # Get permissions from user's roles
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    return list(permissions)

def get_user_modules(user):
    """Get all modules the user has access to"""
    if user.is_superuser:
        # Superuser has access to all modules
        from roles import DEFAULT_PERMISSIONS
        return list(DEFAULT_PERMISSIONS.keys())
    
    # Get modules from user's permissions
    modules = set()
    for role in user.roles:
        for permission in role.permissions:
            modules.add(permission.module)
    return list(modules)
