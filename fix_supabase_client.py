"""
Fix Supabase client initialization with proper error handling

This script creates a properly structured Supabase client initialization
file with robust error handling for token verification.
"""

import os
import shutil
import traceback

def create_fixed_client_module():
    """Create a fixed Supabase client module with better error handling"""
    print("Creating fixed Supabase client module...")
    
    fixed_client_code = """\"\"\"
Supabase Client Module for StockMaster Pro

This module provides a client for interacting with Supabase with robust error handling.
\"\"\"

import os
import logging
import time
from typing import Dict, Any, Optional, Tuple, List, Union

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Check if environment variables are set
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    logger.error("Please check your .env file or environment configuration")

# Cache clients to avoid recreating them
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None
# Token refresh timestamp
_last_refresh_time = 0
# Refresh interval in seconds (10 minutes)
_REFRESH_INTERVAL = 600

def validate_supabase_config() -> bool:
    \"\"\"
    Validate the Supabase configuration
    
    Returns:
        bool: Whether the configuration is valid
    \"\"\"
    if not SUPABASE_URL:
        logger.error("SUPABASE_URL is not set in environment variables")
        return False
        
    if not SUPABASE_KEY:
        logger.error("SUPABASE_KEY is not set in environment variables")
        return False
    
    # Check for newlines or spaces in the key
    if '\\n' in SUPABASE_KEY or ' ' in SUPABASE_KEY or '\\r' in SUPABASE_KEY or '\\t' in SUPABASE_KEY:
        logger.error("SUPABASE_KEY contains invalid characters (newlines, spaces, etc.)")
        return False
    
    # Check URL format
    if not SUPABASE_URL.startswith("https://") or not ".supabase.co" in SUPABASE_URL:
        logger.warning(f"SUPABASE_URL format looks unusual: {SUPABASE_URL}")
        # Not returning False as this might be a custom URL
    
    return True

def get_supabase_client(force_refresh=False) -> Client:
    \"\"\"
    Get the regular Supabase client instance (using anon key).
    Initializes the client if it doesn't exist or if force_refresh is True.
    
    Args:
        force_refresh (bool): Whether to force a refresh of the client
        
    Returns:
        Client: The Supabase client
        
    Raises:
        ValueError: If the Supabase URL or Key is not set
        Exception: If there is an error initializing the client
    \"\"\"
    global supabase, _last_refresh_time
    
    current_time = time.time()
    should_refresh = (
        force_refresh or 
        supabase is None or 
        (current_time - _last_refresh_time) > _REFRESH_INTERVAL
    )
    
    if should_refresh:
        if not validate_supabase_config():
            raise ValueError("Invalid Supabase configuration. Check logs for details.")
        
        try:
            logger.info(f"Initializing Supabase client with URL: {SUPABASE_URL}")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            _last_refresh_time = current_time
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {e}")
            raise
    
    return supabase

def get_supabase_admin_client(force_refresh=False) -> Client:
    \"\"\"
    Get the admin Supabase client instance (using service role key).
    Initializes the client if it doesn't exist or if force_refresh is True.
    
    Args:
        force_refresh (bool): Whether to force a refresh of the client
        
    Returns:
        Client: The Supabase admin client
        
    Raises:
        ValueError: If the Supabase URL or Service Role Key is not set
        Exception: If there is an error initializing the client
    \"\"\"
    global supabase_admin, _last_refresh_time
    
    current_time = time.time()
    should_refresh = (
        force_refresh or 
        supabase_admin is None or 
        (current_time - _last_refresh_time) > _REFRESH_INTERVAL
    )
    
    if should_refresh:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        
        # Check for newlines or spaces in the key
        if '\\n' in SUPABASE_SERVICE_ROLE_KEY or ' ' in SUPABASE_SERVICE_ROLE_KEY:
            logger.error("SUPABASE_SERVICE_ROLE_KEY contains newlines or spaces")
            raise ValueError("Invalid SUPABASE_SERVICE_ROLE_KEY format")
        
        try:
            logger.info(f"Initializing Supabase admin client with URL: {SUPABASE_URL}")
            supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            _last_refresh_time = current_time
            logger.info("Supabase admin client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Supabase admin client: {e}")
            raise
    
    return supabase_admin

def test_supabase_connection() -> bool:
    \"\"\"
    Test the Supabase connection
    
    Returns:
        bool: Whether the connection was successful
    \"\"\"
    try:
        client = get_supabase_client()
        # Make a simple query to test the connection
        response = client.table('locations').select('id').limit(1).execute()
        logger.info("Supabase connection test successful")
        return True
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False

# Rest of your client functions would go here...
"""

    try:
        # Create the directory if it doesn't exist
        os.makedirs("backend/auth", exist_ok=True)
        print(f"Created directory: backend/auth")
        
        # Backup the existing file if it exists
        target_file = "backend/auth/fixed_supabase_client.py"
        if os.path.exists(target_file):
            shutil.copy2(target_file, f"{target_file}.bak")
            print(f"✅ Backed up existing {target_file} to {target_file}.bak")
        
        # Write the fixed client code
        with open(target_file, "w") as f:
            f.write(fixed_client_code)
        
        print(f"✅ Created {target_file} with improved error handling")
        print("   This file includes better validation and error handling for Supabase connections")
        return True
    except Exception as e:
        print(f"❌ Error creating fixed client module: {e}")
        traceback.print_exc()
        return False

