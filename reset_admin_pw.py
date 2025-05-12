#!/usr/bin/env python
"""
Direct Admin Password Reset Script

This script directly updates the admin user password in the SQLite database.
USE WITH CAUTION: This bypasses any application-level validation.
"""

import os
import sys
import sqlite3
import hashlib
import getpass
from pathlib import Path

def reset_admin_password():
    """Reset the admin user password directly in the database"""
    print("\n🔐 EMERGENCY ADMIN PASSWORD RESET 🔐\n")
    
    # Find the database
    possible_db_paths = [
        "backend/instance/stockmaster.db",
        "instance/stockmaster.db",
        "backend/stockmaster.db",
        "stockmaster.db"
    ]
    
    db_path = None
    for path in possible_db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Database file not found. Checked the following paths:")
        for path in possible_db_paths:
            print(f"  - {path}")
        return False
    
    print(f"✅ Found database at: {db_path}")
    
    # Get new password
    email = input("Admin email (leave blank for admin@gmail.com): ").strip() or "admin@gmail.com"
    password = getpass.getpass("New password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("❌ Passwords do not match.")
        return False
    
    if not password:
        print("❌ Password cannot be empty.")
        return False
    
    # Hash the password - we're using basic SHA256 as a fallback
    # This may need to be adjusted based on the actual hashing algorithm used by the app
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check which table structure we have
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'users' in tables:
            # Check which columns are in the users table
            cursor.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Try to find the admin user
            if 'email' in columns:
                cursor.execute("SELECT id FROM users WHERE email = ? OR email = 'admin@gmail.com' OR username = 'admin' LIMIT 1", (email,))
            else:
                cursor.execute("SELECT id FROM users WHERE username = 'admin' LIMIT 1")
            
            admin = cursor.fetchone()
            
            if admin:
                admin_id = admin[0]
                print(f"✅ Found admin user with ID: {admin_id}")
                
                # Update password based on available columns
                if 'password_hash' in columns:
                    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, admin_id))
                elif 'password' in columns:
                    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, admin_id))
                else:
                    print("❌ Could not determine password column in users table.")
                    conn.close()
                    return False
                
                conn.commit()
                print(f"✅ Password updated for admin user!")
                
            else:
                print("❌ Admin user not found. Creating a new admin user...")
                
                # Create a new admin user based on available columns
                if 'email' in columns and 'password_hash' in columns:
                    cursor.execute("""
                        INSERT INTO users (username, email, password_hash, role)
                        VALUES ('admin', ?, ?, 'admin')
                    """, (email, hashed_password))
                elif 'email' in columns and 'password' in columns:
                    cursor.execute("""
                        INSERT INTO users (username, email, password, role)
                        VALUES ('admin', ?, ?, 'admin')
                    """, (email, hashed_password))
                else:
                    print("❌ Could not determine how to create a new admin user.")
                    conn.close()
                    return False
                
                conn.commit()
                print("✅ Created new admin user!")
        
        elif 'user' in tables:
            # Alternative table name
            # Check for admin user
            cursor.execute("SELECT id FROM user WHERE email = ? OR email = 'admin@gmail.com' OR username = 'admin' LIMIT 1", (email,))
            admin = cursor.fetchone()
            
            if admin:
                admin_id = admin[0]
                print(f"✅ Found admin user with ID: {admin_id}")
                
                # Update password (try different column names)
                try:
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", (hashed_password, admin_id))
                    conn.commit()
                    print(f"✅ Password updated for admin user!")
                except sqlite3.OperationalError:
                    try:
                        cursor.execute("UPDATE user SET password_hash = ? WHERE id = ?", (hashed_password, admin_id))
                        conn.commit()
                        print(f"✅ Password updated for admin user!")
                    except sqlite3.OperationalError:
                        print("❌ Could not update password. Unknown column structure.")
                        conn.close()
                        return False
            else:
                print("❌ Admin user not found and creation not supported for this table structure.")
                conn.close()
                return False
        
        else:
            print("❌ Could not find users or user table in the database.")
            print("Available tables:", tables)
            conn.close()
            return False
        
        conn.close()
        
        print("\n🔑 Reset complete! You can now login with:")
        print(f"Email: {email}")
        print(f"Password: {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    reset_admin_password() 