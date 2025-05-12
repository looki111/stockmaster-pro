import os
import sys
import re
from pathlib import Path

def fix_auth_blueprint_registration():
    """
    Modifies app.py to ensure auth_bp is registered with the correct URL prefix
    """
    app_py_path = Path('./app.py')
    
    # Make sure the file exists
    if not app_py_path.exists():
        print(f"Error: {app_py_path} not found.")
        return False
    
    # Read the file
    content = app_py_path.read_text()
    
    # Find the auth blueprint registration
    auth_bp_pattern = r'app\.register_blueprint\(auth_bp(?:\s*,\s*(?:url_prefix\s*=\s*[\'"].*?[\'"])?)?\)'
    match = re.search(auth_bp_pattern, content)
    
    if match:
        # If found, replace with the correct registration
        replacement = 'app.register_blueprint(auth_bp, url_prefix="/auth")'
        new_content = content.replace(match.group(0), replacement)
        
        # Write the modified content back
        app_py_path.write_text(new_content)
        print("Successfully updated auth blueprint registration with url_prefix='/auth'")
        return True
    else:
        print("Could not find auth blueprint registration pattern in app.py")
        return False

def print_fix_instructions():
    """
    Provides instructions for manually fixing the issue
    """
    print("\nTo manually fix the login route issue:")
    print("1. Open app.py")
    print("2. Find the line: app.register_blueprint(auth_bp)")
    print("3. Replace it with: app.register_blueprint(auth_bp, url_prefix='/auth')")
    print("\nAlternatively, make sure you're accessing the login page at /auth/login")
    print("The login form action should be set to '/auth/login' as well.")

def main():
    print("Fixing auth blueprint registration to use correct URL prefix...")
    fixed = fix_auth_blueprint_registration()
    
    # Print instructions regardless of success
    print_fix_instructions()
    
    if fixed:
        print("\nLogin should now be accessible at /auth/login")
        print("Please restart the Flask application for changes to take effect.")
    else:
        print("\nFailed to automatically fix the issue.")
        print("Please follow the manual instructions above.")

if __name__ == "__main__":
    main() 