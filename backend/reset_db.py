import os
import sys
import shutil
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_database():
    """Delete the SQLite database file and recreate it"""
    print("Resetting database...")

    # Get the database path
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    db_path = os.path.join(db_dir, 'stockmaster.db')
    
    # Make sure the instance directory exists
    Path(db_dir).mkdir(exist_ok=True)
    
    # Check if database file exists and backup if it does
    if os.path.exists(db_path):
        backup_path = db_path + '.backup'
        try:
            print(f"Backing up database to {backup_path}")
            # Make sure we close any open connections
            import sqlite3
            try:
                conn = sqlite3.connect(db_path)
                conn.close()
            except:
                pass
                
            # Remove old backup if it exists
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
            # Copy the file instead of renaming to avoid "in use" errors
            shutil.copy2(db_path, backup_path)
            os.remove(db_path)
            print("Database backup created and original deleted")
        except Exception as e:
            print(f"Error backing up database: {e}")
            print("Will attempt to continue...")
    
    # Now initialize the database
    try:
        print("Initializing new database...")
        from init_db import init_db
        init_db()
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

if __name__ == "__main__":
    if reset_database():
        print("Database reset completed successfully")
    else:
        print("Database reset failed") 