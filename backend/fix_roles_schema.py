"""
Fix the roles table schema
"""

import os
import sqlite3

def fix_roles_schema():
    """Fix the roles table schema"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the roles table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")
        if not cursor.fetchone():
            print("Roles table doesn't exist, creating it...")
            cursor.execute('''
            CREATE TABLE roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(80) NOT NULL UNIQUE,
                description VARCHAR(255),
                is_system BOOLEAN DEFAULT 0,
                created_at DATETIME,
                branch_id INTEGER
            )
            ''')
            print("Roles table created successfully!")
        else:
            # Check if the created_at column exists
            cursor.execute("PRAGMA table_info(roles)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'created_at' not in columns:
                print("Adding 'created_at' column to roles table...")
                cursor.execute("ALTER TABLE roles ADD COLUMN created_at DATETIME")
                print("created_at column added successfully!")
            else:
                print("created_at column already exists in roles table")
            
            # Check if the branch_id column exists
            if 'branch_id' not in columns:
                print("Adding 'branch_id' column to roles table...")
                cursor.execute("ALTER TABLE roles ADD COLUMN branch_id INTEGER")
                print("branch_id column added successfully!")
            else:
                print("branch_id column already exists in roles table")
        
        conn.commit()
        print("Roles schema fixed successfully!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error fixing roles schema: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_roles_schema()
