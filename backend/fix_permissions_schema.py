"""
Fix the permissions table schema
"""

import os
import sqlite3

def fix_permissions_schema():
    """Fix the permissions table schema"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')

    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if the permissions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permissions'")
        if not cursor.fetchone():
            print("Permissions table doesn't exist, creating it...")
            cursor.execute('''
            CREATE TABLE permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description VARCHAR(200),
                module VARCHAR(50),
                created_at DATETIME
            )
            ''')
            print("Permissions table created successfully!")
        else:
            # Check if the action column exists
            cursor.execute("PRAGMA table_info(permissions)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'action' not in columns:
                print("Adding 'action' column to permissions table...")
                cursor.execute("ALTER TABLE permissions ADD COLUMN action VARCHAR(50)")
                print("Action column added successfully!")
            else:
                print("Action column already exists in permissions table")

            # Check if the created_at column exists
            if 'created_at' not in columns:
                print("Adding 'created_at' column to permissions table...")
                cursor.execute("ALTER TABLE permissions ADD COLUMN created_at DATETIME")
                print("created_at column added successfully!")
            else:
                print("created_at column already exists in permissions table")

        conn.commit()
        print("Permissions schema fixed successfully!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error fixing permissions schema: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_permissions_schema()