def create_test_script():
    """Create a script to test the fixed Supabase client"""
    print("Creating test script...")
    
    test_script_code = """\"\"\"
Test the fixed Supabase client

This script tests the fixed Supabase client with better error handling.
\"\"\"

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import the fixed client
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from auth.fixed_supabase_client import (
        get_supabase_client,
        validate_supabase_config,
        test_supabase_connection
    )
    logger.info("Successfully imported fixed Supabase client")
except ImportError as e:
    logger.error(f"Error importing fixed Supabase client: {e}")
    sys.exit(1)

def test_fixed_client():
    \"\"\"Test the fixed Supabase client\"\"\"
    logger.info("Testing fixed Supabase client...")
    
    # Validate configuration
    logger.info("Validating Supabase configuration...")
    is_valid = validate_supabase_config()
    if is_valid:
        logger.info("[PASS] Supabase configuration is valid")
    else:
        logger.error("[FAIL] Supabase configuration is invalid")
        return False
    
    # Test connection
    logger.info("Testing Supabase connection...")
    try:
        client = get_supabase_client()
        logger.info("[PASS] Successfully initialized Supabase client")
        
        # Test connection with a simple query
        if test_supabase_connection():
            logger.info("[PASS] Supabase connection test successful")
            return True
        else:
            logger.error("[FAIL] Supabase connection test failed")
            return False
    except Exception as e:
        logger.error(f"[FAIL] Error testing Supabase client: {e}")
        return False

if __name__ == "__main__":
    if test_fixed_client():
        logger.info("[SUCCESS] All tests passed!")
    else:
        logger.error("[ERROR] Tests failed. Please check your Supabase configuration.")
        logger.info("1. Ensure your .env file has the correct format")
        logger.info("2. Check that SUPABASE_URL and SUPABASE_KEY are correct")
        logger.info("3. Verify your Supabase project is active")
"""

    try:
        # Create the directory if it doesn't exist
        os.makedirs("backend", exist_ok=True)
        print(f"Created directory: backend")
        
        # Write the test script
        target_file = "backend/test_fixed_client.py"
        with open(target_file, "w") as f:
            f.write(test_script_code)
        
        print(f"✅ Created {target_file} to test the fixed Supabase client")
        return True
    except Exception as e:
        print(f"❌ Error creating test script: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function to create fixed Supabase client files"""
    print("Creating Fixed Supabase Client Files")
    print("=" * 50)
    
    # Create the fixed client module
    success1 = create_fixed_client_module()
    
    # Create the test script
    success2 = create_test_script()
    
    if success1 and success2:
        print("\nSuccessfully created all files!")
        print("\nNext steps:")
        print("1. Ensure your .env file has the correct Supabase credentials")
        print("2. Run the test script: python backend/test_fixed_client.py")
        print("3. If the tests pass, update your application to use the fixed client")
        print("   by importing from auth.fixed_supabase_client instead of auth.supabase_client")
    else:
        print("\nSome errors occurred during file creation. Please check the logs above.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc() 