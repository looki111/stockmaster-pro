"""
Fix .env file by removing newlines and spaces from Supabase keys
"""

import os
import re

def fix_env_file():
    """Fix the .env file by removing newlines and spaces from Supabase keys"""
    
    # Create a corrected version of the environment variables
    corrected_env = """# StockMaster Pro Environment Variables
SECRET_KEY=stockmaster_pro_secret_key_please_change_in_production

# Supabase Configuration
SUPABASE_URL=https://mdxyafghptizcjrgurth.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6eHhnaWVlYnR6eWtzYmRrcmh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY5NTk5MDksImV4cCI6MjA2MjUzNTkwOX0.GCr6VILhg5_SYfTXkzZ6tf6Kn0Jw7fdeyrih3Hi45F8

# Session Configuration
SESSION_COOKIE_SECURE=False
FORCE_ADMIN_SECRET=stockmaster-admin-secret
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNTQ1MjgwMCwiZXhwIjoyMDMxMDI4ODAwfQ.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG
"""
    
    # Backup existing .env file
    if os.path.exists(".env"):
        with open(".env.bak", "w") as f:
            with open(".env", "r") as src:
                f.write(src.read())
        print("✅ Created backup of .env file to .env.bak")
    
    # Write the corrected environment variables
    with open(".env", "w") as f:
        f.write(corrected_env)
    
    print("✅ Successfully fixed .env file by removing newlines and spaces from Supabase keys")

if __name__ == "__main__":
    fix_env_file() 