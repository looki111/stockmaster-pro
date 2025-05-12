"""
Supabase Client Module for StockMaster Pro

This module provides a client for interacting with Supabase.
"""

import os
import logging
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

# Initialize Supabase clients
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Get the regular Supabase client instance (using anon key).
    Initializes the client if it doesn't exist.
    
    Returns:
        Client: The Supabase client
    """
    global supabase
    
    if not supabase:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            logger.error(f"Error initializing Supabase client: {e}")
            raise
    
    return supabase

def get_supabase_admin_client() -> Client:
    """
    Get the admin Supabase client instance (using service role key).
    Initializes the client if it doesn't exist.
    
    Returns:
        Client: The Supabase admin client
    """
    global supabase_admin
    
    if not supabase_admin:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
        
        try:
            supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        except Exception as e:
            logger.error(f"Error initializing Supabase admin client: {e}")
            raise
    
    return supabase_admin

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by ID from Supabase.
    
    Args:
        user_id (str): The user ID
        
    Returns:
        Optional[Dict[str, Any]]: The user data if found, None otherwise
    """
    try:
        client = get_supabase_admin_client()  # Use admin client for auth admin operations
        response = client.auth.admin.get_user_by_id(user_id)
        return response.user
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by email from Supabase.
    
    Args:
        email (str): The user email
        
    Returns:
        Optional[Dict[str, Any]]: The user data if found, None otherwise
    """
    try:
        client = get_supabase_admin_client()  # Use admin client for auth admin operations
        response = client.auth.admin.list_users()
        for user in response.users:
            if user.email == email:
                return user
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

def update_user_metadata(user_id: str, metadata: Dict[str, Any]) -> bool:
    """
    Update a user's metadata in Supabase.
    
    Args:
        user_id (str): The user ID
        metadata (Dict[str, Any]): The metadata to update
        
    Returns:
        bool: Whether the update was successful
    """
    try:
        client = get_supabase_admin_client()  # Use admin client for auth admin operations
        client.auth.admin.update_user_by_id(
            user_id,
            data={"user_metadata": metadata}
        )
        return True
    except Exception as e:
        logger.error(f"Error updating user metadata: {e}")
        return False

def update_user_app_metadata(user_id: str, metadata: Dict[str, Any]) -> bool:
    """
    Update a user's app metadata in Supabase.
    
    Args:
        user_id (str): The user ID
        metadata (Dict[str, Any]): The app metadata to update
        
    Returns:
        bool: Whether the update was successful
    """
    try:
        client = get_supabase_admin_client()  # Use admin client for auth admin operations
        client.auth.admin.update_user_by_id(
            user_id,
            data={"app_metadata": metadata}
        )
        return True
    except Exception as e:
        logger.error(f"Error updating user app metadata: {e}")
        return False

def set_user_as_admin(user_id: str) -> bool:
    """
    Set a user as an admin in Supabase.
    
    Args:
        user_id (str): The user ID
        
    Returns:
        bool: Whether the update was successful
    """
    try:
        client = get_supabase_admin_client()  # Use admin client for auth admin operations
        response = client.auth.admin.update_user_by_id(
            user_id,
            data={"app_metadata": {"is_admin": True}}
        )
        return response.user is not None
    except Exception as e:
        logger.error(f"Error setting user as admin: {e}")
        return False

def create_user(email: str, password: str, metadata: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Create a new user in Supabase.
    
    Args:
        email (str): The user email
        password (str): The user password
        metadata (Dict[str, Any], optional): The user metadata
        
    Returns:
        Optional[Dict[str, Any]]: The created user data if successful, None otherwise
    """
    try:
        client = get_supabase_admin_client()  # Use admin client for auth admin operations
        response = client.auth.admin.create_user({
            'email': email,
            'password': password,
            'email_confirm': True,
            'user_metadata': metadata or {}
        })
        return response.user
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None
