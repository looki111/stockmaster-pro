#!/usr/bin/env python
"""
Test Authentication Fix for StockMaster Pro

This script tests if the authentication fix has been successfully applied.
"""

import os
import sys
import logging
import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("auth_test")

def main():
    """Test the authentication system"""
    print("\n" + "=" * 70)
    print("StockMaster Pro Authentication Test".center(70))
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Check DEV_MODE
    dev_mode = os.environ.get('DEV_MODE', 'false').lower() == 'true'
    print(f"🔍 DEV_MODE is {'enabled' if dev_mode else 'disabled'}")
    
    # Add backend to path
    sys.path.append('backend')
    
    # Try to import the patched modules
    try:
        from auth import supabase_auth
        print("✅ Successfully imported supabase_auth module")
        
        # Check if necessary functions exist
        if hasattr(supabase_auth, 'verify_token_alternative'):
            print("✅ verify_token_alternative function exists")
        else:
            print("❌ verify_token_alternative function is missing")
        
        if hasattr(supabase_auth, 'verify_supabase_token'):
            print("✅ verify_supabase_token function exists")
        else:
            print("❌ verify_supabase_token function is missing")
        
        # Check if DEV_MODE is properly set in the module
        if hasattr(supabase_auth, 'DEV_MODE'):
            print(f"✅ DEV_MODE in module is set to: {supabase_auth.DEV_MODE}")
        else:
            print("❌ DEV_MODE variable is missing in the module")
    
    except ImportError as e:
        print(f"❌ Error importing supabase_auth module: {e}")
        return False
    
    # Check if Flask server is running
    try:
        response = requests.get('http://127.0.0.1:5000/')
        if response.status_code == 200:
            print("✅ Flask server is running and responding")
        else:
            print(f"⚠️ Flask server returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server. Is it running?")
    
    # Create a test token
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJleHAiOjk5OTk5OTk5OTl9.signature"
    
    # Test the token verification
    try:
        result = supabase_auth.verify_supabase_token(test_token)
        print(f"✅ Token verification function called successfully: {result}")
    except Exception as e:
        print(f"❌ Error during token verification: {e}")
    
    print("\nTest complete!")
    return True

if __name__ == "__main__":
    main() 