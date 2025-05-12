"""
Test all fixes for StockMaster Pro
"""

import os
import sys
from flask import Flask, url_for
from werkzeug.routing import BuildError
from flask_login import current_user

def test_fixes():
    """Test all fixes"""
    print("Starting tests for StockMaster Pro fixes...")

    # Create a Flask app
    app = Flask(__name__)

    # Configure the app
    # Make sure the instance directory exists
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    # Use absolute path for database
    db_path = os.path.join(os.path.abspath(instance_path), 'stockmaster.db')
    print(f"Database path: {db_path}")

    app.config.update(
        SECRET_KEY='your-secret-key-here',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=True
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

    # Import blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.clients import clients_bp
    from routes.promotions import promotions_bp
    from routes.subscription import subscription_bp
    from routes.pos import pos_bp
    from routes.inventory import inventory_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(promotions_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(pos_bp)
    app.register_blueprint(inventory_bp)

    with app.app_context():
        # Test 1: Check database columns
        print("\n--- Test 1: Check database columns ---")
        try:
            # Get all columns from the User model
            user_columns = [column.name for column in User.__table__.columns]
            print(f"User model columns: {', '.join(user_columns)}")

            # Check if theme_color is in the model
            if 'theme_color' in user_columns:
                print("✅ theme_color is in the User model.")
            else:
                print("❌ ERROR: theme_color is not in the User model!")

            # Check if created_at is in the model
            if 'created_at' in user_columns:
                print("✅ created_at is in the User model.")
            else:
                print("❌ ERROR: created_at is not in the User model!")
        except Exception as e:
            print(f"❌ Error checking database columns: {e}")

        # Test 2: Check routes
        print("\n--- Test 2: Check routes ---")
        try:
            # Test dashboard route
            dashboard_url = url_for('dashboard.dashboard')
            print(f"✅ dashboard.dashboard route exists: {dashboard_url}")

            # Test sales route
            sales_url = url_for('dashboard.sales')
            print(f"✅ dashboard.sales route exists: {sales_url}")

            # Test settings route
            settings_url = url_for('dashboard.settings')
            print(f"✅ dashboard.settings route exists: {settings_url}")

            # Test login route
            login_url = url_for('auth.login')
            print(f"✅ auth.login route exists: {login_url}")

            # Test logout route
            logout_url = url_for('auth.logout')
            print(f"✅ auth.logout route exists: {logout_url}")

            # Test inventory routes
            raw_materials_url = url_for('inventory.raw_materials')
            print(f"✅ inventory.raw_materials route exists: {raw_materials_url}")

            recipes_url = url_for('inventory.recipes')
            print(f"✅ inventory.recipes route exists: {recipes_url}")

            reports_url = url_for('inventory.reports')
            print(f"✅ inventory.reports route exists: {reports_url}")

            # Test client routes
            clients_url = url_for('clients.clients_list')
            print(f"✅ clients.clients_list route exists: {clients_url}")

            # Test promotions route
            promotions_url = url_for('promotions.promotions')
            print(f"✅ promotions.promotions route exists: {promotions_url}")

            # Test POS route
            pos_url = url_for('pos.index')
            print(f"✅ pos.index route exists: {pos_url}")

        except BuildError as e:
            print(f"❌ Route error: {e}")
        except Exception as e:
            print(f"❌ Error checking routes: {e}")

        print("\nAll tests completed.")

if __name__ == "__main__":
    test_fixes()
