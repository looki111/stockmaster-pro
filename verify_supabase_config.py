"""
Verify Supabase Configuration

This script checks if your Supabase configuration is valid.
"""

import os
import sys
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("Verifying Supabase configuration...\n")

# Check if values exist
if not SUPABASE_URL:
    print("❌ SUPABASE_URL is missing in your .env file")
    sys.exit(1)
else:
    print(f"✓ SUPABASE_URL found: {SUPABASE_URL}")

if not SUPABASE_KEY:
    print("❌ SUPABASE_KEY is missing in your .env file")
    sys.exit(1)
else:
    masked_key = SUPABASE_KEY[:10] + "..." + SUPABASE_KEY[-5:] if len(SUPABASE_KEY) > 15 else SUPABASE_KEY
    print(f"✓ SUPABASE_KEY found: {masked_key}")

# Validate URL format
url_pattern = r'^https:\/\/[a-zA-Z0-9-]+\.supabase\.co$'
if not re.match(url_pattern, SUPABASE_URL):
    print(f"❌ SUPABASE_URL format is invalid: {SUPABASE_URL}")
    print("   It should follow the pattern: https://your-project-id.supabase.co")
    sys.exit(1)
else:
    print("✓ SUPABASE_URL format is valid")

# Try to import supabase
try:
    from supabase import create_client, Client
    print("✓ Supabase Python package is installed")
except ImportError:
    print("❌ Supabase Python package is not installed")
    print("   Install it with: pip install supabase")
    sys.exit(1)

print("\n✅ Your Supabase configuration is valid!")
print("\nIf you're still experiencing browser DNS issues:")
print("1. Clear your browser cache")
print("2. Check your network connection")
print("3. Make sure your .env file doesn't have any line breaks in the SUPABASE_KEY") 