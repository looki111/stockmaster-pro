#!/usr/bin/env python
"""
Environment Setup Script for StockMaster Pro

This script creates or updates the .env file with required environment variables.
"""

import os
import sys
from datetime import datetime

def create_env_file():
    """Create or update the .env file with essential configuration"""
    print("\n" + "=" * 70)
    print("Setting Up Environment Variables".center(70))
    print("=" * 70)
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("Found existing .env file")
        
        # Backup the existing file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f".env.bak_{timestamp}"
        
        try:
            with open(".env", "r") as src, open(backup_path, "w") as dst:
                dst.write(src.read())
            print(f"✅ Created backup: {backup_path}")
        except Exception as e:
            print(f"⚠️ Could not backup .env file: {e}")
            
        # Read existing content
        try:
            with open(".env", "r") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Could not read .env file: {e}")
            content = ""
    else:
        print("No .env file found, creating a new one")
        content = ""
    
    # Set DEV_MODE in the content
    if "DEV_MODE=" in content:
        # Update existing DEV_MODE
        lines = content.split("\n")
        updated_lines = []
        for line in lines:
            if line.startswith("DEV_MODE="):
                updated_lines.append("DEV_MODE=true")
            else:
                updated_lines.append(line)
        content = "\n".join(updated_lines)
        print("✅ Updated DEV_MODE to true")
    else:
        # Add DEV_MODE if it doesn't exist
        content += "\n# Development mode for token verification\nDEV_MODE=true\n"
        print("✅ Added DEV_MODE=true")
    
    # Add default Supabase configuration if missing
    if "SUPABASE_URL=" not in content:
        content += "\n# Supabase Configuration (replace with your actual values)\n"
        content += "SUPABASE_URL=https://example.supabase.co\n"
        content += "SUPABASE_KEY=your-anon-key-here\n"
        content += "SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here\n"
        print("✅ Added default Supabase configuration")
    
    # Add Flask secret key if missing
    if "SECRET_KEY=" not in content:
        content += "\n# Flask Secret Key\n"
        content += "SECRET_KEY=stockmaster_pro_secret_key\n"
        print("✅ Added Flask Secret Key")
    
    # Write the updated content
    try:
        with open(".env", "w") as f:
            f.write(content)
        print("✅ Successfully updated .env file")
    except Exception as e:
        print(f"❌ Error writing to .env file: {e}")
        return False
    
    print("\nNext steps:")
    print("1. Make sure to update the Supabase configuration in .env with your actual values")
    print("2. Restart your Flask application using: python app.py")
    return True

if __name__ == "__main__":
    create_env_file() 