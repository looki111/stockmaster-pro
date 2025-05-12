"""
Generate Supabase Credentials Helper

This script helps you generate and test proper Supabase credentials for your application.
Follow the instructions to manually enter your Supabase credentials from your project dashboard.
"""

import os
import json
import re
import base64
import requests
from dotenv import load_dotenv

def is_valid_jwt(token):
    """
    Basic validation to check if a string looks like a JWT token
    """
    jwt_pattern = r'^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*$'
    return bool(re.match(jwt_pattern, token))

def is_valid_url(url):
    """
    Basic validation to check if a string looks like a Supabase URL
    """
    url_pattern = r'^https://[a-zA-Z0-9-]+\.supabase\.co$'
    return bool(re.match(url_pattern, url))

def test_supabase_credentials(url, key):
    """
    Test if the provided Supabase credentials work by making a simple API call
    """
    if not url or not key:
        return False, "URL or key is empty"
    
    try:
        # Test with a simple Supabase Auth request
        headers = {
            'apikey': key,
            'Content-Type': 'application/json'
        }
        
        # Just check if we can get a session (even if it's null)
        response = requests.get(f"{url}/auth/v1/user", headers=headers, timeout=5)
        
        # 200 OK or 401 Unauthorized are both fine - they mean the key is valid
        # but 401 means no session which is expected
        if response.status_code in (200, 401):
            return True, "Credentials are valid"
        else:
            return False, f"Invalid response: {response.status_code} - {response.text}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Error testing credentials: {str(e)}"

def update_env_file(url, key, service_key=None):
    """
    Update the .env file with the provided Supabase credentials
    """
    env_path = '.env'
    new_lines = []
    
    if os.path.exists(env_path):
        # Read existing content
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        url_replaced = False
        key_replaced = False
        service_key_replaced = False
        
        # Update existing lines
        for line in lines:
            if line.startswith('SUPABASE_URL='):
                new_lines.append(f'SUPABASE_URL={url}\n')
                url_replaced = True
            elif line.startswith('SUPABASE_KEY='):
                new_lines.append(f'SUPABASE_KEY={key}\n')
                key_replaced = True
            elif service_key and line.startswith('SUPABASE_SERVICE_ROLE_KEY='):
                new_lines.append(f'SUPABASE_SERVICE_ROLE_KEY={service_key}\n')
                service_key_replaced = True
            else:
                new_lines.append(line)
        
        # Add missing entries
        if not url_replaced:
            new_lines.append(f'SUPABASE_URL={url}\n')
        if not key_replaced:
            new_lines.append(f'SUPABASE_KEY={key}\n')
        if service_key and not service_key_replaced:
            new_lines.append(f'SUPABASE_SERVICE_ROLE_KEY={service_key}\n')
    else:
        # Create new .env file
        new_lines = [
            f'SUPABASE_URL={url}\n',
            f'SUPABASE_KEY={key}\n',
        ]
        if service_key:
            new_lines.append(f'SUPABASE_SERVICE_ROLE_KEY={service_key}\n')
    
    # Write updated content
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    return True

def main():
    """
    Main function to run the script
    """
    print("=" * 80)
    print("        Supabase Credentials Generator and Tester for StockMaster Pro")
    print("=" * 80)
    print("\nThis script will help you set up your Supabase credentials for StockMaster Pro.\n")
    
    # Load existing env if available
    load_dotenv()
    existing_url = os.environ.get('SUPABASE_URL', '')
    existing_key = os.environ.get('SUPABASE_KEY', '')
    existing_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
    
    # Instructions for users
    print("INSTRUCTIONS:")
    print("1. Log in to your Supabase dashboard (https://app.supabase.io)")
    print("2. Select your project")
    print("3. Go to Project Settings > API")
    print("4. Copy the URL and anon key (public API key)\n")
    
    # Input URL
    print(f"Current Supabase URL: {existing_url or 'Not set'}")
    url = input("Enter your Supabase URL (press Enter to keep current): ").strip()
    url = url or existing_url
    
    if not url:
        print("\n❌ Error: Supabase URL is required.")
        return
    
    if not is_valid_url(url):
        print(f"\n⚠️ Warning: '{url}' doesn't look like a valid Supabase URL.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    # Input anon key
    print(f"\nCurrent Supabase anon key: {existing_key[:5] + '...' if existing_key else 'Not set'}")
    key = input("Enter your Supabase anon key (press Enter to keep current): ").strip()
    key = key or existing_key
    
    if not key:
        print("\n❌ Error: Supabase anon key is required.")
        return
    
    if not is_valid_jwt(key):
        print(f"\n⚠️ Warning: The provided key doesn't look like a valid JWT token.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    # Test credentials
    print("\nTesting Supabase credentials...")
    is_valid, message = test_supabase_credentials(url, key)
    
    if is_valid:
        print("✅ Supabase credentials are valid!")
    else:
        print(f"❌ Error: {message}")
        confirm = input("Save these credentials anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    # Optionally update service role key
    use_service_key = input("\nDo you want to update the service role key too? (y/n): ").strip().lower() == 'y'
    service_key = None
    
    if use_service_key:
        print(f"Current service role key: {existing_service_key[:5] + '...' if existing_service_key else 'Not set'}")
        service_key = input("Enter your service role key (press Enter to keep current): ").strip()
        service_key = service_key or existing_service_key
        
        if not service_key:
            print("No service role key provided. Continuing without it.")
    
    # Update .env file
    print("\nUpdating .env file...")
    if update_env_file(url, key, service_key if use_service_key else None):
        print("✅ .env file has been updated with your Supabase credentials.")
    else:
        print("❌ Failed to update .env file.")
    
    print("\nYou're all set! Your Supabase credentials have been saved.")
    print("Restart your Flask application to apply the changes.")

if __name__ == "__main__":
    main() 