"""
Test setting a user as admin with the fixed function.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from backend.auth.supabase_client import set_user_as_admin, get_user_by_email

def main():
    """
    Main function to test setting a user as admin.
    """
    if len(sys.argv) < 2:
        print("Usage: python test_admin_role_fix.py <email>")
        return
    
    email = sys.argv[1]
    
    # Get user by email
    user = get_user_by_email(email)
    if not user:
        logger.error(f"User with email {email} not found")
        return
    
    logger.info(f"Found user: {user.id} ({user.email})")
    
    # Set user as admin
    logger.info(f"Setting user {user.email} as admin...")
    result = set_user_as_admin(user.id)
    
    if result:
        logger.info(f"Successfully set user {user.email} as admin")
    else:
        logger.error(f"Failed to set user {user.email} as admin")

if __name__ == "__main__":
    main() 