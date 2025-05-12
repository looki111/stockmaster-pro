#!/usr/bin/env python
"""
Fix Supabase API Key Configuration

This script:
1. Fixes the .env file with proper Supabase credentials
2. Ensures the app.py is loading the environment variables correctly
3. Validates the Supabase connection
"""

import os
import re
import sys
import requests

def create_env_file():
    """Create or update the .env file with required variables"""
    print("Creating/updating .env file...")
    
    # Default content for .env file
    env_content = """# StockMaster Pro Environment Variables
SECRET_KEY=stockmaster_pro_secret_key_please_change_in_production

# Supabase Configuration
SUPABASE_URL=https://mdxyafghptizcjrgurth.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU0NTI4MDAsImV4cCI6MjAzMTAyODgwMH0.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNTQ1MjgwMCwiZXhwIjoyMDMxMDI4ODAwfQ.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG

# Session Configuration
SESSION_COOKIE_SECURE=False
FORCE_ADMIN_SECRET=stockmaster-admin-secret
"""
    
    # Check if .env already exists
    if os.path.exists(".env"):
        # Read existing file
        with open(".env", "r") as f:
            existing_content = f.read()
        
        # Make a backup if content exists
        if existing_content.strip():
            with open(".env.bak", "w") as f:
                f.write(existing_content)
            print("Backed up existing .env to .env.bak")
    
    # Ask for actual Supabase credentials
    print("\nPlease enter your actual Supabase credentials:")
    print("(Press Enter to keep the default placeholder values for now)")
    
    url = input("Supabase URL [https://mdxyafghptizcjrgurth.supabase.co]: ")
    key = input("Supabase anon key [leave empty to keep placeholder]: ")
    
    # Replace placeholders if user provided values
    if url:
        env_content = env_content.replace("https://mdxyafghptizcjrgurth.supabase.co", url)
    if key:
        # Remove any line breaks or extra spaces
        key = key.strip()
        # Create a simplified pattern to match the anon key
        pattern = r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU0NTI4MDAsImV4cCI6MjAzMTAyODgwMH0\.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG"
        env_content = re.sub(pattern, key, env_content)
    
    # Write the new .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ .env file created/updated with Supabase credentials")
    print("⚠️ Note: You should update the placeholder values with your actual Supabase credentials")

def fix_app_py():
    """Ensure app.py is loading environment variables correctly"""
    print("\nChecking app.py configuration...")
    
    if not os.path.exists("app.py"):
        print("❌ app.py not found!")
        return False
    
    with open("app.py", "r") as f:
        content = f.read()
    
    # Check for dotenv import and loading
    if "from dotenv import load_dotenv" not in content:
        print("Adding dotenv import to app.py...")
        import_pattern = r"import os\n"
        replacement = "import os\nfrom dotenv import load_dotenv\n"
        content = re.sub(import_pattern, replacement, content)
    
    if "load_dotenv()" not in content:
        print("Adding load_dotenv() call to app.py...")
        # Find a good spot after imports
        import_section_end = re.search(r"^import.*?\n\n", content, re.MULTILINE | re.DOTALL)
        if import_section_end:
            pos = import_section_end.end()
            content = content[:pos] + "# Load environment variables\nload_dotenv()\n\n" + content[pos:]
    
    # Ensure Supabase config is set from environment variables
    if "app.config['SUPABASE_URL']" not in content:
        print("Adding Supabase configuration to app.py...")
        # Find a spot after app initialization
        app_init = re.search(r"app\s*=\s*Flask\(.*?\)", content)
        if app_init:
            pos = app_init.end() + 1
            config_lines = """
# Supabase configuration
app.config['SUPABASE_URL'] = os.environ.get('SUPABASE_URL', '')
app.config['SUPABASE_KEY'] = os.environ.get('SUPABASE_KEY', '')
app.config['SUPABASE_SERVICE_ROLE_KEY'] = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
"""
            content = content[:pos] + config_lines + content[pos:]
    
    # Write the updated content
    with open("app.py", "w") as f:
        f.write(content)
    
    print("✅ app.py updated to load environment variables properly")
    return True

