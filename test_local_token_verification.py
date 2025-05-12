"""
Test local token verification function directly

This script tests the Supabase token verification function directly,
without requiring a valid token from Supabase.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add the parent directory to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Supabase values directly for testing
os.environ['SUPABASE_URL'] = "https://supabase.com"
os.environ['SUPABASE_KEY'] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1cGFiYXNlLWRlbW8iLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY0MTc2OTIwMCwiZXhwIjoxOTU3MzQ1NjAwfQ.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE"

# Load environment variables
load_dotenv()

# Override the Supabase auth module with direct values
def override_supabase_config():
    """Override the Supabase configuration directly in the module"""
    from backend.auth import supabase_auth
    supabase_auth.SUPABASE_URL = os.environ['SUPABASE_URL']
    supabase_auth.SUPABASE_KEY = os.environ['SUPABASE_KEY']
    print(f"✅ Overrode Supabase configuration to use: {supabase_auth.SUPABASE_URL}")

# Override Supabase configuration
try:
    override_supabase_config()
except Exception as e:
    print(f"❌ Error overriding Supabase configuration: {e}")

try:
    from backend.auth.supabase_auth import verify_supabase_token, get_supabase_public_key
    print("✅ Successfully imported verification functions")
except ImportError as e:
    print(f"❌ Error importing verification functions: {e}")
    sys.exit(1)

def test_direct_jwks_access():
    """Test direct access to Supabase JWKS without using the library"""
    url = "https://supabase.com/auth/v1/jwks"
    try:
        response = requests.get(url)
        print(f"Direct JWKS request status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Direct JWKS response: {response.text[:100]}...")
        else:
            print(f"Direct JWKS response: {response.text}")
    except Exception as e:
        print(f"Direct JWKS request error: {e}")

def test_jwt_verification():
    """Test the JWT verification functionality"""
    
    print("\nTesting JWT verification environment...")
    print("=" * 40)
    
    # Check environment
    from backend.auth import supabase_auth
    supabase_url = supabase_auth.SUPABASE_URL
    supabase_key = supabase_auth.SUPABASE_KEY
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase URL or Key missing from module configuration")
        return
    
    print(f"✅ SUPABASE_URL in module: {supabase_url}")
    masked_key = f"{supabase_key[:10]}...{supabase_key[-5:]}" if len(supabase_key) > 15 else supabase_key
    print(f"✅ SUPABASE_KEY in module: {masked_key}")
    
    # Try direct JWKS access first
    print("\nTesting direct access to Supabase JWKS...")
    test_direct_jwks_access()
    
    # Test getting the JWKS using the module
    print("\nTesting access to Supabase JWKS using module...")
    try:
        jwks = get_supabase_public_key()
        print(f"✅ Successfully retrieved JWKS from Supabase")
        print(f"✅ Found {len(jwks.get('keys', []))} keys in the JWKS")
        
        # Verify some token structure
        if jwks and 'keys' in jwks and len(jwks['keys']) > 0:
            key = jwks['keys'][0]
            if 'kid' in key:
                print(f"✅ JWKS contains valid key with kid: {key['kid']}")
            else:
                print("❌ JWKS keys missing 'kid' attribute")
        else:
            print("❌ Invalid JWKS format or empty keys list")
            
    except Exception as e:
        print(f"❌ Error getting JWKS from module: {e}")
    
    print("\nJWT verification environment test complete")
    print("For additional diagnostics, check JWKS endpoint directly at:")
    print(f"{supabase_url}/auth/v1/jwks")

if __name__ == "__main__":
    test_jwt_verification()