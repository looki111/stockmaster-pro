import os
import sys
from flask import Flask
from database.db_setup import db
from database.models import User, Role, Permission, Shop, Branch
from werkzeug.security import generate_password_hash
import roles
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockmaster.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'stockmaster-secret-key'
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app

def setup_database(app):
    """Set up the database with all required tables and initial data"""
    with app.app_context():
        # Drop all tables and recreate
        logger.info("Dropping all database tables...")
        db.drop_all()
        
        # Create tables
        logger.info("Creating all database tables...")
        db.create_all()
        
        # Check if shop exists, create if not
        shop = Shop.query.first()
        if not shop:
            logger.info("Creating default shop...")
            shop = Shop(
                name="Main Shop", 
                is_active=True
            )
            db.session.add(shop)
            db.session.flush()
        
        # Check if branch exists, create if not
        branch = Branch.query.first()
        if not branch:
            logger.info("Creating default branch...")
            branch = Branch(
                name="Main Branch", 
                is_active=True, 
                is_main=True,
                shop_id=shop.id
            )
            db.session.add(branch)
            db.session.commit()
        
        # Set up roles and permissions
        logger.info("Setting up roles and permissions...")
        try:
            roles.init_roles_and_permissions(app)
            logger.info("Roles and permissions initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing roles and permissions: {e}")
            db.session.rollback()
        
        # Check if admin user exists, create if not
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            logger.info("Creating admin user...")
            admin_role = Role.query.filter_by(name='superuser').first()
            
            if admin_role:
                admin = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    email='admin@stockmaster.com',
                    is_active=True,
                    branch_id=branch.id,
                    preferred_language='ar',
                    theme='light'
                )
                admin.roles.append(admin_role)
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully.")
                logger.info("Username: admin")
                logger.info("Password: admin123")
            else:
                logger.error("Failed to create admin: superuser role not found.")
        else:
            logger.info(f"Admin user already exists: {admin.username}")
            # Update admin password for security
            admin.password = generate_password_hash('admin123')
            # Ensure admin has branch and roles
            if not admin.branch_id and branch:
                admin.branch_id = branch.id
            
            # Check if admin has superuser role
            admin_role = Role.query.filter_by(name='superuser').first()
            if admin_role and admin_role not in admin.roles:
                admin.roles.append(admin_role)
                
            db.session.commit()
            logger.info("Admin user updated.")
            logger.info("Username: admin")
            logger.info("Password: admin123")
        
        logger.info("Database setup completed.")
        logger.info("Login at /auth/login with username 'admin' and password 'admin123'")

def main():
    """Main function to run the setup"""
    app = create_app()
    setup_database(app)
    
    logger.info("\nAll fixes applied. Database should be ready for use.")
    logger.info("The application can now be started with: python app.py")

if __name__ == "__main__":
    main() 