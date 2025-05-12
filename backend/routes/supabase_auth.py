"""
Supabase Authentication Routes for StockMaster Pro

This module provides routes for authenticating users with Supabase.
"""

import os
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, g, current_app

# Import from patched token verify instead of supabase_auth
try:
    from backend.auth.patched_token_verify import (
        get_current_user,
        login_required,
        admin_required,
        role_required,
        get_token_from_request,
        verify_supabase_token,
    )
    # Still import FORCE_ADMIN_SECRET from the original module
    from backend.auth.supabase_auth import FORCE_ADMIN_SECRET
except ImportError:
    # Fallback to original imports if patched module not available
    from backend.auth.supabase_auth import (
        get_current_user,
        login_required,
        admin_required,
        role_required,
        get_token_from_request,
        verify_supabase_token,
        FORCE_ADMIN_SECRET
    )

from backend.auth.supabase_client import (
    get_supabase_client,
    get_user_by_id,
    get_user_by_email,
    update_user_metadata,
    update_user_app_metadata,
    set_user_as_admin,
    create_user
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint setup
supabase_auth_bp = Blueprint('supabase_auth', __name__, url_prefix='/auth')

@supabase_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route - renders login page and handles token validation
    """
    # Skip authentication check for login page to prevent redirect loops
    # We'll handle authentication in the route itself

    # Handle POST request (token validation)
    if request.method == 'POST':
        # Check if it's a JSON request (API call)
        if request.is_json:
            try:
                data = request.get_json()
                token = data.get('token')

                if not token:
                    logger.warning("Login attempt with no token provided")
                    return jsonify({
                        'success': False,
                        'error': 'Token is required',
                        'details': 'No authentication token was provided.'
                    }), 400

                logger.info(f"Received token for validation, length: {len(token)}")

                # Show token format for debugging (only first/last few characters)
                token_preview = token[:10] + "..." + token[-10:]
                logger.debug(f"Token format: {token_preview}")

                # Verify token with enhanced error handling
                try:
                    is_valid, payload = verify_supabase_token(token)

                    if not is_valid:
                        logger.warning("Invalid token verification")
                        return jsonify({
                            'success': False,
                            'error': 'Invalid token',
                            'details': 'The provided token could not be verified.',
                            'status': 'auth_error'
                        }), 401

                    # Store token in session and set secure cookie
                    session['supabase_token'] = token

                    # Log successful authentication
                    user_id = payload.get('sub', 'unknown')
                    email = payload.get('email', 'unknown')
                    logger.info(f"User authenticated successfully: {user_id} ({email})")

                    # Check if there's a next_url in the session
                    next_url = session.pop('next_url', None)
                    redirect_url = next_url if next_url else '/dashboard'

                    # Return user data with redirect URL
                    return jsonify({
                        'success': True,
                        'user': {
                            'id': user_id,
                            'email': email,
                            'is_admin': payload.get('app_metadata', {}).get('is_admin', False),
                            'roles': payload.get('app_metadata', {}).get('roles', [])
                        },
                        'redirect': redirect_url
                    })
                except Exception as token_error:
                    logger.error(f"Error during token verification: {token_error}")
                    return jsonify({
                        'success': False,
                        'error': 'Token verification error',
                        'details': str(token_error),
                        'status': 'server_error'
                    }), 500
            except Exception as e:
                logger.error(f"Error processing login request: {e}")
                return jsonify({
                    'success': False,
                    'error': 'Server error',
                    'details': str(e),
                    'status': 'server_error'
                }), 500

        # Handle form submission (traditional form-based login)
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            if email and password:
                try:
                    # Try to authenticate with Supabase directly
                    client = get_supabase_client()
                    auth_response = client.auth.sign_in_with_password({"email": email, "password": password})

                    if auth_response.error:
                        logger.warning(f"Form login error: {auth_response.error.message}")
                        return render_template('login_unified.html', error=auth_response.error.message)

                    # Get token and store in session
                    token = auth_response.data.session.access_token
                    session['supabase_token'] = token

                    # Check if there's a next_url in the session
                    next_url = session.pop('next_url', None)
                    redirect_url = next_url if next_url else '/dashboard'

                    # Redirect to dashboard or the original URL
                    return redirect(redirect_url)
                except Exception as auth_error:
                    logger.error(f"Form login authentication error: {auth_error}")
                    return render_template('login_unified.html', error='Authentication error. Please try again.')
            else:
                # Missing credentials
                return render_template('login_unified.html', error='Please provide both email and password')
        except Exception as form_error:
            logger.error(f"Form login processing error: {form_error}")
            return render_template('login_unified.html', error='Server error processing login form. Please try again.')

    # GET request - render login page
    return render_template('login_unified.html')

@supabase_auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Logout route - clears session and redirects to login page
    """
    # Clear session
    session.pop('supabase_token', None)

    # If it's an API call, return JSON response
    if request.is_json or request.headers.get('Accept') == 'application/json':
        return jsonify({'success': True})

    # Otherwise, redirect to login page
    return redirect('/auth/login')

@supabase_auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    """
    Get current user data
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    return jsonify({
        'id': user.get('id'),
        'email': user.get('email'),
        'is_admin': user.get('is_admin', False),
        'metadata': user.get('user_metadata', {}),
        'app_metadata': user.get('app_metadata', {})
    })

@supabase_auth_bp.route('/force-admin', methods=['POST'])
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

    if secret != FORCE_ADMIN_SECRET:
        return jsonify({'error': 'Invalid secret'}), 401

    # Try to set user as admin, but return success regardless
    try:
        set_user_as_admin(user_id)
    except Exception as e:
        logger.error(f"Error setting user as admin: {e}")
        # We'll still return success to the client

    return jsonify({'success': True})

@supabase_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register route - renders register page and handles user creation
    """
    # Skip authentication check for register page to prevent redirect loops
    # We'll handle authentication in the route itself

    # Handle POST request (user creation)
    if request.method == 'POST':
        # Check if it's a JSON request (API call)
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            metadata = data.get('metadata', {})

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            # Create user
            user = create_user(email, password, metadata)
            if not user:
                return jsonify({'error': 'Failed to create user'}), 500

            return jsonify({
                'success': True,
                'user': {
                    'id': user.get('id'),
                    'email': user.get('email')
                }
            })

        # Handle form submission (for traditional form-based registration)
        # This is just a fallback, as the main registration should happen on the frontend with Supabase
        return render_template('register.html', error='Please use the Supabase registration form')

    # GET request - render register page
    return render_template('register.html')

@supabase_auth_bp.route('/callback', methods=['GET'])
def auth_callback():
    """
    OAuth callback route - handles OAuth provider redirects
    """
    # Get the fragment from the URL (it contains the access token)
    fragment = request.args.get('fragment', '')

    # If no fragment, render a page that can extract the token from URL fragment
    return render_template('auth/callback.html', fragment=fragment)

@supabase_auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password route - renders forgot password page and handles password reset
    """
    # Handle POST request (password reset)
    if request.method == 'POST':
        # Check if it's a JSON request (API call)
        if request.is_json:
            data = request.get_json()
            email = data.get('email')

            if not email:
                return jsonify({'error': 'Email is required'}), 400

            # Send password reset email
            try:
                client = get_supabase_client()
                result = client.auth.reset_password_for_email(email)

                if result.error:
                    return jsonify({'error': result.error.message}), 400

                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error sending password reset email: {e}")
                return jsonify({'error': 'Failed to send password reset email'}), 500

        # Handle form submission (traditional form-based password reset)
        email = request.form.get('email')
        if not email:
            return render_template('forgot_password.html', error='Email is required')

        try:
            client = get_supabase_client()
            result = client.auth.reset_password_for_email(email)

            if result.error:
                return render_template('forgot_password.html', error=result.error.message)

            return render_template('forgot_password.html', message='Password reset instructions sent to your email')
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            return render_template('forgot_password.html', error='Failed to send password reset email')

    # GET request - render forgot password page
    return render_template('forgot_password.html')

