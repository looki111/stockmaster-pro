"""
Test Supabase JWT verification with a public demo project

This script attempts to connect to a public Supabase demo project
and verify JWT functionality.
"""

import requests
import json
import os

# Supabase demo project details
DEMO_PROJECT_URL = "https://supabase.com/dashboard/project/demo"
DEMO_PROJECT_API_URL = "https://demo-default-rtdb.supabase.co"
DEMO_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"

def test_supabase_connection():
    """Test connection to Supabase demo project"""
    print("Testing connection to Supabase demo project...")
    
    # Set up headers
    headers = {
        "apikey": DEMO_ANON_KEY,
        "Content-Type": "application/json"
    }
    
    # Test health endpoint
    try:
        health_url = f"{DEMO_PROJECT_API_URL}/rest/v1/"
        response = requests.get(health_url, headers=headers)
        
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Successfully connected to Supabase demo project")
            print(f"Response: {response.text[:100]}...")
        else:
            print(f"❌ Failed to connect to Supabase demo project: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error connecting to Supabase demo project: {e}")
    
    # Try the JWKS endpoint directly
    try:
        jwks_url = f"{DEMO_PROJECT_API_URL}/auth/v1/jwks"
        response = requests.get(jwks_url, headers=headers)
        
        print(f"\nJWKS endpoint status code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Successfully accessed JWKS endpoint")
            print(f"Response: {response.text[:100]}...")
        else:
            print(f"❌ Failed to access JWKS endpoint: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error accessing JWKS endpoint: {e}")

if __name__ == "__main__":
    test_supabase_connection() 