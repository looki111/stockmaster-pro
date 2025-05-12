#!/usr/bin/env python
import os
import sys
from flask import Flask
from database.db_setup import db
from database.models import User, Role, Permission, Shop, Branch
from werkzeug.security import generate_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        
    app.config.update(
        SECRET_KEY='stockmaster-secret-key',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(instance_path, "stockmaster.db")}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # Initialize database
    db.init_app(app)
    
    return app

def setup_database(app):
    """
    Set up fresh database with all tables and initial admin user
    """
    with app.app_context():
        # Drop all tables if they exist
        logger.info("Dropping all database tables...")
        db.drop_all()
        
        # Create tables
        logger.info("Creating database tables...")
        db.create_all()
        
        # Create shop and branch
        logger.info("Creating shop and branch...")
        shop = Shop(
            name="StockMaster Main",
            owner_name="Admin",
            email="admin@stockmaster.com",
            phone="123456789",
            is_active=True
        )
        db.session.add(shop)
        db.session.flush()
        
        branch = Branch(
            name="Main Branch",
            address="Main Street",
            is_active=True,
            is_main=True,
            shop_id=shop.id
        )
        db.session.add(branch)
        db.session.flush()
        
        # Create basic roles and permissions
        logger.info("Creating roles and permissions...")
        permissions = [
            Permission(name="manage_inventory", description="Can manage inventory items"),
            Permission(name="manage_sales", description="Can manage sales and orders"),
            Permission(name="manage_users", description="Can manage users"),
            Permission(name="manage_roles", description="Can manage roles and permissions"),
            Permission(name="view_reports", description="Can view reports"),
            Permission(name="manage_settings", description="Can manage system settings")
        ]
        db.session.add_all(permissions)
        db.session.flush()
        
        # Create superuser role with all permissions
        superuser_role = Role(name="superuser", description="Administrator with all permissions")
        for permission in permissions:
            superuser_role.permissions.append(permission)
        db.session.add(superuser_role)
        db.session.flush()
        
        # Create admin user with superuser role
        logger.info("Creating admin user...")
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            email="admin@stockmaster.com",
            is_active=True,
            branch_id=branch.id,
            theme="light",
            preferred_language="ar"
        )
        admin.roles.append(superuser_role)
        db.session.add(admin)
        
        # Commit all changes
        db.session.commit()
        logger.info("Database setup complete!")
        
        # Print login information
        logger.info("You can now login with:")
        logger.info("Username: admin")
        logger.info("Password: admin123")
        logger.info("URL: http://localhost:5000/auth/login")

def main():
    # Create Flask app
    app = create_app()
    
    # Set up database
    setup_database(app)
    
    logger.info("Database initialization complete. You can now run the application.")

if __name__ == "__main__":
    main()
