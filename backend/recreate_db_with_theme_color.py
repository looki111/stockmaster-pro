"""
Recreate the database with the theme_color column in the users table
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Create a Flask app
app = Flask(__name__)

# Configure the app
app.config.update(
    SECRET_KEY='your-secret-key-here',
    SQLALCHEMY_DATABASE_URI='sqlite:///stockmaster.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Import the database setup
from database.db_setup import db as existing_db
existing_db.init_app(app)

# Import all models
from database.models import User, Branch, Role, Permission
from database.subscription_models import Shop, SubscriptionPlan, Subscription

# Initialize the database with the app context
with app.app_context():
    try:
        # Drop all tables and recreate them
        db.drop_all()
        print("All tables dropped successfully")
        db.create_all()
        print("All tables recreated successfully")

        # Create default branch
        default_branch = Branch(
            name="الفرع الرئيسي",
            address="العنوان الرئيسي",
            phone="1234567890",
            is_active=True,
            weight_unit='kg',
            currency='SAR',
            time_format='24',
            invoice_template='default',
            is_main=True
        )
        db.session.add(default_branch)
        db.session.commit()
        print("Default branch created successfully")

        # Create admin user
        admin_user = User(
            username="admin",
            password=generate_password_hash("admin123"),
            coffee_name="Admin",
            branch_id=default_branch.id,
            email="admin@example.com",
            is_active=True,
            preferred_language="en",
            theme="light",
            theme_color="blue",  # Make sure this field is set
            is_superuser=True,
            is_system_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully")

        # Create roles and permissions
        admin_role = Role(name="Admin", description="Administrator with full access")
        manager_role = Role(name="Manager", description="Manager with limited access")
        cashier_role = Role(name="Cashier", description="Cashier with POS access")

        # Add roles to the database
        db.session.add_all([admin_role, manager_role, cashier_role])
        db.session.commit()
        print("Roles created successfully")

        # Assign admin role to admin user
        admin_user.roles.append(admin_role)
        db.session.commit()
        print("Admin role assigned to admin user")

        print("Database recreated successfully with theme_color column!")

    except Exception as e:
        print(f"Error recreating database: {e}")
        sys.exit(1)
