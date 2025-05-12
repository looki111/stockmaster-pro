"""
Check users in the database
"""

import os
import sqlite3

def check_users():
    """Check users in the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check users
        cursor.execute("SELECT id, username, password, email FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database")
            
            # Create a default admin user
            from werkzeug.security import generate_password_hash
            
            # Check if branches table exists and has at least one branch
            cursor.execute("SELECT id FROM branches LIMIT 1")
            branch = cursor.fetchone()
            
            if not branch:
                print("Creating default branch...")
                cursor.execute("INSERT INTO branches (name, is_active, is_main) VALUES ('Main Branch', 1, 1)")
                branch_id = cursor.lastrowid
            else:
                branch_id = branch[0]
            
            # Create default admin user
            print(f"Creating default admin user with branch_id {branch_id}...")
            hashed_password = generate_password_hash("admin123")
            cursor.execute("""
                INSERT INTO users (
                    username, password, coffee_name, branch_id, email, 
                    is_active, preferred_language, theme, is_superuser, is_system_admin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "admin", hashed_password, "Admin", branch_id, "admin@example.com", 
                1, "en", "light", 1, 1
            ))
            
            # Create roles if they don't exist
            cursor.execute("SELECT id FROM roles WHERE name = 'admin' LIMIT 1")
            admin_role = cursor.fetchone()
            
            if not admin_role:
                print("Creating admin role...")
                cursor.execute("INSERT INTO roles (name, description, is_system) VALUES ('admin', 'Administrator', 1)")
                admin_role_id = cursor.lastrowid
            else:
                admin_role_id = admin_role[0]
            
            # Assign admin role to admin user
            user_id = cursor.lastrowid
            print(f"Assigning admin role {admin_role_id} to user {user_id}...")
            cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, admin_role_id))
            
            conn.commit()
            print("Default admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
        else:
            print(f"Found {len(users)} users in the database:")
            for user in users:
                print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[3]}")
        
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error checking users: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()
