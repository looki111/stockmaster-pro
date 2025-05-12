"""
Get User Data from Auth Endpoint

This script fetches user data from the /auth/me endpoint.
"""

import requests
import json
import os
from dotenv import load_dotenv

def get_auth_me(token=None):
    """
    Fetch user data from the /auth/me endpoint using the given token or environment token
    """
    # Get base URL from environment
    load_dotenv()
    
    # Set up the base URL for the API request
    base_url = "http://localhost:5000"
    endpoint = "/auth/me"
    url = base_url + endpoint
    
    # Set up headers with token if provided
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Get token from session cookie
    try:
        print("Attempting to fetch user data from /auth/me...")
        response = requests.get(url, headers=headers)
        
        # Print response status
        print(f"Response status: {response.status_code}")
        
        # Print response content
        if response.status_code == 200:
            data = response.json()
            print("\nUser Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Error response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching user data: {str(e)}")
        return None

if __name__ == "__main__":
    # Try to get token from environment
    load_dotenv()
    token = os.environ.get('SUPABASE_TOKEN')
    
    print("=" * 60)
    print("SUPABASE USER DATA FETCHER")
    print("=" * 60)
    
    # If token is in environment, use it, otherwise ask user
    if token:
        print(f"Found token in environment: {token[:10]}...")
        use_env_token = input("Use this token? (y/n): ").strip().lower() == 'y'
        if not use_env_token:
            token = None
    
    # If no token was found or user didn't want to use it, ask for a new one
    if not token:
        use_token = input("Do you want to provide a token? (y/n): ").strip().lower() == 'y'
        if use_token:
            token = input("Enter your authentication token: ").strip()
    
    # Fetch user data
    user_data = get_auth_me(token)
    
    if not user_data:
        print("\nNo user data found or error occurred.")
        print("Possible reasons:")
        print("1. You are not logged in")
        print("2. Your token is invalid or expired")
        print("3. The Flask server is not running")
        print("4. The /auth/me endpoint has an issue")
        
        print("\nTry logging in first through the web interface.") 