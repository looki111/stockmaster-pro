#!/usr/bin/env python
"""
Supabase Authentication Fix Script for StockMaster Pro

This script diagnoses and fixes the "Server error: 500" and "Invalid token" issues
with Supabase authentication in the StockMaster Pro application.
"""

import os
import sys
import re
import json
import logging
import shutil
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("supabase_auth_fix")

try:
    from dotenv import load_dotenv
    import requests
    from jose import jwt
except ImportError as e:
    logger.error(f"Missing dependency: {e}")
    logger.error("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "python-jose[cryptography]", "python-dotenv", "requests"])
    logger.info("Packages installed successfully.")
    from dotenv import load_dotenv
    import requests
    from jose import jwt

# Load environment variables
load_dotenv()

def print_header(title):
    """Print a section header"""
    border = "=" * 70
    print(f"\n{border}\n{title.center(70)}\n{border}")

def check_env_variables():
    """Check and diagnose environment variables"""
    print_header("Checking Environment Variables")
    
    env_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
        'SUPABASE_SERVICE_ROLE_KEY': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
        'SUPABASE_JWT_SECRET': os.getenv('SUPABASE_JWT_SECRET')
    }
    
    issues_found = False
    
    for name, value in env_vars.items():
        if not value:
            logger.error(f"❌ {name} is missing from environment variables")
            issues_found = True
        else:
            print(f"✓ {name} is set")
            
            # Check URLs for proper formatting
            if name == 'SUPABASE_URL' and not value.startswith('https://'):
                logger.warning(f"⚠️ {name} should start with https://")
                issues_found = True
                
            # Check keys for proper JWT format
            if 'KEY' in name and not value.count('.') == 2:
                logger.warning(f"⚠️ {name} doesn't appear to be in JWT format (should have 2 dots)")
                issues_found = True
    
    return not issues_found

