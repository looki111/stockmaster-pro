"""
Set up Flask-Migrate for database migrations
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade

def setup_migrations():
    """Set up Flask-Migrate for database migrations"""
    print("Setting up Flask-Migrate for database migrations...")

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

    # Check if migrations directory exists
    with app.app_context():
        versions_dir = os.path.join(migrate_dir, 'versions')
        if not os.path.exists(versions_dir):
            print("Initializing migrations directory...")
            init(migrate_dir)
            print("Migrations directory initialized.")
        else:
            print(f"Migrations directory already exists at {migrate_dir}")
            print("Checking if it's properly configured...")

            # Check if alembic.ini exists
            if not os.path.exists(os.path.join(migrate_dir, 'alembic.ini')):
                print("alembic.ini not found. Reinitializing migrations directory...")
                # Backup the existing versions directory
                import shutil
                backup_dir = os.path.join(migrate_dir, 'versions_backup')
                if os.path.exists(versions_dir):
                    shutil.move(versions_dir, backup_dir)
                # Initialize the migrations directory
                init(migrate_dir)
                # Restore the versions directory
                if os.path.exists(backup_dir):
                    if os.path.exists(versions_dir):
                        shutil.rmtree(versions_dir)
                    shutil.move(backup_dir, versions_dir)
                print("Migrations directory reinitialized.")

        # Create a migration for any pending changes
        print("Creating migration for pending changes...")
        try:
            migrate(migrate_dir, message="Update schema")
            print("Migration created.")

            # Apply the migration
            print("Applying migration...")
            upgrade(migrate_dir)
            print("Migration applied.")
        except Exception as e:
            print(f"Error during migration: {e}")
            print("You may need to manually review and fix the migration files.")

    print("Flask-Migrate setup completed successfully!")
    print("\nNow you can use the following commands for future schema changes:")
    print("  flask db migrate -m \"your message\"  # Create a migration")
    print("  flask db upgrade                    # Apply the migration")

    return True

if __name__ == "__main__":
    setup_migrations()
