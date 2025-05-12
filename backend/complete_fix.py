#!/usr/bin/env python
"""
Complete Fix for StockMaster Pro
This script fixes all database issues, recreates the database properly,
and sets up initial data to ensure the application works correctly.
"""

import os
import sys
from flask import Flask, current_app
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_project_root():
    """Returns the project root directory"""
    return os.path.dirname(os.path.abspath(__file__))

def create_app():
    """Create a Flask application instance"""
    app = Flask(__name__)
    
    # Configuration
    instance_path = os.path.join(get_project_root(), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Database configuration
    app.config.update(
        SECRET_KEY='stockmaster-secret-key',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(instance_path, "stockmaster.db")}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # Initialize extensions
    from database.db_setup import db, init_db
    db.init_app(app)
    
    # Initialize login manager
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from database.models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    with app.app_context():
        # Import blueprints
        from routes.auth import auth_bp
        
        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app

def setup_database(app):
    """Set up the database with initial data"""
    from database.db_setup import db
    from database.models import User, Role, Permission, Shop, Branch
    from werkzeug.security import generate_password_hash
    import roles
    
    with app.app_context():
        # Drop and recreate all tables
        logger.info("Dropping all database tables...")
        db.drop_all()
        
        logger.info("Creating all database tables...")
        db.create_all()
        
        # Create default shop
        logger.info("Creating default shop...")
        shop = Shop(
            name="StockMaster Coffee",
            owner_name="Admin User",
            email="admin@example.com",
            phone="123456789",
            is_active=True
        )
        db.session.add(shop)
        db.session.flush()  # Get the shop ID
        
        # Create main branch
        logger.info("Creating main branch...")
        branch = Branch(
            name="Main Branch",
            is_main=True,
            is_active=True,
            shop_id=shop.id
        )
        db.session.add(branch)
        db.session.flush()  # Get the branch ID
        
        # Initialize roles and permissions
        logger.info("Initializing roles and permissions...")
        try:
            roles.init_roles_and_permissions(current_app)
        except Exception as e:
            logger.error(f"Error initializing roles and permissions: {e}")
            # Create minimal permissions and roles
            create_minimal_roles_and_permissions()
        
        # Create admin user
        logger.info("Creating admin user...")
        admin_role = Role.query.filter_by(name="admin").first()
        
        if not admin_role:
            logger.warning("Admin role not found, creating it...")
            admin_role = Role(name="admin", description="System Administrator")
            db.session.add(admin_role)
            db.session.flush()
        
        admin_user = User(
            username="admin",
            password=generate_password_hash("admin123"),
            email="admin@stockmaster.com",
            is_active=True,
            branch_id=branch.id
        )
        
        # Assign admin role to user
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        
        # Commit changes
        logger.info("Committing database changes...")
        try:
            db.session.commit()
            logger.info("Database setup completed successfully!")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error committing database changes: {e}")
            raise

def create_minimal_roles_and_permissions():
    """Create minimal roles and permissions if the full initialization fails"""
    from database.db_setup import db
    from database.models import Role, Permission
    
    # Create basic permissions
    permissions = [
        {"name": "dashboard_access", "description": "Access the dashboard", "module": "dashboard"},
        {"name": "inventory_view", "description": "View inventory", "module": "inventory"},
        {"name": "inventory_edit", "description": "Edit inventory", "module": "inventory"},
        {"name": "pos_access", "description": "Access the POS system", "module": "pos"},
        {"name": "reports_view", "description": "View reports", "module": "reports"},
        {"name": "users_manage", "description": "Manage users", "module": "users"},
    ]
    
    # Add permissions to the database
    for perm_data in permissions:
        permission = Permission(**perm_data)
        db.session.add(permission)
    
    # Create roles
    admin_role = Role(name="admin", description="System Administrator", is_system=True)
    cashier_role = Role(name="cashier", description="Cashier", is_system=True)
    
    db.session.add(admin_role)
    db.session.add(cashier_role)
    db.session.flush()
    
    # Assign all permissions to admin role
    for permission in Permission.query.all():
        admin_role.permissions.append(permission)
    
    # Assign limited permissions to cashier role
    for perm_name in ["dashboard_access", "pos_access"]:
        permission = Permission.query.filter_by(name=perm_name).first()
        if permission:
            cashier_role.permissions.append(permission)

def add_root_route(app):
    """Add a root route to redirect to the login page"""
    from flask import redirect, url_for
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

def main():
    """Main function to run the script"""
    logger.info("Starting complete fix for StockMaster Pro...")
    
    try:
        # Create Flask app
        logger.info("Creating Flask application...")
        app = create_app()
        
        # Add root route
        logger.info("Adding root route...")
        add_root_route(app)
        
        # Set up database
        logger.info("Setting up database...")
        setup_database(app)
        
        logger.info("Fix complete! You can now run the application.")
        logger.info("Login with username: admin, password: admin123")
        
        # Run the app for testing (comment out for production)
        print("Running the application for testing...")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"Error during fix: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 