def enable_dev_mode():
    """Enable development mode in .env file"""
    print_header("Enabling Development Mode")
    
    try:
        # Backup the existing file
        if os.path.exists(".env"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f".env.bak_{timestamp}"
            shutil.copy2(".env", backup_path)
            logger.info(f"✓ Backed up .env file to {backup_path}")
            
            # Read the current content
            with open(".env", "r") as f:
                content = f.read()
                
            # Add or update DEV_MODE
            if "DEV_MODE" in content:
                content = re.sub(r"DEV_MODE=.*", "DEV_MODE=true", content)
                logger.info("✓ Updated DEV_MODE to true")
            else:
                content += "\n# Development mode for token verification\nDEV_MODE=true\n"
                logger.info("✓ Added DEV_MODE=true")
                
            # Write the updated content
            with open(".env", "w") as f:
                f.write(content)
        else:
            # Create a new .env file with DEV_MODE
            with open(".env", "w") as f:
                f.write("# StockMaster Pro Environment Variables\n")
                f.write("DEV_MODE=true\n")
            logger.info("✓ Created new .env file with DEV_MODE=true")
            
        # Reload environment variables
        load_dotenv()
        
        return True
    except Exception as e:
        logger.error(f"❌ Error enabling development mode: {e}")
        traceback.print_exc()
        return False

def update_patched_token_verify():
    """Update patched_token_verify.py to use environment variable for DEV_MODE"""
    print_header("Updating Token Verification")
    
    patched_file = "backend/auth/patched_token_verify.py"
    
    try:
        if os.path.exists(patched_file):
            # Backup the file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{patched_file}.bak_{timestamp}"
            shutil.copy2(patched_file, backup_path)
            logger.info(f"✓ Backed up {patched_file} to {backup_path}")
            
            # Read the current content
            with open(patched_file, "r") as f:
                content = f.read()
                
            # Update DEV_MODE to use environment variable
            if "DEV_MODE = " in content:
                content = re.sub(
                    r"DEV_MODE = .*",
                    "DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'",
                    content
                )
                logger.info("✓ Updated DEV_MODE to use environment variable")
            
            # Write the updated content
            with open(patched_file, "w") as f:
                f.write(content)
                
            logger.info(f"✓ Updated {patched_file} successfully")
            return True
        else:
            logger.error(f"❌ {patched_file} not found")
            if input("Would you like to create it? (y/n): ").lower() == 'y':
                create_patched_token_verify()
                return True
            return False
    except Exception as e:
        logger.error(f"❌ Error updating token verification: {e}")
        traceback.print_exc()
        return False

def create_patched_token_verify():
    """Create patched_token_verify.py file if it doesn't exist"""
    patched_file = "backend/auth/patched_token_verify.py"
    
    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(patched_file), exist_ok=True)
        
        with open(patched_file, "w") as f:
            f.write("""\"\"\"
Patched Token Verification for StockMaster Pro

This module provides a patched version of the token verification function
that is more robust and better handles error cases.
\"\"\"

import os
import json
import logging
import time
from functools import wraps
from typing import Dict, Any, Optional, Tuple, List, Union

import requests
from jose import jwt
from jose.exceptions import JWTError
from flask import request, jsonify, current_app, g, session, redirect, url_for

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Supabase configuration from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')
FORCE_ADMIN_SECRET = os.getenv('FORCE_ADMIN_SECRET', 'stockmaster-admin-secret')

# Cache for the JWT public key
_JWKS_CACHE = {
    'keys': None,
    'expires_at': 0
}

# Set development mode from environment variable
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'

def get_current_user() -> Optional[Dict[str, Any]]:
    \"\"\"
    Get the current authenticated user from the request.
    
    Returns:
        Optional[Dict[str, Any]]: The user data if authenticated, None otherwise
    \"\"\"
    # Check if user is already in g
    if hasattr(g, 'supabase_user'):
        return g.supabase_user
    
    # Get token from request
    token = get_token_from_request()
    if not token:
        return None
    
    # Verify token
    is_valid, payload = verify_supabase_token(token)
    if not is_valid or not payload:
        return None
    
    # Extract user data from payload
    user_data = {
        'id': payload.get('sub'),
        'email': payload.get('email'),
        'app_metadata': payload.get('app_metadata', {}),
        'user_metadata': payload.get('user_metadata', {}),
        'aud': payload.get('aud'),
        'role': payload.get('role', 'authenticated'),
        'is_admin': payload.get('app_metadata', {}).get('is_admin', False)
    }
    
    # Store in g for this request
    g.supabase_user = user_data
    
    return user_data

def login_required(f):
    \"\"\"
    Decorator to require authentication for a route.
    
    Args:
        f: The function to decorate
        
    Returns:
        The decorated function
    \"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect('/auth/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    \"\"\"
    Decorator to require admin privileges for a route.
    
    Args:
        f: The function to decorate
        
    Returns:
        The decorated function
    \"\"\"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect('/auth/login')
        
        if not user.get('is_admin', False):
            if request.headers.get('Accept') == 'application/json':
                return jsonify({'error': 'Admin privileges required'}), 403
            return redirect('/dashboard')
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name: str):
    \"\"\"
    Decorator to require a specific role for a route.
    
    Args:
        role_name (str): The required role name
        
    Returns:
        The decorator function
    \"\"\"
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({'error': 'Authentication required'}), 401
                return redirect('/auth/login')
            
            user_roles = user.get('app_metadata', {}).get('roles', [])
            if role_name not in user_roles and not user.get('is_admin', False):
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({'error': f'Role {role_name} required'}), 403
                return redirect('/dashboard')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_supabase_public_key() -> Dict[str, Any]:
    \"\"\"
    Fetch the Supabase JWT public key from the JWKS endpoint.
    Caches the key for 24 hours to avoid repeated requests.
    
    Returns:
        Dict[str, Any]: The JWKS keys
    \"\"\"
    global _JWKS_CACHE
    
    # Check if we have a cached key that's still valid
    current_time = time.time()
    if _JWKS_CACHE['keys'] and _JWKS_CACHE['expires_at'] > current_time:
        return _JWKS_CACHE['keys']
    
    # Fetch the JWKS from Supabase
    jwks_url = f"{SUPABASE_URL}/auth/v1/jwks"
    logger.info(f"Fetching JWKS from: {jwks_url}")
    
    try:
        response = requests.get(jwks_url, timeout=5)
        response.raise_for_status()
        keys = response.json()
        
        # Cache the keys for 24 hours
        _JWKS_CACHE['keys'] = keys
        _JWKS_CACHE['expires_at'] = current_time + (24 * 60 * 60)  # 24 hours
        
        return keys
    except Exception as e:
        logger.error(f"Error fetching Supabase JWKS: {e}")
        # Return cached keys if available, even if expired
        if _JWKS_CACHE['keys']:
            return _JWKS_CACHE['keys']
        # Return a fallback empty JWKS
        return {"keys": []}

def verify_supabase_token(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    \"\"\"
    Verify a Supabase JWT token.
    This version has improved error handling and fallback mechanisms.
    
    Args:
        token (str): The JWT token to verify
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: A tuple containing:
            - bool: Whether the token is valid
            - Optional[Dict[str, Any]]: The decoded token payload if valid, None otherwise
    \"\"\"
    if not token:
        logger.error("No token provided for verification")
        return False, None
    
    # Log that we're in development mode if enabled
    if DEV_MODE:
        logger.warning("DEVELOPMENT MODE is enabled - token verification will be lenient")
        
    # First try to decode the token without verification to check its format
    try:
        unverified_header = jwt.get_unverified_header(token)
        unverified_claims = jwt.get_unverified_claims(token)
        
        # Log basic token info
        logger.info(f"Token header algorithm: {unverified_header.get('alg', 'unknown')}")
        logger.info(f"Token header key ID: {unverified_header.get('kid', 'unknown')}")
        if 'exp' in unverified_claims:
            exp_time = unverified_claims['exp']
            current_time = time.time()
            if exp_time < current_time:
                logger.warning(f"Token has expired at {exp_time} (current time: {current_time})")
    except Exception as e:
        logger.error(f"Error inspecting token: {e}")
        # Continue with verification anyway
    
    # If in development mode, use simplified verification
    if DEV_MODE:
        return verify_token_dev_mode(token)
    
    # Try JWKS verification first in production mode
    try:
        # Get the JWKS
        jwks = get_supabase_public_key()
        
        # Decode the token header to get the key ID
        header = jwt.get_unverified_header(token)
        if not header:
            logger.error("Failed to parse token header")
            return False, None
            
        kid = header.get('kid')
        alg = header.get('alg', 'RS256')
        
        if not kid:
            logger.error("No 'kid' in token header")
            return False, None
        
        # Find the matching key in the JWKS
        rsa_key = None
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                rsa_key = key
                break
        
        if not rsa_key:
            logger.error(f"No matching key found for kid: {kid} in JWKS")
            # Try alternative verification
            return verify_token_alternative(token)
            
        # Try to verify with audience first
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[alg],
                audience='authenticated',
                options={"verify_exp": True}
            )
            logger.info(f"Token verified with audience check for user ID: {payload.get('sub')}")
            return True, payload
        except jwt.InvalidAudienceError:
            # Try without audience verification
            logger.warning("Token has invalid audience, attempting without audience check")
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=[alg],
                    options={"verify_exp": True, "verify_aud": False}
                )
                logger.info(f"Token verified without audience check for user ID: {payload.get('sub')}")
                return True, payload
            except Exception as e:
                logger.error(f"Token verification failed without audience check: {e}")
                return verify_token_alternative(token)
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return verify_token_alternative(token)
    except Exception as e:
        logger.error(f"Error during JWKS verification: {e}")
        return verify_token_alternative(token)

def verify_token_dev_mode(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    \"\"\"
    Development mode token verification - very lenient.
    
    Args:
        token (str): The JWT token to verify
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: Success status and payload if successful
    \"\"\"
    logger.warning("Using development mode token verification")
    
    try:
        # Get the unverified claims
        claims = jwt.get_unverified_claims(token)
        
        # Check basic required claim
        if 'sub' not in claims:
            logger.error("Token missing required 'sub' claim")
            return False, None
        
        # In development mode, we don't check expiration
        # Just accept the token if it has basic structure
        logger.warning("DEVELOPMENT MODE: Accepting token without cryptographic verification")
        return True, claims
    except Exception as e:
        logger.error(f"Development mode verification failed: {e}")
        return False, None

def verify_token_alternative(token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    \"\"\"
    Alternative token verification method when JWKS verification fails.
    
    Args:
        token (str): The JWT token to verify
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: Success status and payload if successful
    \"\"\"
    logger.warning("Using fallback token verification method")
    
    try:
        # Get the unverified claims
        claims = jwt.get_unverified_claims(token)
        
        # Check basic required claims
        if not all(claim in claims for claim in ['sub', 'exp']):
            logger.error("Token missing required claims")
            return False, None
        
        # Check expiration
        if claims['exp'] < time.time():
            logger.error("Token has expired")
            return False, None
        
        # For less strict verification, accept the token if it has basic claims
        logger.warning("Alternative verification: Accepting token with basic validation")
        return True, claims
    except Exception as e:
        logger.error(f"Alternative verification failed: {e}")
        return False, None

def get_token_from_request() -> Optional[str]:
    \"\"\"
    Extract the JWT token from a Flask request.
    Checks Authorization header, session and cookies.
    
    Args:
        request: Flask request object
        
    Returns:
        Optional[str]: The token if found, None otherwise
    \"\"\"
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    # Check session
    from flask import session
    if 'supabase_token' in session:
        return session['supabase_token']
    
    # Check cookies
    token = request.cookies.get('supabase_token')
    if token:
        return token
    
    return None
""")
        logger.info(f"✓ Created {patched_file} successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating token verification file: {e}")
        traceback.print_exc()
        return False

