"""
Reset database and create admin user for StockMaster Pro
This script will:
1. Delete the existing database
2. Create a new database with all tables
3. Create a default admin user
4. Create a default branch
"""

import os
import sys
import sqlite3
from flask import Flask
from werkzeug.security import generate_password_hash
from datetime import datetime

def reset_database():
    """Reset database and create admin user"""
    print("\n=== StockMaster Pro Database Reset ===\n")
    
    # Create a Flask app
    app = Flask(__name__)
    
    # Configure the app
    # Make sure the instance directory exists
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance directory: {instance_path}")
        
    # Use absolute path for database
    db_path = os.path.join(os.path.abspath(instance_path), 'stockmaster.db')
    print(f"Database path: {db_path}")
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        print(f"Removing existing database: {db_path}")
        try:
            os.remove(db_path)
            print("Existing database removed successfully.")
        except Exception as e:
            print(f"Error removing database: {e}")
            print("Trying to continue anyway...")
    
    # Configure Flask app
    app.config.update(
        SECRET_KEY='stockmaster-secret-key',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize SQLAlchemy
    try:
        from database.db_setup import db
        db.init_app(app)
        print("SQLAlchemy initialized successfully.")
    except Exception as e:
        print(f"Error initializing SQLAlchemy: {e}")
        return False
    
    # Import all models to ensure they're registered with SQLAlchemy
    try:
        from database.models import (
            User, Branch, Role, Permission, user_roles, role_permissions
        )
        print("Models imported successfully.")
    except Exception as e:
        print(f"Error importing models: {e}")
        return False
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("Database tables created successfully!")
            
            # Create default branch
            branch = Branch(
                name="Main Branch",
                address="Main Address",
                phone="1234567890",
                is_active=True,
                is_main=True
            )
            db.session.add(branch)
            db.session.commit()
            print(f"Default branch created with ID: {branch.id}")
            
            # Create admin role
            admin_role = Role(
                name="admin",
                description="Administrator with full access",
                is_system=True,
                created_at=datetime.utcnow()
            )
            db.session.add(admin_role)
            db.session.commit()
            print(f"Admin role created with ID: {admin_role.id}")
            
            # Create admin user
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
                is_system_admin=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f"Admin user created with ID: {admin_user.id}")
            
            # Verify the admin user was created correctly
            verify_user = User.query.filter_by(username="admin").first()
            if verify_user:
                print(f"Verified admin user exists with ID: {verify_user.id}")
            else:
                print("ERROR: Admin user was not created correctly!")
                
            # Print admin credentials for reference
            print("\n=== Admin Credentials ===")
            print("Username: admin")
            print("Password: admin123")
            print("=========================\n")
            
            print("Database reset completed successfully!")
            return True
        except Exception as e:
            print(f"Error resetting database: {e}")
            return False

def verify_login():
    """Verify that login works with the admin credentials"""
    print("\n=== Verifying Login Functionality ===\n")
    
    # Create a Flask app
    app = Flask(__name__)
    
    # Configure the app
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    db_path = os.path.join(os.path.abspath(instance_path), 'stockmaster.db')
    
    app.config.update(
        SECRET_KEY='stockmaster-secret-key',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize SQLAlchemy
    from database.db_setup import db
    db.init_app(app)
    
    # Import User model
    from database.models import User
    from werkzeug.security import check_password_hash
    
    with app.app_context():
        try:
            # Try to find the admin user
            admin = User.query.filter_by(username="admin").first()
            
            if not admin:
                print("ERROR: Admin user not found in database!")
                return False
                
            # Verify password
            if check_password_hash(admin.password, "admin123"):
                print("Password verification successful!")
            else:
                print("ERROR: Password verification failed!")
                return False
                
            print("Login verification completed successfully!")
            return True
        except Exception as e:
            print(f"Error verifying login: {e}")
            return False

if __name__ == "__main__":
    success = reset_database()
    
    if success:
        verify_login()
        
        print("\n=== Next Steps ===")
        print("1. Start the application: python app.py")
        print("2. Log in with username 'admin' and password 'admin123'")
        print("3. If login fails, check the application logs for errors")
    else:
        print("\nDatabase reset failed. Please check the error messages above.")
