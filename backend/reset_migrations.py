"""
Reset and properly set up Flask-Migrate for database migrations
"""

import os
import sys
import shutil
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade

def reset_migrations():
    """Reset and properly set up Flask-Migrate for database migrations"""
    print("Resetting and setting up Flask-Migrate for database migrations...")
    
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
    migrate_instance = Migrate(app, db)
    
    # Backup the existing migrations directory if it exists
    if os.path.exists(migrate_dir):
        backup_dir = os.path.join(os.path.dirname(__file__), 'migrations_backup')
        print(f"Backing up existing migrations directory to {backup_dir}...")
        
        # Remove old backup if it exists
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        
        # Create backup
        shutil.copytree(migrate_dir, backup_dir)
        
        # Remove existing migrations directory
        shutil.rmtree(migrate_dir)
        print("Existing migrations directory removed.")
    
    # Initialize migrations directory
    with app.app_context():
        print("Initializing new migrations directory...")
        init(migrate_dir)
        print("Migrations directory initialized.")
        
        # Create an initial migration
        print("Creating initial migration...")
        try:
            migrate(migrate_dir, message="Initial migration")
            print("Initial migration created.")
            
            # Apply the migration
            print("Applying migration...")
            upgrade(migrate_dir)
            print("Migration applied.")
        except Exception as e:
            print(f"Error during migration: {e}")
            print("You may need to manually review and fix the migration files.")
    
    print("Flask-Migrate reset and setup completed successfully!")
    print("\nNow you can use the following commands for future schema changes:")
    print("  flask db migrate -m \"your message\"  # Create a migration")
    print("  flask db upgrade                    # Apply the migration")
    
    return True

if __name__ == "__main__":
    reset_migrations()
