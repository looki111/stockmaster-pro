"""
Get User Data from Auth Endpoint Using Browser Cookies

This script fetches user data from the /auth/me endpoint using session cookies.
"""

import requests
import json
import os
import browser_cookie3
from dotenv import load_dotenv

def get_auth_me_with_cookie():
    """
    Fetch user data from the /auth/me endpoint using the browser cookie
    """
    # Set up the base URL for the API request
    base_url = "http://localhost:5000"
    endpoint = "/auth/me"
    url = base_url + endpoint
    
    # Set up headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Try to get cookies from all browsers
    try:
        print("Attempting to get cookies from Chrome...")
        cookies = browser_cookie3.chrome(domain_name="localhost")
        print("Chrome cookies retrieved successfully")
    except Exception as e:
        print(f"Could not get Chrome cookies: {str(e)}")
        try:
            print("Attempting to get cookies from Firefox...")
            cookies = browser_cookie3.firefox(domain_name="localhost")
            print("Firefox cookies retrieved successfully")
        except Exception as e:
            print(f"Could not get Firefox cookies: {str(e)}")
            try:
                print("Attempting to get cookies from Edge...")
                cookies = browser_cookie3.edge(domain_name="localhost")
                print("Edge cookies retrieved successfully")
            except Exception as e:
                print(f"Could not get Edge cookies: {str(e)}")
                print("Failed to get cookies from any browser.")
                return None
    
    # Make the request with cookies
    try:
        print("\nAttempting to fetch user data from /auth/me using browser cookies...")
        response = requests.get(url, headers=headers, cookies=cookies)
        
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
    print("=" * 60)
    print("SUPABASE USER DATA FETCHER (BROWSER COOKIES)")
    print("=" * 60)
    print("This script will attempt to use your browser cookies to fetch")
    print("user data from the /auth/me endpoint.")
    print("\nMake sure:")
    print("1. You have logged in through the browser")
    print("2. The Flask server is running on localhost:5000")
    print("3. You have the browser_cookie3 package installed")
    print("   (pip install browser-cookie3)")
    print("=" * 60)
    
    # Ask user if they want to proceed
    proceed = input("\nDo you want to proceed? (y/n): ").strip().lower() == 'y'
    if not proceed:
        print("Operation cancelled.")
        exit()
    
    # Fetch user data
    user_data = get_auth_me_with_cookie()
    
    if not user_data:
        print("\nNo user data found or error occurred.")
        print("Possible reasons:")
        print("1. You are not logged in through the browser")
        print("2. Your session cookie is invalid or expired")
        print("3. The Flask server is not running")
        print("4. The /auth/me endpoint has an issue")
        
        print("\nTry logging in first through the web interface.") 