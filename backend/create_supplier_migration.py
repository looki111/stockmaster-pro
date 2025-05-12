"""
Migration script for adding supplier models to the database
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, init, migrate, upgrade
import os

def create_supplier_migration():
    """Create a migration for supplier models"""
    print("Creating migration for supplier models...")
    
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
    
    # Import inventory models
    from database.inventory_models import (
        InventoryTransaction, StockCount, StockCountItem, ConsumptionRule,
        InventoryAdjustment, InventoryAdjustmentItem, DailyStockReport, DailyStockReportItem
    )
    
    # Import supplier models
    from database.supplier_models import (
        Supplier, SupplierOrder, SupplierOrderItem
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
        
        # Create a migration for supplier models
        print("Creating migration for supplier models...")
        try:
            migrate(migrate_dir, message="Add supplier models")
            print("Migration created.")
            
            # Apply the migration
            print("Applying migration...")
            upgrade(migrate_dir)
            print("Migration applied.")
            return True
        except Exception as e:
            print(f"Error during migration: {e}")
            print("You may need to manually review and fix the migration files.")
            return False

if __name__ == "__main__":
    create_supplier_migration()
