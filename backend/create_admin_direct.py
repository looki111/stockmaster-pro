"""
Create admin user directly in the database using SQLite
This is a fallback method if the SQLAlchemy approach doesn't work
"""

import os
import sqlite3
import hashlib
import datetime

def create_admin_direct():
    """Create admin user directly in the database"""
    print("\n=== Creating Admin User Directly in Database ===\n")
    
    # Make sure the instance directory exists
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance directory: {instance_path}")
        
    # Use absolute path for database
    db_path = os.path.join(os.path.abspath(instance_path), 'stockmaster.db')
    print(f"Database path: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Connected to database successfully.")
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Creating users table...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                coffee_name TEXT,
                branch_id INTEGER,
                email TEXT,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                last_login TIMESTAMP,
                preferred_language TEXT DEFAULT 'en',
                theme TEXT DEFAULT 'light',
                theme_color TEXT DEFAULT 'blue',
                sidebar_collapsed INTEGER DEFAULT 0,
                dashboard_layout TEXT,
                first_name TEXT,
                last_name TEXT,
                profile_image TEXT,
                job_title TEXT,
                bio TEXT,
                is_superuser INTEGER DEFAULT 0,
                is_system_admin INTEGER DEFAULT 0,
                last_password_change TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked_until TIMESTAMP,
                last_active TIMESTAMP,
                login_ip TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            ''')
            print("Users table created.")
        
        # Check if branch table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='branch'")
        if not cursor.fetchone():
            print("Creating branch table...")
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS branch (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                is_main INTEGER DEFAULT 0,
                shop_id INTEGER,
                weight_unit TEXT DEFAULT 'kg',
                currency TEXT DEFAULT 'SAR',
                time_format TEXT DEFAULT '24',
                invoice_template TEXT DEFAULT 'default',
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            ''')
            print("Branch table created.")
        
        # Create a branch if none exists
        cursor.execute("SELECT id FROM branch LIMIT 1")
        branch = cursor.fetchone()
        
        if not branch:
            print("Creating default branch...")
            now = datetime.datetime.now().isoformat()
            cursor.execute('''
            INSERT INTO branch (name, address, phone, is_active, is_main, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', ("Main Branch", "Main Address", "1234567890", 1, 1, now, now))
            branch_id = cursor.lastrowid
            print(f"Default branch created with ID: {branch_id}")
        else:
            branch_id = branch[0]
            print(f"Using existing branch with ID: {branch_id}")
        
        # Generate password hash (similar to werkzeug's generate_password_hash)
        # This is a simplified version - in production, use werkzeug's function
        def simple_hash(password):
            return f"pbkdf2:sha256:260000${hashlib.sha256(password.encode()).hexdigest()}"
        
        password_hash = simple_hash("admin123")
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        admin = cursor.fetchone()
        
        now = datetime.datetime.now().isoformat()
        
        if not admin:
            print("Creating admin user...")
            cursor.execute('''
            INSERT INTO users (
                username, password, coffee_name, branch_id, email, is_active,
                preferred_language, theme, theme_color, is_superuser, is_system_admin,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "admin", password_hash, "Admin", branch_id, "admin@example.com", 1,
                "en", "light", "blue", 1, 1, now, now
            ))
            admin_id = cursor.lastrowid
            print(f"Admin user created with ID: {admin_id}")
        else:
            admin_id = admin[0]
            print(f"Admin user already exists with ID: {admin_id}")
            
            # Update admin password
            print("Updating admin password...")
            cursor.execute('''
            UPDATE users SET password = ?, updated_at = ? WHERE id = ?
            ''', (password_hash, now, admin_id))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("\n=== Admin Credentials ===")
        print("Username: admin")
        print("Password: admin123")
        print("=========================\n")
        
        print("Admin user created/updated successfully!")
        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

if __name__ == "__main__":
    create_admin_direct()
    
    print("\n=== Next Steps ===")
    print("1. Start the application: python app.py")
    print("2. Log in with username 'admin' and password 'admin123'")
    print("3. If login fails, check the application logs for errors")
