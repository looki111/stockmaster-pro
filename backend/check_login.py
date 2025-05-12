import os
import sys
from flask import Flask, url_for
from database.db_setup import db
from database.models import User, Role
from werkzeug.security import generate_password_hash, check_password_hash
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
    
    # Import and register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app

def main():
    app = create_app()
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            logger.info(f"Admin user exists: {admin.username}, ID: {admin.id}")
            # Check password hash format
            logger.info(f"Password hash: {admin.password[:20]}...")
            
            # Verify login credentials
            test_password = 'admin123'
            if check_password_hash(admin.password, test_password):
                logger.info(f"Admin password validation successful with password: {test_password}")
            else:
                logger.warning(f"Admin password validation failed with password: {test_password}")
                # Create a new admin with known password
                admin.password = generate_password_hash('admin123')
                db.session.commit()
                logger.info(f"Admin password reset to: admin123")
        else:
            logger.warning("Admin user does not exist!")
            # Create admin user
            admin_role = Role.query.filter_by(name='superuser').first()
            
            if admin_role:
                logger.info("Creating admin user...")
                admin = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    email='admin@stockmaster.com',
                    is_active=True
                )
                admin.roles.append(admin_role)
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully.")
            else:
                logger.error("Superuser role not found. Please run fix_db_relationships.py first.")
        
        # Print available URL routes
        logger.info("\nAvailable URL routes:")
        with app.test_request_context():
            try:
                login_url = url_for('auth.login')
                logger.info(f"Login URL: {login_url}")
            except Exception as e:
                logger.error(f"Error getting login URL: {e}")

if __name__ == "__main__":
    main() 