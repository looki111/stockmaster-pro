"""
Authentication Package for StockMaster Pro
"""

from .supabase_auth import (
    verify_supabase_token,
    get_current_user,
    login_required,
    admin_required,
    role_required,
    get_token_from_request
)

from .supabase_client import (
    get_supabase_client,
    get_user_by_id,
    get_user_by_email,
    update_user_metadata,
    update_user_app_metadata,
    set_user_as_admin,
    create_user
)

__all__ = [
    'verify_supabase_token',
    'get_current_user',
    'login_required',
    'admin_required',
    'role_required',
    'get_token_from_request',
    'get_supabase_client',
    'get_user_by_id',
    'get_user_by_email',
    'update_user_metadata',
    'update_user_app_metadata',
    'set_user_as_admin',
    'create_user'
]
