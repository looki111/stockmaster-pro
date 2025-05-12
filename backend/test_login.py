"""
Test login functionality
"""

import requests
import sys

def test_login(username, password):
    """Test login functionality"""
    try:
        # Make a POST request to the login endpoint
        response = requests.post(
            "http://localhost:5000/login",
            data={"username": username, "password": password},
            allow_redirects=False
        )
        
        # Check if login was successful
        if response.status_code == 302:  # Redirect after successful login
            print(f"Login successful for user {username}!")
            print(f"Redirect URL: {response.headers.get('Location')}")
            return True
        else:
            print(f"Login failed for user {username}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing login: {e}")
        return False

if __name__ == "__main__":
    # Get username and password from command line arguments
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = "admin"
        password = "admin123"
    
    test_login(username, password)
