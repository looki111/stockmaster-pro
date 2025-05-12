"""
Test Admin Role Script

This script tests setting a user as an admin using the set_user_as_admin function.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the function from supabase_client.py
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))
    from auth.supabase_client import set_user_as_admin, get_user_by_id
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this script from the project root directory")
    sys.exit(1)

def test_set_admin_role():
    # Check if user ID is provided as a command-line argument
    if len(sys.argv) < 2:
        user_id = input("Enter the user ID to set as admin: ")
    else:
        user_id = sys.argv[1]
    
    if not user_id:
        print("❌ No user ID provided")
        return
    
    print(f"Testing set_user_as_admin function with user ID: {user_id}")
    
    # Try to get the user first to verify they exist
    user = get_user_by_id(user_id)
    if not user:
        print(f"❌ User with ID '{user_id}' not found")
        return
    
    print(f"✓ Found user: {user.get('email', 'Unknown email')}")
    
    # Check if user is already an admin
    app_metadata = user.get('app_metadata', {})
    if app_metadata.get('is_admin'):
        print("ℹ️ User is already an admin")
    
    # Set user as admin
    print("Setting user as admin...")
    result = set_user_as_admin(user_id)
    
    if result:
        print("✅ Successfully set user as admin!")
        
        # Verify the change by getting the user again
        updated_user = get_user_by_id(user_id)
        if updated_user:
            updated_app_metadata = updated_user.get('app_metadata', {})
            if updated_app_metadata.get('is_admin'):
                print("✓ Verified user is now an admin")
            else:
                print("⚠️ User's app_metadata doesn't show is_admin=true")
                print(f"Current app_metadata: {updated_app_metadata}")
    else:
        print("❌ Failed to set user as admin")
        print("⚠️ This may be due to using a placeholder SUPABASE_SERVICE_ROLE_KEY")
        print("Please update your .env file with a valid service role key from the Supabase dashboard")

if __name__ == "__main__":
    test_set_admin_role() 