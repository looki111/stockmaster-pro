"""
Test Supabase Initialization

This script tests if the Supabase credentials are correctly loaded and accessible.
"""

import os
from dotenv import load_dotenv
from flask import Flask

def test_supabase_init():
    """
    Test Supabase initialization by loading environment variables and setting up a Flask app.
    """
    print("Testing Supabase initialization...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if Supabase URL and key exist in environment
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    supabase_service_role_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in environment variables.")
    else:
        print(f"✅ SUPABASE_URL found: {supabase_url}")
    
    if not supabase_key:
        print("❌ SUPABASE_KEY not found in environment variables.")
    else:
        print(f"✅ SUPABASE_KEY found: {supabase_key[:10]}...{supabase_key[-10:]}")
    
    if not supabase_service_role_key:
        print("❌ SUPABASE_SERVICE_ROLE_KEY not found in environment variables.")
    else:
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY found: {supabase_service_role_key[:10]}...{supabase_service_role_key[-10:]}")
    
    # Create a test Flask app
    app = Flask(__name__)
    
    # Configure app from environment
    app.config['SUPABASE_URL'] = supabase_url or ''
    app.config['SUPABASE_KEY'] = supabase_key or ''
    app.config['SUPABASE_SERVICE_ROLE_KEY'] = supabase_service_role_key or ''
    
    # Check that the configuration is set in the app
    if not app.config.get('SUPABASE_URL'):
        print("❌ SUPABASE_URL not set in Flask app config.")
    else:
        print(f"✅ SUPABASE_URL correctly set in Flask app config.")
    
    if not app.config.get('SUPABASE_KEY'):
        print("❌ SUPABASE_KEY not set in Flask app config.")
    else:
        print(f"✅ SUPABASE_KEY correctly set in Flask app config.")
    
    if not app.config.get('SUPABASE_SERVICE_ROLE_KEY'):
        print("❌ SUPABASE_SERVICE_ROLE_KEY not set in Flask app config.")
    else:
        print(f"✅ SUPABASE_SERVICE_ROLE_KEY correctly set in Flask app config.")
    
    print("\nNOTE: Make sure your Supabase credentials are real and correct!")
    print("The script only checks if the environment variables are loaded, not if they are valid.")

if __name__ == "__main__":
    test_supabase_init() 