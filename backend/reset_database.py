"""
Reset the database completely
"""

import os
import sys
import shutil
import sqlite3

def reset_database():
    """Reset the database completely"""
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    # Backup the existing database if it exists
    if os.path.exists(db_path):
        backup_path = db_path + '.bak'
        print(f"Backing up existing database to {backup_path}")
        shutil.copy2(db_path, backup_path)
        
        # Remove the existing database
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    # Create the instance directory if it doesn't exist
    instance_dir = os.path.dirname(db_path)
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
    
    # Create a new empty database
    print("Creating new empty database...")
    conn = sqlite3.connect(db_path)
    
    # Create users table
    print("Creating users table...")
    conn.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        coffee_name VARCHAR(100),
        branch_id INTEGER,
        email VARCHAR(120),
        phone VARCHAR(20),
        is_active BOOLEAN DEFAULT 1,
        last_login DATETIME,
        preferred_language VARCHAR(2) DEFAULT 'ar',
        theme VARCHAR(10) DEFAULT 'light',
        theme_color VARCHAR(20) DEFAULT 'blue',
        sidebar_collapsed BOOLEAN DEFAULT 0,
        dashboard_layout TEXT,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        profile_image VARCHAR(255),
        job_title VARCHAR(100),
        bio TEXT,
        is_superuser BOOLEAN DEFAULT 0,
        is_system_admin BOOLEAN DEFAULT 0,
        last_password_change DATETIME,
        failed_login_attempts INTEGER DEFAULT 0,
        account_locked_until DATETIME,
        last_active DATETIME,
        login_ip VARCHAR(45),
        created_at DATETIME,
        updated_at DATETIME
    )
    ''')
    
    # Create branches table
    print("Creating branches table...")
    conn.execute('''
    CREATE TABLE branches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        address VARCHAR(200),
        phone VARCHAR(20),
        email VARCHAR(120),
        is_active BOOLEAN DEFAULT 1,
        is_main BOOLEAN DEFAULT 0,
        created_at DATETIME,
        shop_id INTEGER,
        manager_name VARCHAR(100),
        opening_hours VARCHAR(100),
        location_lat FLOAT,
        location_lng FLOAT,
        description TEXT,
        image VARCHAR(255),
        weight_unit VARCHAR(10) DEFAULT 'kg',
        currency VARCHAR(10) DEFAULT 'SAR',
        time_format VARCHAR(10) DEFAULT '24',
        invoice_template VARCHAR(50) DEFAULT 'default',
        invoice_fields TEXT,
        order_types TEXT,
        tax_rate FLOAT DEFAULT 15.0,
        pos_printer VARCHAR(100),
        barcode_printer VARCHAR(100),
        pos_hardware TEXT,
        quick_pos_mode BOOLEAN DEFAULT 0,
        shift_closing_time TIME,
        inventory_sync BOOLEAN DEFAULT 1,
        whatsapp_api VARCHAR(200),
        sms_api VARCHAR(200),
        marketing_enabled BOOLEAN DEFAULT 0,
        pos_integration VARCHAR(50),
        accounting_integration VARCHAR(50),
        ai_analytics_enabled BOOLEAN DEFAULT 0,
        sales_prediction_enabled BOOLEAN DEFAULT 0,
        inventory_prediction_enabled BOOLEAN DEFAULT 0,
        customer_insights_enabled BOOLEAN DEFAULT 0,
        last_inventory_count DATETIME,
        last_backup DATETIME,
        updated_at DATETIME
    )
    ''')
    
    # Create roles table
    print("Creating roles table...")
    conn.execute('''
    CREATE TABLE roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(80) NOT NULL UNIQUE,
        description VARCHAR(255),
        is_system BOOLEAN DEFAULT 0
    )
    ''')
    
    # Create permissions table
    print("Creating permissions table...")
    conn.execute('''
    CREATE TABLE permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(80) NOT NULL UNIQUE,
        description VARCHAR(255),
        module VARCHAR(50)
    )
    ''')
    
    # Create user_roles table
    print("Creating user_roles table...")
    conn.execute('''
    CREATE TABLE user_roles (
        user_id INTEGER,
        role_id INTEGER,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (role_id) REFERENCES roles (id)
    )
    ''')
    
    # Create role_permissions table
    print("Creating role_permissions table...")
    conn.execute('''
    CREATE TABLE role_permissions (
        role_id INTEGER,
        permission_id INTEGER,
        PRIMARY KEY (role_id, permission_id),
        FOREIGN KEY (role_id) REFERENCES roles (id),
        FOREIGN KEY (permission_id) REFERENCES permissions (id)
    )
    ''')
    
    # Create default branch
    print("Creating default branch...")
    conn.execute('''
    INSERT INTO branches (name, is_active, is_main, address, phone, email)
    VALUES ('Main Branch', 1, 1, '123 Main St', '123-456-7890', 'branch@example.com')
    ''')
    
    # Create default roles
    print("Creating default roles...")
    conn.execute("INSERT INTO roles (name, description, is_system) VALUES ('admin', 'Administrator', 1)")
    conn.execute("INSERT INTO roles (name, description, is_system) VALUES ('cashier', 'Cashier', 1)")
    conn.execute("INSERT INTO roles (name, description, is_system) VALUES ('manager', 'Manager', 1)")
    
    # Create default permissions
    print("Creating default permissions...")
    conn.execute("INSERT INTO permissions (name, description, module) VALUES ('view_dashboard', 'View Dashboard', 'dashboard')")
    conn.execute("INSERT INTO permissions (name, description, module) VALUES ('manage_inventory', 'Manage Inventory', 'inventory')")
    conn.execute("INSERT INTO permissions (name, description, module) VALUES ('manage_users', 'Manage Users', 'users')")
    conn.execute("INSERT INTO permissions (name, description, module) VALUES ('manage_settings', 'Manage Settings', 'settings')")
    conn.execute("INSERT INTO permissions (name, description, module) VALUES ('process_sales', 'Process Sales', 'pos')")
    conn.execute("INSERT INTO permissions (name, description, module) VALUES ('view_reports', 'View Reports', 'reports')")
    
    # Assign permissions to roles
    print("Assigning permissions to roles...")
    # Admin gets all permissions
    for i in range(1, 7):
        conn.execute(f"INSERT INTO role_permissions (role_id, permission_id) VALUES (1, {i})")
    
    # Cashier gets POS and inventory permissions
    conn.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (2, 2)")  # manage_inventory
    conn.execute("INSERT INTO role_permissions (role_id, permission_id) VALUES (2, 5)")  # process_sales
    
    # Manager gets most permissions except user management
    for i in [1, 2, 4, 5, 6]:  # All except manage_users
        conn.execute(f"INSERT INTO role_permissions (role_id, permission_id) VALUES (3, {i})")
    
    # Create default admin user
    print("Creating default admin user...")
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash("admin123")
    conn.execute('''
    INSERT INTO users (
        username, password, coffee_name, branch_id, email, 
        is_active, preferred_language, theme, theme_color, is_superuser, is_system_admin
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        "admin", hashed_password, "Admin", 1, "admin@example.com", 
        1, "en", "light", "blue", 1, 1
    ))
    
    # Assign admin role to admin user
    print("Assigning admin role to admin user...")
    conn.execute("INSERT INTO user_roles (user_id, role_id) VALUES (1, 1)")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database reset successfully!")
    print("Default admin user created:")
    print("Username: admin")
    print("Password: admin123")
    
    return True

if __name__ == "__main__":
    reset_database()
