#!/usr/bin/env python
"""
Authentication Setup Verification for StockMaster Pro

This script checks if the authentication system is properly set up.
"""

import os
import sys
import importlib.util
import json
from datetime import datetime
from dotenv import load_dotenv

def check_files():
    """Check if all required files exist"""
    required_files = [
        "backend/auth/supabase_auth.py",
        "backend/auth/patched_token_verify.py",
        ".env",
        "app.py",
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("✅ All required files exist")
    return True

def check_env_variables():
    """Check if all required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        "DEV_MODE",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SECRET_KEY",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("✅ Required environment variables are set:")
    print(f"  - DEV_MODE: {os.environ.get('DEV_MODE')}")
    print(f"  - SUPABASE_URL: {os.environ.get('SUPABASE_URL')[:15]}...")
    return True

def check_importable_modules():
    """Check if required modules can be imported"""
    required_modules = [
        "flask",
        "dotenv",
        "jose",
        "requests",
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("❌ Missing required Python modules:")
        for module in missing_modules:
            print(f"  - {module}")
        return False
    
    print("✅ All required Python modules can be imported")
    return True

def check_jwt_fix():
    """Check if the JWT fix has been applied"""
    try:
        # Try to import the supabase_auth module
        sys.path.append('backend')
        from auth import supabase_auth
        
        # Check if DEV_MODE exists in the module
        if hasattr(supabase_auth, 'DEV_MODE'):
            print("✅ JWT fix has been applied (DEV_MODE exists)")
            return True
        
        # Check if patched verification functions exist
        if hasattr(supabase_auth, 'verify_token_alternative'):
            print("✅ JWT fix has been applied (verify_token_alternative exists)")
            return True
        
        print("❌ JWT fix may not be fully applied")
        return False
    except Exception as e:
        print(f"❌ Error checking JWT fix: {e}")
        return False

def main():
    """Run all checks"""
    print("\n" + "=" * 70)
    print("StockMaster Pro Authentication Setup Check".center(70))
    print("=" * 70 + "\n")
    
    all_passed = True
    all_passed &= check_files()
    all_passed &= check_env_variables()
    all_passed &= check_importable_modules()
    all_passed &= check_jwt_fix()
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All checks passed! Your authentication system should be working.".center(70))
        print("=" * 70)
        print("\nYou can now run the application with:")
        print("python run_app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.".center(70))
        print("=" * 70)
        print("\nAfter fixing the issues, run:")
        print("1. python fix_jwt_errors.py    # To fix JWT errors")
        print("2. python setup_env.py         # To set up environment variables")
        print("3. python run_app.py           # To run the application")
    
    return all_passed

if __name__ == "__main__":
    main() 