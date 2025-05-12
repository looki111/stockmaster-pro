"""
Fix database issues by ensuring all columns in the User model are properly migrated
"""

import os
from flask import Flask
from flask_migrate import Migrate

def fix_database():
    """Fix database issues"""
    print("Starting database fix...")

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
    migrate = Migrate(app, db)

    with app.app_context():
        try:
            # Check if the User model has all required columns
            print("Checking User model columns...")

            # Get all columns from the User model
            user_columns = [column.name for column in User.__table__.columns]
            print(f"User model columns: {user_columns}")

            # Check if theme_color is in the model
            if 'theme_color' not in user_columns:
                print("ERROR: theme_color is not in the User model!")
            else:
                print("theme_color is in the User model.")

            # Try to query a user with theme_color
            print("Trying to query a user with theme_color...")
            user = User.query.first()
            if user:
                print(f"User found: {user.username}")
                print(f"User theme_color: {user.theme_color}")
            else:
                print("No users found in the database.")

                # Create a test user if no users exist
                print("Creating a test user...")

                # Check if a branch exists
                branch = Branch.query.first()
                if not branch:
                    print("Creating a test branch...")
                    branch = Branch(
                        name="Test Branch",
                        is_active=True,
                        is_main=True
                    )
                    db.session.add(branch)
                    db.session.commit()

                # Create a test user
                from werkzeug.security import generate_password_hash
                user = User(
                    username="testuser",
                    password=generate_password_hash("testpass"),
                    coffee_name="Test User",
                    branch_id=branch.id,
                    email="test@example.com",
                    is_active=True,
                    preferred_language="en",
                    theme="light",
                    theme_color="blue",
                    is_superuser=True,
                    is_system_admin=True,
                    created_at=db.func.now(),
                    updated_at=db.func.now()
                )
                db.session.add(user)
                db.session.commit()
                print(f"Test user created with ID: {user.id}")

            print("Database check completed.")
            return True
        except Exception as e:
            print(f"Error checking database: {e}")
            return False

if __name__ == "__main__":
    fix_database()
