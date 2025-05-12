"""
Check Supabase Environment Variables

This script checks if the Supabase URL and Key are properly loaded from the .env file.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("Checking Supabase environment variables...\n")

# Check if the .env file exists
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if not os.path.exists(env_path):
    print(f"❌ .env file not found at: {env_path}")
    sys.exit(1)
else:
    print(f"✓ .env file found at: {env_path}")

# Check if SUPABASE_URL is set and valid
if not SUPABASE_URL:
    print("❌ SUPABASE_URL is not set in the .env file")
    sys.exit(1)
else:
    print(f"✓ SUPABASE_URL: {SUPABASE_URL}")

# Check if SUPABASE_KEY is set and valid
if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY is not set in the .env file")
    sys.exit(1)
else:
    # Only show part of the key for security
    masked_key = SUPABASE_KEY[:10] + "..." + SUPABASE_KEY[-5:] if len(SUPABASE_KEY) > 15 else SUPABASE_KEY
    print(f"✓ SUPABASE_KEY: {masked_key}")
    
    # Count newlines in the key, which would indicate a malformed key
    newlines = SUPABASE_KEY.count('\n')
    if newlines > 0:
        print(f"❌ SUPABASE_KEY contains {newlines} newline character(s). The key should be a single line!")
        sys.exit(1)
    
    # Check for common formatting issues
    if ' ' in SUPABASE_KEY or '\t' in SUPABASE_KEY or '\r' in SUPABASE_KEY:
        print("❌ SUPABASE_KEY contains whitespace characters that may cause issues")
        sys.exit(1)

print("\n✅ Supabase environment variables are properly loaded!")
print("\nNext steps:")
print("1. If you previously saw 'DNS_PROBE_POSSIBLE' errors, try clearing your browser cache")
print("2. Run the test Supabase app: python test_supabase_app.py")
print("3. Open http://localhost:5001 in your browser to test the connection") 