"""
Local JWT verification test

This script tests JWT verification locally using the jose library
without requiring an external Supabase connection.
"""

import jwt
import time
import json
from datetime import datetime, timedelta, timezone

# Function to create a test JWT token
def create_test_token(secret_key="your-test-secret-key"):
    """Create a test JWT token that expires in 1 hour"""
    payload = {
        "iss": "test-issuer",
        "sub": "1234567890",
        "name": "Test User",
        "role": "authenticated",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600  # Expires in 1 hour
    }
    
    # HS256 is what Supabase uses by default
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

# Function to verify a JWT token
def verify_token(token, secret_key="your-test-secret-key"):
    """Verify a JWT token"""
    try:
        # Decode and verify the token
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError as e:
        return False, f"Invalid token: {str(e)}"
    except Exception as e:
        return False, f"Verification error: {str(e)}"

def main():
    """Main function to test JWT token creation and verification"""
    print("JWT Local Verification Test")
    print("=" * 40)
    
    # Create a test token
    token = create_test_token()
    print(f"Test token created: {token}")
    
    # Verify the token
    is_valid, result = verify_token(token)
    if is_valid:
        print("\n✅ Token verification successful")
        print(f"Payload: {json.dumps(result, indent=2)}")
    else:
        print(f"\n❌ Token verification failed: {result}")
    
    # Test with invalid key
    print("\nTesting with wrong secret key:")
    is_valid, result = verify_token(token, "wrong-secret-key")
    if not is_valid:
        print(f"✅ Expected failure: {result}")
    else:
        print("❓ Unexpected success with wrong key")
    
    # Create an expired token
    expired_payload = {
        "iss": "test-issuer",
        "sub": "1234567890",
        "name": "Test User",
        "exp": int(time.time()) - 3600  # Expired 1 hour ago
    }
    expired_token = jwt.encode(expired_payload, "your-test-secret-key", algorithm="HS256")
    
    print("\nTesting with expired token:")
    is_valid, result = verify_token(expired_token)
    if not is_valid:
        print(f"✅ Expected failure: {result}")
    else:
        print("❓ Unexpected success with expired token")

if __name__ == "__main__":
    main() 