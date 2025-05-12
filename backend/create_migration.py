"""
Create a new migration to ensure all fields in the User model are properly reflected in the database
"""

import os
from flask import Flask
from flask_migrate import Migrate, migrate

def create_migration():
    """Create a new migration"""
    print("Creating a new migration...")
    
    # Create a Flask app
    app = Flask(__name__)
    
    # Configure the app
    app.config.update(
        SECRET_KEY='your-secret-key-here',
        SQLALCHEMY_DATABASE_URI='sqlite:///instance/stockmaster.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize SQLAlchemy
    from database.db_setup import db
    db.init_app(app)
    
    # Import all models to ensure they're registered with SQLAlchemy
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
    
    # Initialize Flask-Migrate
    migrate_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    migrate = Migrate(app, db)
    
    # Create a new migration
    with app.app_context():
        print("Creating migration...")
        try:
            migrate(migrate_dir, message="ensure_all_user_fields")
            print("Migration created successfully!")
            return True
        except Exception as e:
            print(f"Error creating migration: {e}")
            print("You may need to manually review and fix the migration files.")
            return False

if __name__ == "__main__":
    create_migration()
