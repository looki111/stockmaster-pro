"""
Supabase Client Module for StockMaster Pro

This module provides a client for interacting with Supabase with robust error handling.
"""

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
    """
    Validate the Supabase configuration
    
    Returns:
        bool: Whether the configuration is valid
    """
    # Track validation issues
    validation_issues = []
    
    # Check URL
    if not SUPABASE_URL:
        logger.error("SUPABASE_URL is not set in environment variables")
        validation_issues.append("Missing SUPABASE_URL")
        
    # Check keys
    if not SUPABASE_KEY:
        logger.error("SUPABASE_KEY is not set in environment variables")
        validation_issues.append("Missing SUPABASE_KEY")
    
    # Check for newlines or spaces in the key
    if SUPABASE_KEY and ('\n' in SUPABASE_KEY or ' ' in SUPABASE_KEY or '\r' in SUPABASE_KEY or '\t' in SUPABASE_KEY):
        logger.error("SUPABASE_KEY contains invalid characters (newlines, spaces, etc.)")
        validation_issues.append("SUPABASE_KEY format invalid")
    
    # Check URL format
    if SUPABASE_URL:
        if not SUPABASE_URL.startswith("https://"):
            logger.error(f"SUPABASE_URL must start with https://: {SUPABASE_URL}")
            validation_issues.append("SUPABASE_URL must use HTTPS")
        
        if not (".supabase.co" in SUPABASE_URL):
            logger.warning(f"SUPABASE_URL format looks unusual: {SUPABASE_URL}")
            # Not adding to validation issues as this could be a custom domain
    
    # Check service role key if needed for admin operations
    if not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("SUPABASE_SERVICE_ROLE_KEY is not set. Admin operations will not work.")
    elif '\n' in SUPABASE_SERVICE_ROLE_KEY or ' ' in SUPABASE_SERVICE_ROLE_KEY:
        logger.error("SUPABASE_SERVICE_ROLE_KEY contains invalid characters (newlines, spaces, etc.)")
        validation_issues.append("SUPABASE_SERVICE_ROLE_KEY format invalid")
    
    # Log validation summary
    if validation_issues:
        logger.error(f"Supabase configuration validation failed with {len(validation_issues)} issues: {', '.join(validation_issues)}")
        return False
    
    logger.info("Supabase configuration validated successfully")
    return True

def get_supabase_client(force_refresh=False) -> Client:
    """
    Get the regular Supabase client instance (using anon key).
    Initializes the client if it doesn't exist or if force_refresh is True.
    
    Args:
        force_refresh (bool): Whether to force a refresh of the client
        
    Returns:
        Client: The Supabase client
        
    Raises:
        ValueError: If the Supabase URL or Key is not set
        Exception: If there is an error initializing the client
    """
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
    """
    Get the admin Supabase client instance (using service role key).
    Initializes the client if it doesn't exist or if force_refresh is True.
    
    Args:
        force_refresh (bool): Whether to force a refresh of the client
        
    Returns:
        Client: The Supabase admin client
        
    Raises:
        ValueError: If the Supabase URL or Service Role Key is not set
        Exception: If there is an error initializing the client
    """
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
        if '\n' in SUPABASE_SERVICE_ROLE_KEY or ' ' in SUPABASE_SERVICE_ROLE_KEY:
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
    """
    Test the Supabase connection
    
    Returns:
        bool: Whether the connection was successful
    """
    try:
        client = get_supabase_client()
        # Instead of querying a specific table, just check auth status
        response = client.auth.get_user()
        # Even if the user is not authenticated, we've successfully connected
        logger.info("Supabase connection test successful")
        return True
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False

# Add a new function to refresh tokens
async def refresh_token() -> Dict[str, Any]:
    """
    Refresh the current user's token if it's expired
    
    Returns:
        Dict[str, Any]: The refresh result containing:
            - success (bool): Whether the refresh was successful
            - token (str, optional): The new token if successful
            - error (str, optional): Error message if unsuccessful
    """
    try:
        # Get or initialize Supabase client
        client = get_supabase_client()
        
        # Try to refresh the session
        response = await client.auth.refresh_session()
        
        if response.error:
            logger.error(f"Error refreshing token: {response.error}")
            return {'success': False, 'error': response.error.message}
        
        if not response.data:
            logger.error("No data returned when refreshing token")
            return {'success': False, 'error': 'No data returned when refreshing token'}
            
        # Return the new token
        new_token = response.data.session.access_token
        logger.info("Successfully refreshed token")
        
        return {'success': True, 'token': new_token}
    except Exception as e:
        logger.error(f"Exception during token refresh: {e}")
        return {'success': False, 'error': str(e)}

# Synchronous version for compatibility
def refresh_token_sync() -> Dict[str, Any]:
    """
    Synchronous version of refresh_token
    
    Returns:
        Dict[str, Any]: The refresh result
    """
    try:
        # Get or initialize Supabase client
        client = get_supabase_client()
        
        # Try to refresh the session
        response = client.auth.refresh_session()
        
        if response.error:
            logger.error(f"Error refreshing token: {response.error}")
            return {'success': False, 'error': response.error.message}
        
        if not response.data:
            logger.error("No data returned when refreshing token")
            return {'success': False, 'error': 'No data returned when refreshing token'}
            
        # Return the new token
        new_token = response.data.session.access_token
        logger.info("Successfully refreshed token")
        
        return {'success': True, 'token': new_token}
    except Exception as e:
        logger.error(f"Exception during token refresh: {e}")
        return {'success': False, 'error': str(e)}

# Rest of your client functions would go here...
