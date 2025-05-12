"""
Fix ENV File Script

This script fixes the .env file by:
1. Ensuring SUPABASE_KEY is on a single line
2. Adding SUPABASE_SERVICE_ROLE_KEY if it doesn't exist
"""

import os
import re
import sys

def fix_env_file():
    try:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if not os.path.exists(env_path):
            print(f"❌ .env file not found at: {env_path}")
            return False
            
        print(f"✓ Found .env file at: {env_path}")
        
        # Read the current content
        with open(env_path, 'r') as file:
            content = file.read()
        
        # Process SUPABASE_KEY to remove line breaks and formatting issues
        supabase_key_match = re.search(r'SUPABASE_KEY=([^\n]*(?:\n[^\n]*)*?)\n', content)
        if supabase_key_match:
            broken_key = supabase_key_match.group(1)
            # Clean up the key by removing spaces, line breaks, etc.
            clean_key = ''.join(broken_key.split())
            
            # Replace the broken key with the clean key
            content = content.replace(f"SUPABASE_KEY={broken_key}", f"SUPABASE_KEY={clean_key}")
            print("✓ Fixed SUPABASE_KEY formatting")
        else:
            print("❌ SUPABASE_KEY not found in .env file")
        
        # Add SUPABASE_SERVICE_ROLE_KEY if it doesn't exist
        if 'SUPABASE_SERVICE_ROLE_KEY' not in content:
            # Create a service role key based on the existing key pattern
            # For example, modify the regular key to be a service role key
            if 'SUPABASE_KEY' in content:
                content += "\n# Service Role Key for admin operations (use your actual service role key)\n"
                content += "SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNTQ1MjgwMCwiZXhwIjoyMDMxMDI4ODAwfQ.example_service_role_key_suffix\n"
                print("✓ Added SUPABASE_SERVICE_ROLE_KEY placeholder")
                print("⚠️ IMPORTANT: Make sure to replace the placeholder with your actual service role key from Supabase")
        else:
            print("✓ SUPABASE_SERVICE_ROLE_KEY already exists in .env file")
        
        # Write the fixed content back to .env
        with open(env_path, 'w') as file:
            file.write(content)
        
        print("\n✅ .env file has been fixed successfully!")
        print("\n⚠️ IMPORTANT REMINDERS:")
        print("1. If you have a placeholder service role key, replace it with your actual key from the Supabase dashboard")
        print("2. Restart any running services or applications to apply the changes")
        print("3. Clear your browser cache to ensure DNS resolution works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing .env file: {e}")
        return False

if __name__ == "__main__":
    fix_env_file() 