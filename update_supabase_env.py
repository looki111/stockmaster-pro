"""
Update Supabase Environment Variables

This script updates the .env file with the necessary Supabase credentials.
"""

import os
import re

def update_env_file():
    """
    Updates the .env file with Supabase credentials.
    """
    env_path = '.env'
    
    # Check if .env exists
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        env_content = ''
    
    # Add or update Supabase URL
    if 'SUPABASE_URL=' not in env_content:
        if env_content and not env_content.endswith('\n'):
            env_content += '\n'
        env_content += 'SUPABASE_URL=https://your-project-id.supabase.co\n'
    else:
        # URL already exists, no need to update
        pass
    
    # Add or update Supabase Key
    if 'SUPABASE_KEY=' not in env_content:
        if env_content and not env_content.endswith('\n'):
            env_content += '\n'
        env_content += 'SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU0NTI4MDAsImV4cCI6MjAzMTAyODgwMH0.example_anon_key_suffix\n'
    else:
        # Key already exists, no need to update
        pass
    
    # Write the updated content back to the file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ .env file has been updated with Supabase credentials.")
    print("ℹ️ Note: Make sure to replace the placeholder values with your actual Supabase credentials.")

if __name__ == "__main__":
    update_env_file() 