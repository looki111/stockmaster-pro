"""
Install the fixed Supabase client as the main client

This script copies the fixed Supabase client to the main client file,
backing up the original first.
"""

import os
import shutil
import datetime

def install_fixed_client():
    """Install the fixed Supabase client as the main client"""
    print("Installing fixed Supabase client...")
    
    # Source and destination paths
    source_file = "backend/auth/fixed_supabase_client.py"
    dest_file = "backend/auth/supabase_client.py"
    
    # Check if the source file exists
    if not os.path.exists(source_file):
        print(f"❌ Error: Source file {source_file} not found")
        return False
    
    # If the destination file exists, create a backup
    if os.path.exists(dest_file):
        # Create a timestamp for the backup
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = f"{dest_file}.bak.{timestamp}"
        
        # Copy the original file to a backup
        shutil.copy2(dest_file, backup_file)
        print(f"✅ Backed up original {dest_file} to {backup_file}")
    
    # Copy the fixed client to the destination
    shutil.copy2(source_file, dest_file)
    print(f"✅ Installed fixed client as {dest_file}")
    
    return True

def main():
    """Main function"""
    print("Installing Fixed Supabase Client")
    print("=" * 40)
    
    # Install the fixed client
    if install_fixed_client():
        print("\nInstallation complete!")
        print("\nNext steps:")
        print("1. Restart your application")
        print("2. If you encounter any issues, you can restore the backup file")
    else:
        print("\nInstallation failed. See errors above.")

if __name__ == "__main__":
    main() 