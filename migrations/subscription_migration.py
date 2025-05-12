"""
Migration script for adding subscription models to the database
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a minimal Flask app for migration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///stockmaster.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models
from backend.database.subscription_models import (
    Shop, SubscriptionPlan, Subscription, SubscriptionPayment, SubscriptionInvoice
)
from backend.database.models import (
    User, Branch, Product, Sale, RawMaterial, Recipe, Order, OrderItem, 
    Notification, Client, Vendor, ActivityLog, Promotion,
    Shift, SupportTicket, TicketResponse, KnowledgeBase, AIPrediction,
    Permission, Role
)

def create_default_subscription_plans():
    """Create default subscription plans if they don't exist"""
    # Check if plans already exist
    if SubscriptionPlan.query.first():
        print("Subscription plans already exist. Skipping creation.")
        return
    
    # Create basic plan
    basic_plan = SubscriptionPlan(
        name="Basic",
        description="Perfect for small coffee shops with a single location",
        price_monthly=99.0,
        price_yearly=999.0,
        features={
            'max_branches': 1,
            'max_users': 5,
            'max_products': 100,
            'pos': True,
            'inventory': True,
            'reports': True,
            'marketing': False,
            'ai': False,
            'api': False,
        },
        max_branches=1,
        max_users=5,
        max_products=100,
        is_active=True
    )
    
    # Create standard plan
    standard_plan = SubscriptionPlan(
        name="Standard",
        description="Ideal for growing coffee shops with multiple staff members",
        price_monthly=199.0,
        price_yearly=1999.0,
        features={
            'max_branches': 3,
            'max_users': 15,
            'max_products': 500,
            'pos': True,
            'inventory': True,
            'reports': True,
            'marketing': True,
            'ai': False,
            'api': False,
        },
        max_branches=3,
        max_users=15,
        max_products=500,
        is_active=True
    )
    
    # Create premium plan
    premium_plan = SubscriptionPlan(
        name="Premium",
        description="Complete solution for established coffee shop chains",
        price_monthly=399.0,
        price_yearly=3999.0,
        features={
            'max_branches': 10,
            'max_users': 50,
            'max_products': 2000,
            'pos': True,
            'inventory': True,
            'reports': True,
            'marketing': True,
            'ai': True,
            'api': True,
        },
        max_branches=10,
        max_users=50,
        max_products=2000,
        is_active=True
    )
    
    # Add plans to database
    db.session.add(basic_plan)
    db.session.add(standard_plan)
    db.session.add(premium_plan)
    db.session.commit()
    
    print("Created default subscription plans")

def migrate_existing_data():
    """Migrate existing data to the new subscription model"""
    # Check if any shops exist
    if Shop.query.first():
        print("Shops already exist. Skipping migration.")
        return
    
    # Get default subscription plan
    default_plan = SubscriptionPlan.query.filter_by(name="Standard").first()
    if not default_plan:
        print("No default plan found. Please run create_default_subscription_plans first.")
        return
    
    # Get all branches
    branches = Branch.query.all()
    
    # Group branches by name (assuming branches with the same name belong to the same shop)
    shops_by_name = {}
    for branch in branches:
        if branch.name not in shops_by_name:
            shops_by_name[branch.name] = []
        shops_by_name[branch.name].append(branch)
    
    # Create shops and link branches
    for shop_name, shop_branches in shops_by_name.items():
        # Get a sample user from the first branch to use for shop info
        sample_user = User.query.filter_by(branch_id=shop_branches[0].id).first()
        
        # Create shop
        shop = Shop(
            name=shop_name,
            owner_name=sample_user.username if sample_user else "Owner",
            email=sample_user.email if sample_user else f"{shop_name.lower().replace(' ', '')}@example.com",
            is_active=True
        )
        
        db.session.add(shop)
        db.session.flush()  # Get shop ID without committing
        
        # Create subscription
        subscription = Subscription(
            shop_id=shop.id,
            plan_id=default_plan.id,
            start_date=db.func.now(),
            end_date=db.func.date_add(db.func.now(), db.text("INTERVAL 1 YEAR")),
            billing_cycle='yearly',
            auto_renew=True,
            is_active=True,
            payment_status='paid'
        )
        
        db.session.add(subscription)
        
        # Link branches to shop
        for branch in shop_branches:
            branch.shop_id = shop.id
    
    db.session.commit()
    print(f"Migrated {len(shops_by_name)} shops and {len(branches)} branches")

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create default subscription plans
        create_default_subscription_plans()
        
        # Migrate existing data
        migrate_existing_data()
        
        print("Migration completed successfully")
