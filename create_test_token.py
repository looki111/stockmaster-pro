"""
Create Test Supabase Token

This script creates a test JWT token with the correct format for Supabase.
This is not a real token but will have valid JWT structure for testing frontend code.
"""

import base64
import json
import os
import time
import hmac
import hashlib
from dotenv import load_dotenv

def create_test_token():
    """
    Create a test JWT token for Supabase with the correct format
    """
    # Create header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # Create payload with Supabase-specific claims
    payload = {
        "iss": "supabase",
        "ref": "mdxyafghptizcjrgurth",  # A fake reference ID
        "role": "anon",
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400  # Expires in 24 hours
    }
    
    # Create a fake signing key
    signing_key = "thisisaplaceholdersigningkeyfordevelopmentonly12345"
    
    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    # Create signature
    message = f"{header_encoded}.{payload_encoded}"
    signature = hmac.new(
        signing_key.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    # Combine to form the JWT
    token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
    
    return token

def update_env_file(token):
    """
    Update the .env file with the test token
    """
    env_path = '.env'
    new_lines = []
    
    if os.path.exists(env_path):
        # Read existing content
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        key_replaced = False
        
        # Update existing lines
        for line in lines:
            if line.startswith('SUPABASE_KEY='):
                new_lines.append(f'SUPABASE_KEY={token}\n')
                key_replaced = True
            else:
                new_lines.append(line)
        
        # Add missing entry if needed
        if not key_replaced:
            new_lines.append(f'SUPABASE_KEY={token}\n')
    else:
        # Create new .env file
        new_lines = [
            f'SUPABASE_URL=https://mdxyafghptizcjrgurth.supabase.co\n',
            f'SUPABASE_KEY={token}\n'
        ]
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    return True

if __name__ == "__main__":
    print("Creating test Supabase token...")
    token = create_test_token()
    print(f"Token created: {token[:15]}...{token[-10:]}")
    
    update = input("Do you want to update your .env file with this token? (y/n): ").strip().lower()
    if update == 'y':
        if update_env_file(token):
            print("✅ .env file updated with test token.")
            print("⚠️ WARNING: This is not a real Supabase token and will not work for actual API calls.")
            print("It's only for testing frontend code that requires valid JWT format.")
            print("Restart your Flask application to apply the changes.")
        else:
            print("❌ Failed to update .env file.") 