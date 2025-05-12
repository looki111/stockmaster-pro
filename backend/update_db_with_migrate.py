"""
Update database schema using Flask-Migrate
"""

import os
import sys
from flask import Flask
from flask_migrate import Migrate, upgrade, init
from flask_migrate import migrate as migrate_command

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_db_schema():
    """Update database schema using Flask-Migrate"""
    from database.db_setup import db, init_db

    # Create a Flask app
    app = Flask(__name__)

    # Make sure the instance directory exists
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    # Configure the app
    app.config.update(
        SECRET_KEY='your-secret-key-here',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(instance_path, "stockmaster.db")}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # Initialize database
    init_db(app)

    # Import all models to ensure they are registered with SQLAlchemy
    from database.models import (
        User, Product, Sale, RawMaterial, Recipe, Order, OrderItem, Notification,
        Branch, Client, Vendor, ActivityLog, Promotion, Permission, Role
    )
    from database.inventory_models import (
        InventoryTransaction, StockCount, StockCountItem, ConsumptionRule,
        InventoryAdjustment, InventoryAdjustmentItem, DailyStockReport, DailyStockReportItem
    )
    from database.subscription_models import (
        Shop, SubscriptionPlan, Subscription, SubscriptionPayment, SubscriptionInvoice
    )

    # Initialize Flask-Migrate
    migrate_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    migrate = Migrate(app, db)

    # Check if migrations directory exists
    if not os.path.exists(migrate_dir):
        print("Initializing migrations directory...")
        with app.app_context():
            init(migrate_dir)

    # Create a migration
    print("Creating migration...")
    with app.app_context():
        migrate_command(message="Update database schema")

    # Apply migration
    print("Applying migration...")
    with app.app_context():
        upgrade()

    print("Database schema updated successfully!")
    return True

if __name__ == "__main__":
    update_db_schema()