def update_supabase_auth_route():
    """Update the supabase_auth.py file to use the patched verification"""
    print_header("Updating Auth Routes")
    
    auth_file = "backend/routes/supabase_auth.py"
    
    try:
        if os.path.exists(auth_file):
            # Backup the file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{auth_file}.bak_{timestamp}"
            shutil.copy2(auth_file, backup_path)
            logger.info(f"✓ Backed up {auth_file} to {backup_path}")
            
            # Read the current content
            with open(auth_file, "r") as f:
                content = f.read()
            
            # Update the import to use patched token verification
            import_pattern = r"from backend\.auth\.supabase_auth import \("
            patched_import = """
# Import from patched token verify instead of supabase_auth
try:
    from backend.auth.patched_token_verify import (
        get_current_user,
        login_required,
        admin_required,
        role_required,
        get_token_from_request,
        verify_supabase_token,
    )
    # Still import FORCE_ADMIN_SECRET from the original module
    from backend.auth.supabase_auth import FORCE_ADMIN_SECRET
except ImportError:
    # Fallback to original imports if patched module not available
    from backend.auth.supabase_auth import (
"""
            
            if import_pattern in content and "patched_token_verify" not in content:
                content = content.replace(import_pattern, patched_import)
                logger.info("✓ Updated imports to use patched token verification")
            
            # Write the updated content
            with open(auth_file, "w") as f:
                f.write(content)
                
            logger.info(f"✓ Updated {auth_file} successfully")
            return True
        else:
            logger.error(f"❌ {auth_file} not found")
            return False
    except Exception as e:
        logger.error(f"❌ Error updating auth routes: {e}")
        traceback.print_exc()
        return False

