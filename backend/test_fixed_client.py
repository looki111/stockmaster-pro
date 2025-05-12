"""
Test the fixed Supabase client

This script tests the fixed Supabase client with better error handling.
"""

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
    """Test the fixed Supabase client"""
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
