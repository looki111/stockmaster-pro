"""
Add the theme_color column to the users table
"""

import os
import sqlite3
import sys

def add_theme_color_column():
    """Add the theme_color column to the users table"""
    print("Starting to add theme_color column to users table...")
    
    # Find the database file
    db_paths = [
        os.path.join(os.path.dirname(__file__), 'stockmaster.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {db_path}")
            break
    
    if not db_path:
        print("Database file not found. Searched in:")
        for path in db_paths:
            print(f"  - {path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Users table does not exist!")
            conn.close()
            return False
        
        # Check if theme_color column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns in users table: {columns}")
        
        if 'theme_color' not in columns:
            print("Adding theme_color column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN theme_color VARCHAR(20) DEFAULT 'blue'")
            conn.commit()
            print("theme_color column added successfully!")
        else:
            print("theme_color column already exists.")
        
        # Close the connection
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if add_theme_color_column():
        print("Successfully added theme_color column to users table.")
    else:
        print("Failed to add theme_color column to users table.")
