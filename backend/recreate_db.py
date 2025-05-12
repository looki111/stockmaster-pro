"""
Recreate the database from scratch
"""

import os
import sys
import shutil
from werkzeug.security import generate_password_hash

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def recreate_database():
    """Recreate the database from scratch"""
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

    # Import the database setup and models
    from flask import Flask
    from database.db_setup import db, init_db
    from database.models import User, Branch, Role, Permission, user_roles, role_permissions

    # Create a Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    print("Initializing database...")
    init_db(app)

    # Use app context for all database operations
    with app.app_context():
        # Create a default branch
        print("Creating default branch...")
        branch = Branch(
            name="Main Branch",
            is_active=True,
            is_main=True,
            address="123 Main St",
            phone="123-456-7890",
            email="branch@example.com"
        )
        db.session.add(branch)
        db.session.commit()

        # Create default roles
        print("Creating default roles...")
        admin_role = Role(
            name="admin",
            description="Administrator",
            is_system=True
        )
        cashier_role = Role(
            name="cashier",
            description="Cashier",
            is_system=True
        )
        manager_role = Role(
            name="manager",
            description="Manager",
            is_system=True
        )
        db.session.add_all([admin_role, cashier_role, manager_role])
        db.session.commit()

        # Create default permissions
        print("Creating default permissions...")
        permissions = [
            Permission(name="view_dashboard", description="View Dashboard", module="dashboard"),
            Permission(name="manage_inventory", description="Manage Inventory", module="inventory"),
            Permission(name="manage_users", description="Manage Users", module="users"),
            Permission(name="manage_settings", description="Manage Settings", module="settings"),
            Permission(name="process_sales", description="Process Sales", module="pos"),
            Permission(name="view_reports", description="View Reports", module="reports")
        ]
        db.session.add_all(permissions)
        db.session.commit()

        # Assign permissions to roles
        print("Assigning permissions to roles...")
        # Admin gets all permissions
        for permission in permissions:
            admin_role.permissions.append(permission)

        # Cashier gets POS and inventory permissions
        for permission in permissions:
            if permission.module in ["pos", "inventory"]:
                cashier_role.permissions.append(permission)

        # Manager gets most permissions except user management
        for permission in permissions:
            if permission.module != "users":
                manager_role.permissions.append(permission)

        db.session.commit()

        # Create default admin user
        print("Creating default admin user...")
        admin_user = User(
            username="admin",
            password=generate_password_hash("admin123"),
            coffee_name="Admin",
            branch_id=branch.id,
            email="admin@example.com",
            is_active=True,
            preferred_language="en",
            theme="light",
            theme_color="blue",
            is_superuser=True,
            is_system_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()

        # Assign admin role to admin user
        print("Assigning admin role to admin user...")
        admin_user.roles.append(admin_role)
        db.session.commit()

    print("Database recreated successfully!")
    print("Default admin user created:")
    print("Username: admin")
    print("Password: admin123")

    return True

if __name__ == "__main__":
    recreate_database()
