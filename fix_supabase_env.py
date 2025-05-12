"""
Fix Supabase Environment Variables

This script fixes the .env file by:
1. Ensuring Supabase credentials are present
2. Fixing any line breaks in the tokens
"""

import os
import re

def fix_env_file():
    """
    Fixes the .env file with properly formatted Supabase credentials.
    """
    env_path = '.env'
    
    # Check if .env exists
    if not os.path.exists(env_path):
        print(f"❌ Error: .env file not found at {env_path}")
        return False
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Process all lines
    new_lines = []
    skip_next = False
    url_found = False
    key_found = False
    service_key_found = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip lines that are part of a multi-line token that we've already processed
        if skip_next:
            skip_next = False
            i += 1
            continue
        
        # Check for SUPABASE_URL
        if line.startswith('SUPABASE_URL='):
            url_found = True
            new_lines.append('SUPABASE_URL=https://mdxyafghptizcjrgurth.supabase.co\n')
        
        # Check for SUPABASE_KEY
        elif line.startswith('SUPABASE_KEY='):
            key_found = True
            # Collect all lines of the key
            full_key = line.strip()[len('SUPABASE_KEY='):]
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(('#', 'SUPABASE_', 'SECRET_', 'FORCE_')):
                full_key += lines[j].strip()
                j += 1
            
            # Clean up the key
            full_key = ''.join(full_key.split())
            
            # Add the fixed key
            new_lines.append(f'SUPABASE_KEY={full_key}\n')
            
            # Skip lines we've processed
            skip_next = True
            i = j - 1
        
        # Check for SUPABASE_SERVICE_ROLE_KEY
        elif line.startswith('SUPABASE_SERVICE_ROLE_KEY='):
            service_key_found = True
            # Collect all lines of the key
            full_key = line.strip()[len('SUPABASE_SERVICE_ROLE_KEY='):]
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(('#', 'SUPABASE_', 'SECRET_', 'FORCE_')):
                full_key += lines[j].strip()
                j += 1
            
            # Clean up the key
            full_key = ''.join(full_key.split())
            
            # Add the fixed key
            new_lines.append(f'SUPABASE_SERVICE_ROLE_KEY={full_key}\n')
            
            # Skip lines we've processed
            skip_next = True
            i = j - 1
        
        # Keep other lines
        else:
            new_lines.append(line)
        
        i += 1
    
    # Add missing entries if needed
    if not url_found:
        new_lines.append('SUPABASE_URL=https://mdxyafghptizcjrgurth.supabase.co\n')
    
    if not key_found:
        new_lines.append('SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTU0NTI4MDAsImV4cCI6MjAzMTAyODgwMH0.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG\n')
    
    if not service_key_found:
        new_lines.append('SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1keHlhZmdocHRpemNqcmd1cnRoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcxNTQ1MjgwMCwiZXhwIjoyMDMxMDI4ODAwfQ.abcdefghijklmnopqrstuvwxyz123456789ABCDEFG\n')
    
    # Write the updated content back to the file
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ .env file has been fixed with proper Supabase credentials.")
    print("ℹ️ Note: Make sure to replace the placeholder values with your actual Supabase credentials.")
    return True

if __name__ == "__main__":
    fix_env_file() 