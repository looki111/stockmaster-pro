#!/usr/bin/env python
"""
Token Debugging Script for StockMaster Pro

This script helps diagnose token verification issues with various logging
and visualization features.
"""

import os
import sys
import json
import base64
import logging
from typing import Dict, Any, Optional, Tuple

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("token_debugger")
logger.setLevel(logging.DEBUG)

# Add console handler with more visible formatting for errors
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('\n%(levelname)s: %(message)s\n')
ch.setFormatter(formatter)
logger.addHandler(ch)

try:
    from jose import jwt
    from jose.exceptions import JWTError, JWKError
    from dotenv import load_dotenv
    import requests
except ImportError as e:
    logger.error(f"Missing dependency: {e}")
    logger.error("Please run: pip install python-jose[cryptography] python-dotenv requests")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Get Supabase configuration from environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

def print_header(title: str) -> None:
    """Print a formatted header for better readability"""
    line = "=" * 80
    print(f"\n{line}\n{title.center(80)}\n{line}\n")

def parse_jwt_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Parse a JWT token without verification to view its contents.
    
    Args:
        token (str): The JWT token to parse
        
    Returns:
        Optional[Dict[str, Any]]: The parsed token or None if invalid
    """
    try:
        # Split the token into parts
        parts = token.split('.')
        if len(parts) != 3:
            logger.error(f"Token doesn't have 3 parts (header.payload.signature)")
            return None
        
        # Decode the header
        header_padded = parts[0] + '=' * (4 - len(parts[0]) % 4)
        header_bytes = base64.b64decode(header_padded.encode('utf-8'))
        header = json.loads(header_bytes)
        
        # Decode the payload
        payload_padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
        payload_bytes = base64.b64decode(payload_padded.encode('utf-8'))
        payload = json.loads(payload_bytes)
        
        return {
            'header': header,
            'payload': payload
        }
    except Exception as e:
        logger.error(f"Error parsing token: {e}")
        return None

def pretty_print_token(token_data: Dict[str, Any]) -> None:
    """
    Pretty print token data
    
    Args:
        token_data (Dict[str, Any]): The token data to print
    """
    if not token_data:
        return
    
    print_header("Token Header")
    print(json.dumps(token_data['header'], indent=2))
    
    print_header("Token Payload")
    print(json.dumps(token_data['payload'], indent=2))
    
    # Print some helpful diagnostics
    payload = token_data['payload']
    current_time = import_time_module().time()
    
    print_header("Token Diagnostics")
    
    if 'exp' in payload:
        exp_time = payload['exp']
        print(f"Token expires at: {exp_time} ({format_timestamp(exp_time)})")
        
        if exp_time < current_time:
            print(f"❌ Token is EXPIRED (expired {format_time_diff(current_time - exp_time)} ago)")
        else:
            print(f"✅ Token is VALID (expires in {format_time_diff(exp_time - current_time)})")
    else:
        print("❌ Token has no expiration (exp) claim")
    
    if 'aud' in payload:
        print(f"Audience: {payload['aud']}")
    else:
        print("❌ Token has no audience (aud) claim")
    
    if 'iss' in payload:
        print(f"Issuer: {payload['iss']}")
    else:
        print("❌ Token has no issuer (iss) claim")

def import_time_module():
    """Import the time module to avoid global import issues"""
    import time
    return time

def format_timestamp(timestamp: int) -> str:
    """Format a timestamp to human-readable format"""
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def format_time_diff(seconds: float) -> str:
    """Format a time difference to human-readable format"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds/60)} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

def fetch_jwks() -> Optional[Dict[str, Any]]:
    """
    Fetch the JWKS from Supabase
    
    Returns:
        Optional[Dict[str, Any]]: The JWKS or None if fetch failed
    """
    if not SUPABASE_URL:
        logger.error("SUPABASE_URL not set in environment variables")
        return None
    
    jwks_url = f"{SUPABASE_URL}/auth/v1/jwks"
    
    try:
        logger.info(f"Fetching JWKS from: {jwks_url}")
        response = requests.get(jwks_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching JWKS: {e}")
        return None

def debug_verify_token(token: str) -> None:
    """
    Debug token verification process step by step
    
    Args:
        token (str): The token to verify
    """
    print_header("Token Verification Debug")
    
    # First parse the token without verification
    print("Step 1: Parsing token without verification...")
    token_data = parse_jwt_without_verification(token)
    
    if not token_data:
        logger.error("Failed to parse token. It may be malformed.")
        return
    
    # Get the header's key ID
    kid = token_data['header'].get('kid')
    alg = token_data['header'].get('alg', 'RS256')
    
    print(f"Token algorithm: {alg}")
    print(f"Token key ID: {kid}")
    
    # Fetch the JWKS
    print("\nStep 2: Fetching JWKS from Supabase...")
    jwks = fetch_jwks()
    
    if not jwks:
        logger.error("Failed to fetch JWKS.")
        return
    
    print(f"JWKS fetched successfully with {len(jwks.get('keys', []))} keys.")
    
    # Find the matching key
    print("\nStep 3: Finding matching key in JWKS...")
    rsa_key = None
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            rsa_key = key
            break
    
    if not rsa_key:
        logger.error(f"No key with ID {kid} found in JWKS.")
        available_kids = [key.get('kid') for key in jwks.get('keys', [])]
        print(f"Available key IDs: {available_kids}")
        return
    
    print(f"Matching key found for kid: {kid}")
    
    # Attempt to verify the token
    print("\nStep 4: Verifying token...")
    try:
        # Try with audience verification
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[alg],
            audience='authenticated',
            options={"verify_exp": True}
        )
        print("✅ Token verified successfully!")
        return
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired.")
    except jwt.InvalidAudienceError:
        print("❌ Invalid audience. Trying without audience verification...")
        try:
            # Try without audience verification
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[alg],
                options={"verify_exp": True, "verify_aud": False}
            )
            print("✅ Token verified without audience check!")
            
            # Check what audience the token has
            aud = token_data['payload'].get('aud')
            print(f"Token audience is {aud} (expected 'authenticated')")
            
            return
        except Exception as e:
            logger.error(f"Failed even without audience verification: {e}")
    except Exception as e:
        logger.error(f"Verification error: {e}")

def main():
    """Main function"""
    print_header("Supabase Token Debugger")
    
    # Check if token is provided as argument
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        # Prompt for token
        print("Please enter your Supabase JWT token:")
        token = input().strip()
    
    if not token:
        logger.error("No token provided.")
        return
    
    # Parse and print token
    token_data = parse_jwt_without_verification(token)
    if token_data:
        pretty_print_token(token_data)
        
        # Perform verification
        debug_verify_token(token)

if __name__ == "__main__":
    main() 