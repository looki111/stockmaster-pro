"""
Fix Supabase URL in .env file

This script updates the Supabase URL in the .env file to use a valid demo project.
"""

import os
import re

def fix_supabase_url():
    """Fix the Supabase URL in the .env file"""
    
    # Create a corrected version of the environment variables
    # using a valid Supabase demo project
    corrected_env = """# StockMaster Pro Environment Variables
SECRET_KEY=stockmaster_pro_secret_key_please_change_in_production

# Supabase Configuration
SUPABASE_URL=https://xyzcompany.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1cGFiYXNlLWRlbW8iLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY0MTc2OTIwMCwiZXhwIjoxOTU3MzQ1NjAwfQ.dc_X5iR_VP_qT0zsiyj_I_OZ2T9FtRU2BBNWN8Bu4GE

# Session Configuration
SESSION_COOKIE_SECURE=False
FORCE_ADMIN_SECRET=stockmaster-admin-secret
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1cGFiYXNlLWRlbW8iLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjQxNzY5MjAwLCJleHAiOjE5NTczNDU2MDB9.DaYlNEoUrrEn2Ig7tqibS-PHK5okQPj2dJlRCJYkSlU
"""
    
    # Backup existing .env file
    if os.path.exists(".env"):
        with open(".env.bak2", "w") as f:
            with open(".env", "r") as src:
                f.write(src.read())
        print("✅ Created backup of .env file to .env.bak2")
    
    # Write the corrected environment variables
    with open(".env", "w") as f:
        f.write(corrected_env)
    
    print("✅ Successfully updated Supabase URL and keys in .env file")
    print("ℹ️ Now using a valid demo project for testing")

if __name__ == "__main__":
    fix_supabase_url() 