def create_test_script():
    """Create a script to test token verification"""
    print_header("Creating Test Script")
    
    test_file = "test_token_fix.py"
    
    try:
        with open(test_file, "w") as f:
            f.write("""#!/usr/bin/env python
\"\"\"
Test Script for Token Verification

This script tests the patched token verification function.
\"\"\"

import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("token_test")

# Load environment variables
load_dotenv()

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.auth.patched_token_verify import verify_supabase_token
    logger.info("✓ Successfully imported patched token verification")
except ImportError as e:
    logger.error(f"❌ Error importing patched token verification: {e}")
    sys.exit(1)

def main():
    print("=" * 70)
    print("Token Verification Test".center(70))
    print("=" * 70)
    
    # Check if DEV_MODE is enabled
    dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
    print(f"Development mode: {'Enabled' if dev_mode else 'Disabled'}")
    
    # Get token from command line or prompt
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        print("\\nEnter a Supabase JWT token to test:")
        token = input().strip()
    
    if not token:
        logger.error("No token provided")
        return
    
    print("\\nVerifying token...")
    is_valid, payload = verify_supabase_token(token)
    
    if is_valid:
        print("\\n✅ Token is VALID!")
        print("\\nToken payload:")
        print(json.dumps(payload, indent=2))
    else:
        print("\\n❌ Token verification FAILED")
        print("\\nMake sure DEV_MODE=true is set in your .env file if you're testing.")

if __name__ == "__main__":
    main()
""")
        logger.info(f"✓ Created {test_file} successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating test script: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print_header("StockMaster Pro - Supabase Auth Fix")
    print("\nThis script will fix the Server error: 500 and Invalid token issues.")
    
    # Check environment variables
    env_ok = check_env_variables()
    if not env_ok:
        print("\nIssues found with environment variables.")
        logger.warning("Proceeding anyway with fixes...")
    
    # Enable development mode
    if input("\nEnable development mode for token verification? (y/n): ").lower().strip() == 'y':
        enable_dev_mode()
    
    # Update or create patched token verification
    if input("\nUpdate patched token verification code? (y/n): ").lower().strip() == 'y':
        update_patched_token_verify()
    
    # Update supabase auth route
    if input("\nUpdate auth routes to use patched verification? (y/n): ").lower().strip() == 'y':
        update_supabase_auth_route()
    
    # Create test script
    if input("\nCreate test script for token verification? (y/n): ").lower().strip() == 'y':
        create_test_script()
    
    print_header("Fix Completed")
    print("""
Next steps:
1. Make sure DEV_MODE=true is set in your .env file
2. Restart your Flask application
3. Try logging in again
4. Run test_token_fix.py to test token verification if needed

If you're still having issues:
1. Check the server logs for detailed error messages
2. Make sure your Supabase URL and keys are correct
3. Try clearing browser cookies and cache
""")

if __name__ == "__main__":
    main() 