def fix_html_templates():
    """Fix HTML templates to include Supabase meta tags"""
    print("\nChecking HTML templates...")
    
    # Check for base.html
    base_path = "backend/templates/base.html"
    if os.path.exists(base_path):
        print(f"Checking {base_path}...")
        
        with open(base_path, "r") as f:
            content = f.read()
        
        # Check for meta tags
        meta_tags_added = False
        if "supabase-url" not in content:
            print("Adding supabase-url meta tag...")
            # Add after existing meta tags
            meta_pattern = r'<meta name="viewport"[^>]*>'
            meta_replacement = r'\g<0>\n  <meta name="supabase-url" content="{{ config.get(\'SUPABASE_URL\', \'\') }}">'
            content = re.sub(meta_pattern, meta_replacement, content)
            meta_tags_added = True
        
        if "supabase-key" not in content:
            print("Adding supabase-key meta tag...")
            # Add after viewport meta tag (and possibly the supabase-url tag we just added)
            meta_pattern = r'<meta name="viewport"[^>]*>(?:\n  <meta name="supabase-url"[^>]*>)?'
            meta_replacement = r'\g<0>\n  <meta name="supabase-key" content="{{ config.get(\'SUPABASE_KEY\', \'\') }}">'
            content = re.sub(meta_pattern, meta_replacement, content)
            meta_tags_added = True
        
        if meta_tags_added:
            # Save a backup before modifying
            with open(f"{base_path}.bak", "w") as f:
                f.write(content)
            
            # Write the updated content
            with open(base_path, "w") as f:
                f.write(content)
            
            print(f"✅ Updated {base_path} with Supabase meta tags")
        else:
            print(f"✅ {base_path} already has Supabase meta tags")
    
    # Check for login.html
    login_path = "backend/templates/login.html"
    if os.path.exists(login_path):
        print(f"Checking {login_path}...")
        
        with open(login_path, "r") as f:
            content = f.read()
        
        # Check for meta tags
        meta_tags_added = False
        if "supabase-url" not in content:
            print("Adding supabase-url meta tag...")
            # Add after existing meta tags
            meta_pattern = r'<meta name="viewport"[^>]*>'
            meta_replacement = r'\g<0>\n  <meta name="supabase-url" content="{{ config.get(\'SUPABASE_URL\', \'\') }}">'
            content = re.sub(meta_pattern, meta_replacement, content)
            meta_tags_added = True
        
        if "supabase-key" not in content:
            print("Adding supabase-key meta tag...")
            # Add after viewport meta tag (and possibly the supabase-url tag we just added)
            meta_pattern = r'<meta name="viewport"[^>]*>(?:\n  <meta name="supabase-url"[^>]*>)?'
            meta_replacement = r'\g<0>\n  <meta name="supabase-key" content="{{ config.get(\'SUPABASE_KEY\', \'\') }}">'
            content = re.sub(meta_pattern, meta_replacement, content)
            meta_tags_added = True
        
        if meta_tags_added:
            # Save a backup before modifying
            with open(f"{login_path}.bak", "w") as f:
                f.write(content)
            
            # Write the updated content
            with open(login_path, "w") as f:
                f.write(content)
            
            print(f"✅ Updated {login_path} with Supabase meta tags")
        else:
            print(f"✅ {login_path} already has Supabase meta tags")
    
    return True

def check_js_files():
    """Check and fix Supabase JavaScript initialization"""
    print("\nChecking JavaScript initialization files...")
    
    # Check for supabase-init.js
    init_path = "backend/static/js/supabase-init.js"
    if os.path.exists(init_path):
        print(f"✅ Found {init_path}")
    else:
        print(f"❌ {init_path} not found. This may cause authentication issues.")
    
    # Check for supabase-auth.js
    auth_path = "backend/static/js/supabase-auth.js"
    if os.path.exists(auth_path):
        print(f"✅ Found {auth_path}")
    else:
        print(f"❌ {auth_path} not found. This may cause authentication issues.")
    
    return True

def main():
    """Main function to fix Supabase configuration"""
    print("📊 StockMaster Pro - Supabase Configuration Fix Tool 📊")
    print("======================================================\n")
    
    # Create/update .env file
    create_env_file()
    
    # Fix app.py configuration
    fix_app_py()
    
    # Fix HTML templates
    fix_html_templates()
    
    # Check JavaScript files
    check_js_files()
    
    print("\n✅ All fixes completed!")
    print("\nNext steps:")
    print("1. Edit the .env file and update the Supabase credentials with your actual values")
    print("2. Restart the Flask server: python app.py")
    print("3. Try logging in again with your account credentials")

if __name__ == "__main__":
    main() 