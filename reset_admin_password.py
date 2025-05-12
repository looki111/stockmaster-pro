#!/usr/bin/env python
"""
Reset Admin Password or Create Admin User

This script allows you to reset the password for an existing admin user
or create a new admin user if the account doesn't exist.
"""

import os
import sys
import getpass
from dotenv import load_dotenv

# Import Supabase client functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from backend.auth.supabase_client import get_supabase_admin_client, get_user_by_email, create_user, update_user_app_metadata
except ImportError:
    print("❌ Error: Could not import Supabase client functions.")
    print("Make sure the backend/auth/supabase_client.py file exists and contains the required functions.")
    sys.exit(1)

def reset_admin_password():
    """Reset admin password or create admin user"""
    print("\n🔐 StockMaster Pro - Admin Password Reset Tool 🔐\n")
    
    # Load environment variables
    print("Loading environment variables...")
    load_dotenv()
    
    # Check required environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_service_role_key:
        print("❌ Error: Missing required environment variables.")
        print("Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set in your .env file.")
        sys.exit(1)
    
    # Get email and new password
    print("\nPlease enter the admin email and new password:")
    email = input("Email: ").strip()
    if not email:
        print("❌ Email cannot be empty.")
        return
    
    password = getpass.getpass("New password: ")
    if not password:
        print("❌ Password cannot be empty.")
        return
    
    confirm_password = getpass.getpass("Confirm password: ")
    if password != confirm_password:
        print("❌ Passwords do not match.")
        return
    
    # Check if user exists
    try:
        print(f"\nChecking if user {email} exists...")
        admin_client = get_supabase_admin_client()
        user = get_user_by_email(email)
        
        if user:
            print(f"✅ User found with ID: {user.get('id')}")
            
            # Update user's password
            print("Updating password...")
            admin_client.auth.admin.update_user_by_id(
                user.get('id'),
                {"password": password}
            )
            
            # Make sure the user has admin privileges
            print("Ensuring user has admin privileges...")
            update_user_app_metadata(user.get('id'), {"is_admin": True})
            
            print(f"✅ Password updated successfully for {email}")
            print("✅ Admin privileges granted")
            
        else:
            print(f"⚠️ User {email} not found. Creating new admin user...")
            
            # Create new admin user
            new_user = create_user(email, password, {"admin": True})
            
            if new_user:
                # Make sure the user has admin privileges
                update_user_app_metadata(new_user.get('id'), {"is_admin": True})
                
                print(f"✅ Created new admin user: {email}")
                print("✅ Admin privileges granted")
            else:
                print("❌ Failed to create new admin user.")
                return
        
        print("\n🎉 Admin user setup complete!")
        print("You can now log in with the provided credentials.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
if __name__ == "__main__":
    reset_admin_password() 