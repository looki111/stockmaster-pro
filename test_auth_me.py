#!/usr/bin/env python
"""
Test Auth Me Endpoint

This script tests the /auth/me endpoint with proper debugging information.
It helps diagnose issues with the Supabase authentication system.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

def decode_jwt(token):
    """Decode a JWT token to inspect its contents"""
    if not token:
        return None
    
    try:
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            print(f"⚠️ Invalid token format: {token[:20]}...")
            return None
        
        # Add padding to avoid base64 errors
        def fix_padding(part):
            padding_needed = len(part) % 4
            if padding_needed:
                return part + '=' * (4 - padding_needed)
            return part
        
        # Decode header and payload
        header = json.loads(base64.b64decode(fix_padding(parts[0].replace('-', '+').replace('_', '/'))).decode('utf-8'))
        payload = json.loads(base64.b64decode(fix_padding(parts[1].replace('-', '+').replace('_', '/'))).decode('utf-8'))
        
        return {
            "header": header,
            "payload": payload,
            "signature": parts[2][:10] + "..." # Just show part of the signature
        }
    except Exception as e:
        print(f"⚠️ Error decoding token: {e}")
        return None

def test_auth_me():
    """Test the /auth/me endpoint with token from environment"""
    print("\n🔑 SUPABASE AUTH TEST TOOL 🔑\n")
    
    # 1. Check environment variables
    print("Checking environment variables...")
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    supabase_jwt_secret = os.getenv('SUPABASE_JWT_SECRET')
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in environment!")
    else:
        print(f"✅ SUPABASE_URL found: {supabase_url}")
    
    if not supabase_key:
        print("❌ SUPABASE_KEY not found in environment!")
    else:
        print(f"✅ SUPABASE_KEY found: {supabase_key[:15]}...")
        
        # Decode the key to check its format
        decoded_key = decode_jwt(supabase_key)
        if decoded_key:
            print("\nDecoded SUPABASE_KEY:")
            print(f"Header: {json.dumps(decoded_key['header'], indent=2)}")
            print(f"Payload: {json.dumps(decoded_key['payload'], indent=2)}")
            print(f"Signature: {decoded_key['signature']}")
            
            # Check token expiration
            if 'exp' in decoded_key['payload']:
                import time
                exp_time = decoded_key['payload']['exp']
                current_time = int(time.time())
                if exp_time > current_time:
                    print(f"✅ Token is valid until {time.ctime(exp_time)}")
                else:
                    print(f"❌ Token is EXPIRED! (Expired on {time.ctime(exp_time)})")
            
            # Check role in the token
            if 'role' in decoded_key['payload']:
                print(f"Token role: {decoded_key['payload']['role']}")
    
    print("\n------------------------------------------------\n")
    
    # 2. Get a token for testing
    token = None
    
    # First try: Use token from environment
    if supabase_key and supabase_key.startswith('eyJ'):
        token = supabase_key
        print("Using SUPABASE_KEY from environment as token")
    
    # If no token found, ask user to enter one
    if not token:
        print("No valid token found in environment.")
        token_input = input("Enter a valid JWT token (or press Enter to skip): ").strip()
        if token_input:
            token = token_input
        else:
            print("❌ No token provided, cannot test /auth/me endpoint")
            return
    
    print("\n------------------------------------------------\n")
    
    # 3. Test /auth/me endpoint
    print("Testing /auth/me endpoint...")
    
    base_url = "http://localhost:5000"  # Default Flask development server
    endpoint = "/auth/me"
    url = base_url + endpoint
    
    # Set up headers with token
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Make the request
    try:
        print(f"Sending request to {url}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        
        response = requests.get(url, headers=headers)
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        
        # Try to parse as JSON
        try:
            data = response.json()
            print("\nResponse JSON data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except:
            print("\nResponse is not JSON. Text content:")
            print(response.text[:500])  # Show first 500 chars
        
        # Check for common issues
        if response.status_code == 401:
            print("\n❌ Authentication failed (401 Unauthorized)")
            print("Possible causes:")
            print("1. Invalid token")
            print("2. Token is expired")
            print("3. Token does not have the required permissions")
            
        elif response.status_code == 500:
            print("\n❌ Server error (500 Internal Server Error)")
            print("Check server logs for more details")
            
        elif "text/html" in response.headers.get("Content-Type", ""):
            print("\n⚠️ The response is HTML instead of JSON")
            print("This suggests the endpoint is redirecting to a login page or returning an error page")
        
        return response
        
    except Exception as e:
        print(f"\n❌ Error making request: {e}")
        return None

if __name__ == "__main__":
    test_auth_me() 