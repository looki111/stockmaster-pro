#!/usr/bin/env python
"""
Create Default Environment Variables File

This script creates a default .env file with sample Supabase credentials.
"""

import os

def create_default_env():
    """Create a default .env file with sample credentials"""
    print("Creating default .env file...")
    
    env_content = """# StockMaster Pro Environment Variables
SECRET_KEY=stockmaster_pro_secret_key

# Supabase Configuration
SUPABASE_URL=https://mdxyafghptizcjrgurth.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU0NTI4MDAsImV4cCI6MjAzMTAyODgwMH0.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNTQ1MjgwMCwiZXhwIjoyMDMxMDI4ODAwfQ.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG

# Session Configuration
SESSION_COOKIE_SECURE=False
"""
    
    # Backup existing file if needed
    if os.path.exists(".env"):
        with open(".env.bak", "w") as f:
            with open(".env", "r") as original:
                f.write(original.read())
        print("Backed up existing .env file to .env.bak")
    
    # Write the new .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Default .env file created!")
    print("⚠️ Note: The Supabase credentials are placeholders. You need to replace them with actual values.")

if __name__ == "__main__":
    create_default_env() 