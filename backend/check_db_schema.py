"""
Check database schema
"""

import os
import sqlite3

def check_db_schema():
    """Check database schema"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check users table schema
        print("Checking users table schema...")
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        # Print column information
        print("Users table columns:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
        # Check if theme_color column exists
        theme_color_exists = any(column[1] == 'theme_color' for column in columns)
        print(f"theme_color column exists: {theme_color_exists}")
        
        # Check if there are any users
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}")
        
        return True
    except Exception as e:
        print(f"Error checking database schema: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_schema()
