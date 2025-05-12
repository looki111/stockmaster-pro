#!/usr/bin/env python
"""
Test Token Verification for StockMaster Pro

This script tests the patched token verification system with development mode enabled.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("token_test")

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)

def load_env_variables():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Loaded environment variables from .env file")
        
        # Check if DEV_MODE is enabled
        dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
        print(f"Development mode: {'Enabled' if dev_mode else 'Disabled'}")
        
        if not dev_mode:
            print("\n⚠️ Warning: DEV_MODE is not enabled in your .env file.")
            print("Token verification may fail in strict mode.")
            print("Run backend/auth/fix_authentication.py to enable development mode.")
        
        return True
    except ImportError:
        logger.error("python-dotenv is not installed. Run: pip install python-dotenv")
        return False

def import_verification_module():
    """Try to import the token verification function"""
    print_header("Importing Verification Module")
    
    try:
        # Add the parent directory to the path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import from patched module first
        try:
            from backend.auth.patched_token_verify import verify_supabase_token
            logger.info("Successfully imported patched token verification")
            return verify_supabase_token
        except ImportError:
            # Try the original module as fallback
            try:
                from backend.auth.supabase_auth import verify_supabase_token
                logger.info("Imported original token verification (patched module not found)")
                return verify_supabase_token
            except ImportError:
                logger.error("Could not import any token verification module")
                return None
    except Exception as e:
        logger.error(f"Error during import: {e}")
        return None

def test_token_verification(verify_function):
    """Test token verification with the provided function"""
    print_header("Token Verification Test")
    
    if not verify_function:
        logger.error("No verification function available for testing")
        return False
    
    # Get token from command line or prompt
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("\nEnter a Supabase JWT token to test:")
        token = input().strip()
    
    if not token:
        logger.error("No token provided")
        return False
    
    try:
        print("\nVerifying token...")
        is_valid, payload = verify_function(token)
        
        if is_valid:
            print("\n✅ Token is VALID!")
            print("\nToken payload:")
            for key, value in payload.items():
                if key == 'app_metadata' or key == 'user_metadata':
                    print(f"  {key}: {json.dumps(value, indent=2)}")
                else:
                    print(f"  {key}: {value}")
            
            if 'sub' in payload:
                print(f"\nUser ID: {payload['sub']}")
            if 'email' in payload:
                print(f"Email: {payload['email']}")
            if 'exp' in payload:
                exp_time = payload['exp']
                exp_datetime = datetime.fromtimestamp(exp_time)
                print(f"Expires: {exp_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
        else:
            print("\n❌ Token verification FAILED")
            print("\nPossible solutions:")
            print("1. Make sure DEV_MODE=true is set in your .env file")
            print("2. Run backend/auth/fix_authentication.py to enable development mode")
            print("3. Check if the token is valid and not expired")
            print("4. Verify your Supabase configuration in .env file")
            return False
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        return False

def main():
    """Main function"""
    print_header("StockMaster Pro - Token Verification Test")
    
    # Load environment variables
    load_env_variables()
    
    # Import verification module
    verify_function = import_verification_module()
    
    # Test token verification
    test_token_verification(verify_function)

if __name__ == "__main__":
    main() 