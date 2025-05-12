from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create a single SQLAlchemy instance for the entire application
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app"""
    # Initialize the SQLAlchemy extension
    db.init_app(app)

    # Import models inside the function to avoid circular imports
    # and to ensure models are registered with this SQLAlchemy instance
    with app.app_context():
        # Import all models here
        # These imports are to ensure all models are registered with the SQLAlchemy instance
        from .models import User, Product, Sale, RawMaterial, Recipe, Order, OrderItem, Notification
        from .models import Branch, Client, Vendor, ActivityLog, Promotion, Shift, SupportTicket
        from .models import TicketResponse, KnowledgeBase, AIPrediction, Permission, Role, Shop

        # Import inventory models
        try:
            from .inventory_models import InventoryTransaction, StockCount, StockCountItem
            from .inventory_models import ConsumptionRule, InventoryAdjustment, InventoryAdjustmentItem
            from .inventory_models import DailyStockReport, DailyStockReportItem
        except ImportError:
            app.logger.warning("Could not import inventory_models")

        # Import subscription models
        try:
            # Import without recreating the Shop model which is already in models.py
            from .subscription_models import SubscriptionPlan, Subscription
            from .subscription_models import SubscriptionPayment, SubscriptionInvoice
        except ImportError:
            app.logger.warning("Could not import subscription_models")

        # Import supplier models
        try:
            from .supplier_models import Supplier, SupplierOrder, SupplierOrderItem
        except ImportError:
            app.logger.warning("Could not import supplier_models")

        # Create tables if they don't exist
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            raise
