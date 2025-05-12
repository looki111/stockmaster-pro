"""
Initialize the database with all required tables
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

def initialize_database():
    """Initialize the database with all required tables"""
    print("Starting database initialization...")
    
    # Create a Flask app
    app = Flask(__name__)
    
    # Configure the app
    app.config.update(
        SECRET_KEY='your-secret-key-here',
        SQLALCHEMY_DATABASE_URI='sqlite:///stockmaster.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize SQLAlchemy
    from database.db_setup import db
    db.init_app(app)
    
    # Import all models
    from database.models import (
        User, Product, Sale, RawMaterial, Recipe, Order, OrderItem,
        Notification, Branch, Client, Vendor, ActivityLog, Promotion,
        Shift, SupportTicket, TicketResponse, KnowledgeBase, AIPrediction,
        Permission, Role
    )
    
    # Import subscription models
    from database.subscription_models import (
        Shop, SubscriptionPlan, Subscription, SubscriptionPayment, SubscriptionInvoice
    )
    
    # Create all tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
            
            # Create default branch
            branch = Branch(
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
            db.session.add(branch)
            db.session.commit()
            print("Default branch created successfully!")
            
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
                is_system_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
            
            # Create roles
            admin_role = Role(name="Admin", description="Administrator with full access")
            manager_role = Role(name="Manager", description="Manager with limited access")
            cashier_role = Role(name="Cashier", description="Cashier with POS access")
            
            # Add roles to the database
            db.session.add_all([admin_role, manager_role, cashier_role])
            db.session.commit()
            print("Roles created successfully!")
            
            # Assign admin role to admin user
            admin_user.roles.append(admin_role)
            db.session.commit()
            print("Admin role assigned to admin user!")
            
            return True
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False

if __name__ == "__main__":
    if initialize_database():
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")
