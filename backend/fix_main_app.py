#!/usr/bin/env python
"""
Fix Main App Script for StockMaster Pro

This script updates the main app.py file to use the patched token verification
to resolve the 500 error during login.
"""

import os
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of a file"""
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak_{timestamp}"
    
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return False

def update_imports_in_file(file_path):
    """Update imports in a file to use the patched token verification"""
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
        
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check if the file already has the patched import
        if "from auth.patched_token_verify import" in content:
            logger.info(f"File {file_path} already has patched import")
            return True
            
        # Replace the import from supabase_auth with patched_token_verify
        if "from auth.supabase_auth import verify_supabase_token" in content:
            # Full path replacement
            content = content.replace(
                "from auth.supabase_auth import verify_supabase_token", 
                "from auth.patched_token_verify import verify_supabase_token"
            )
            
            # If get_token_from_request is also imported, replace that too
            if "get_token_from_request" in content:
                content = content.replace(
                    "from auth.supabase_auth import verify_supabase_token, get_token_from_request", 
                    "from auth.patched_token_verify import verify_supabase_token, get_token_from_request"
                )
                
        # Handle relative import with backend prefix
        elif "from backend.auth.supabase_auth import verify_supabase_token" in content:
            content = content.replace(
                "from backend.auth.supabase_auth import verify_supabase_token", 
                "from backend.auth.patched_token_verify import verify_supabase_token"
            )
            
            # If get_token_from_request is also imported, replace that too
            if "get_token_from_request" in content:
                content = content.replace(
                    "from backend.auth.supabase_auth import verify_supabase_token, get_token_from_request", 
                    "from backend.auth.patched_token_verify import verify_supabase_token, get_token_from_request"
                )
        else:
            logger.warning(f"Could not find supabase_auth import in {file_path}")
            # No changes made
            return False
            
        # Write the updated content back to the file
        with open(file_path, 'w') as f:
            f.write(content)
            
        logger.info(f"Updated imports in {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to update imports in {file_path}: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("StockMaster Pro - Fix Main App".center(80))
    print("=" * 80 + "\n")
    
    # Find the main app files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_paths = [
        os.path.join(base_dir, "app.py"),
        os.path.join(base_dir, "backend", "app.py"),
        os.path.join(base_dir, "fixed_app.py")
    ]
    
    # Also check routes directory files
    routes_dir = os.path.join(base_dir, "backend", "routes")
    if os.path.exists(routes_dir) and os.path.isdir(routes_dir):
        for file in os.listdir(routes_dir):
            if file.endswith(".py"):
                app_paths.append(os.path.join(routes_dir, file))
                
    # Count of files updated
    updated_count = 0
    
    # Update each file
    for app_path in app_paths:
        if os.path.exists(app_path):
            print(f"Updating {app_path}...")
            
            # Create backup
            if backup_file(app_path):
                # Update imports
                if update_imports_in_file(app_path):
                    updated_count += 1
                    print(f"✅ Successfully updated {app_path}")
                else:
                    print(f"⚠️ No changes made to {app_path}")
            else:
                print(f"❌ Failed to create backup of {app_path}")
        else:
            print(f"⚠️ File not found: {app_path}")
    
    # Summary
    print("\n" + "-" * 80)
    if updated_count > 0:
        print(f"✅ Successfully updated {updated_count} files to use patched token verification.")
        print("\nNext steps:")
        print("  1. Restart your Flask application")
        print("  2. Try logging in again - the 500 error should be resolved")
    else:
        print("⚠️ No files were updated. Please check the log for details.")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main() 