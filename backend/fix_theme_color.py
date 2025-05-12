import os
import sqlite3
import sys
import glob

# Make sure the working directory is correct
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def add_theme_color_column():
    """Add the theme_color column to the users table if it doesn't exist"""
    print("Checking for theme_color column in users table...")

    # Try to find the database file
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stockmaster.db'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'stockmaster.db'),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'stockmaster.db')
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            print(f"Found database at: {db_path}")
            break

    if not db_path:
        # Try to find any .db file
        db_files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '*.db'))
        if db_files:
            db_path = db_files[0]
            print(f"Found database at: {db_path}")
        else:
            print("No database file found. Searched in:")
            for path in possible_paths:
                print(f"  - {path}")
            return False

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if theme_color column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        print(f"Existing columns in users table: {column_names}")

        if 'theme_color' not in column_names:
            print("Adding theme_color column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN theme_color VARCHAR(20) DEFAULT 'blue'")
            conn.commit()
            print("Column theme_color added successfully!")
        else:
            print("Column theme_color already exists, checking if it has data...")

            # Check if there are any NULL values in the theme_color column
            cursor.execute("SELECT COUNT(*) FROM users WHERE theme_color IS NULL")
            null_count = cursor.fetchone()[0]

            if null_count > 0:
                print(f"Found {null_count} users with NULL theme_color, updating to default 'blue'...")
                cursor.execute("UPDATE users SET theme_color = 'blue' WHERE theme_color IS NULL")
                conn.commit()
                print("Updated NULL theme_color values to default 'blue'")

        # Close the connection
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating database: {e}")
        return False

if __name__ == "__main__":
    print("Starting theme_color column fix...")
    if add_theme_color_column():
        print("Fix completed successfully!")
    else:
        print("Fix failed.")