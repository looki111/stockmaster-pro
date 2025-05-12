"""
Check Supabase Service Role Key

This script checks if the SUPABASE_SERVICE_ROLE_KEY is properly loaded from the .env file.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("Checking Supabase environment variables...\n")

if not SUPABASE_URL:
    print("❌ SUPABASE_URL is not set in the .env file")
else:
    print(f"✓ SUPABASE_URL: {SUPABASE_URL}")

if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY is not set in the .env file")
else:
    masked_key = SUPABASE_KEY[:10] + "..." + SUPABASE_KEY[-5:] if len(SUPABASE_KEY) > 15 else SUPABASE_KEY
    print(f"✓ SUPABASE_KEY: {masked_key}")
    
    # Check for line breaks
    if '\n' in SUPABASE_KEY:
        print("⚠️ SUPABASE_KEY still contains line breaks!")
    else:
        print("✓ SUPABASE_KEY is properly formatted")

if not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ SUPABASE_SERVICE_ROLE_KEY is not set in the .env file")
else:
    masked_key = SUPABASE_SERVICE_ROLE_KEY[:10] + "..." + SUPABASE_SERVICE_ROLE_KEY[-5:] if len(SUPABASE_SERVICE_ROLE_KEY) > 15 else SUPABASE_SERVICE_ROLE_KEY
    print(f"✓ SUPABASE_SERVICE_ROLE_KEY: {masked_key}")
    
    # Check for placeholders
    if 'example_service_role_key_suffix' in SUPABASE_SERVICE_ROLE_KEY:
        print("⚠️ SUPABASE_SERVICE_ROLE_KEY contains a placeholder value. Please replace it with your actual service role key from the Supabase dashboard.")
    
    # Check roles in JWT
    import json
    import base64
    
    try:
        # Parse the JWT to check the role claim
        parts = SUPABASE_SERVICE_ROLE_KEY.split('.')
        if len(parts) >= 2:
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 != 0 else ''
            decoded_payload = base64.b64decode(payload)
            payload_json = json.loads(decoded_payload)
            
            role = payload_json.get('role')
            if role == 'service_role':
                print(f"✓ JWT role is correct: {role}")
            else:
                print(f"⚠️ JWT role is not 'service_role', found: {role}")
        else:
            print("⚠️ Could not parse JWT to verify role claim")
    except Exception as e:
        print(f"⚠️ Error checking JWT role: {e}")

print("\n✅ Environment variables check complete!")
print("\nNext steps:")
print("1. If you need to update the service role key, edit the .env file manually")
print("2. Make sure you restart any running applications after updating the .env file")
print("3. Test administrative functions like setting a user as admin") 