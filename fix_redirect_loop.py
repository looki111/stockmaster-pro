#!/usr/bin/env python
"""
Fix Redirect Loop Script for StockMaster Pro

This script fixes the infinite redirect loop issue between login and dashboard pages.
"""

import os
import sys
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create a backup of a file"""
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.bak_{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return True
    return False

def fix_middleware_file():
    """Fix the middleware file to prevent redirect loops"""
    middleware_file = "backend/middleware/supabase_middleware.py"
    if not os.path.exists(middleware_file):
        print(f"❌ Error: {middleware_file} not found")
        return False
    
    print(f"🔧 Fixing {middleware_file}...")
    backup_file(middleware_file)
    
    try:
        with open(middleware_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update public routes to include static and test routes
        if "public_routes = [" in content:
            routes_pattern = r"public_routes = \[(.*?)\]"
            routes_match = re.search(routes_pattern, content, re.DOTALL)
            if routes_match:
                routes_text = routes_match.group(1)
                if "'/static/'" not in routes_text and "'/test/supabase'" not in routes_text:
                    updated_routes = """public_routes = [
            '/',
            '/auth/login',
            '/auth/register',
            '/auth/logout',
            '/auth/callback',
            '/auth/reset-password',
            '/auth/forgot-password',
            '/favicon.ico',
            '/static/',  # Add the static directory as a public route
            '/test/supabase',  # Add the test route as a public route
        ]"""
                    content = re.sub(routes_pattern, updated_routes, content, flags=re.DOTALL)
                    print("✅ Updated public routes")
        
        # Fix the route checking logic
        if "request.path.startswith('/static') or" in content:
            old_check = r"if \(request\.path\.startswith\('/static'\) or\s+request\.path in public_routes or\s+request\.path\.startswith\('/api/public/'\)\):"
            new_check = "if any(request.path.startswith(route) for route in public_routes) or request.path.startswith('/static/'):"
            content = re.sub(old_check, new_check, content, flags=re.DOTALL)
            print("✅ Updated route checking logic")
        
        # Add check to prevent redirect loops for unauthenticated users
        if "No token, continue without setting user" in content and "For web routes that require authentication" not in content:
            no_token_pattern = r"# No token, continue without setting user\s+g\.supabase_user = None\s+\s+# Check if this is an API route that should require authentication(.*?)\s+return None"
            no_token_replacement = """# No token, continue without setting user
            g.supabase_user = None
            
            # Check if this is an API route that should require authentication
            if request.path.startswith('/api/') and not request.path.startswith('/api/public/'):
                logger.warning(f"API request without authentication token: {request.path}")
                return jsonify({'error': 'Authentication required'}), 401
                
            # For web routes that require authentication, redirect to login
            if not request.is_xhr and not request.headers.get('Accept') == 'application/json':
                # Don't redirect if already on the login page to prevent loops
                if not request.path == '/auth/login' and not request.path.startswith('/auth/'):
                    logger.info(f"Unauthenticated access to {request.path}, redirecting to login")
                    return redirect('/auth/login')
            
            return None"""
            content = re.sub(no_token_pattern, no_token_replacement, content, flags=re.DOTALL)
            print("✅ Added check for unauthenticated users")
        
        # Update redirect logic for invalid tokens
        if "Only redirect non-AJAX requests" in content:
            invalid_token_pattern = r"# For web routes, redirect to login\s+if not request\.is_xhr and not request\.headers\.get\('Accept'\) == 'application/json':\s+# Only redirect non-AJAX requests\s+logger\.info\(f\"Invalid token for web route, redirecting to login: \{request\.path\}\"\)\s+return redirect\('/auth/login'\)"
            invalid_token_replacement = """# For web routes, redirect to login
                if not request.is_xhr and not request.headers.get('Accept') == 'application/json':
                    # Don't redirect if already on the login page to prevent loops
                    if not request.path == '/auth/login' and not request.path.startswith('/auth/'):
                        logger.info(f"Invalid token for {request.path}, redirecting to login")
                        return redirect('/auth/login')"""
            content = re.sub(invalid_token_pattern, invalid_token_replacement, content, flags=re.DOTALL)
            print("✅ Updated redirect logic for invalid tokens")
        
        # Write the updated content
        with open(middleware_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {middleware_file}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {middleware_file}: {e}")
        return False

def fix_app_file():
    """Fix the app.py file to prevent redirect loops"""
    app_file = "app.py"
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found")
        return False
    
    print(f"🔧 Fixing {app_file}...")
    backup_file(app_file)
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update root route to show landing page instead of redirecting to login
        if "redirect('/auth/login')" in content:
            root_route_pattern = r"@app\.route\('\/'\)\s+def index\(\):.*?if 'username' in session:.*?return redirect\('\/dashboard'\).*?else:.*?return redirect\('\/auth\/login'\).*?\s+"
            root_route_replacement = """@app.route('/')
def index():
    \"\"\"
    Root route - redirects to dashboard if logged in, otherwise shows the landing page
    This route should not be protected by any middleware and should not throw 403 errors
    \"\"\"
    # This route is intentionally simple and not protected by any middleware
    # It should always work and never throw 403 Forbidden errors
    from flask import g
    
    # Check if user is authenticated using g.supabase_user
    user = getattr(g, 'supabase_user', None)
    if user:
        return redirect('/dashboard')  # Redirect to dashboard if logged in
    else:
        # Show landing page (this prevents redirect loops)
        return render_template('landing.html', lang=request.args.get('lang', 'en'))

"""
            content = re.sub(root_route_pattern, root_route_replacement, content, flags=re.DOTALL)
            print("✅ Updated root route to show landing page")
        
        # Update login route to check if user is already logged in
        if "@auth_bp.route('/login'" in content and "Check if user is already logged in" not in content:
            login_route_pattern = r"@auth_bp\.route\('\/login'.*?\s+def login\(\):.*?\s+\"\"\".*?\"\"\".*?\s+"
            login_route_replacement = """@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    \"\"\"
    Login route - handles login form submission and renders login page
    \"\"\"
    # Check if user is already logged in
    from flask import g
    user = getattr(g, 'supabase_user', None)
    if user:
        return redirect('/dashboard')  # Redirect to dashboard if already logged in
    
"""
            content = re.sub(login_route_pattern, login_route_replacement, content, flags=re.DOTALL)
            print("✅ Updated login route to check if user is already logged in")
        
        # Write the updated content
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {app_file}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {app_file}: {e}")
        return False

def main():
    """Fix the redirect loop issue in StockMaster Pro"""
    print("\n" + "=" * 70)
    print("Fixing Redirect Loop Issue in StockMaster Pro".center(70))
    print("=" * 70 + "\n")
    
    middleware_fixed = fix_middleware_file()
    app_fixed = fix_app_file()
    
    if middleware_fixed and app_fixed:
        print("\n✅ Successfully fixed the redirect loop issue!")
        print("\nPlease restart your Flask application to apply the changes.")
    else:
        print("\n⚠️ Some fixes were not applied. Please check the errors above.")
    
    return middleware_fixed and app_fixed

if __name__ == "__main__":
    main() 