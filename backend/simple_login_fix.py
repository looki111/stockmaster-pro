#!/usr/bin/env python
"""
Simple Login Fix for StockMaster Pro
This script focuses only on ensuring the login functionality works properly.
"""

import os
import sys
from flask import Flask, redirect, url_for
from werkzeug.security import generate_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create a simple Flask application with only auth functionality"""
    app = Flask(__name__)
    
    # Configuration
    app.config.update(
        SECRET_KEY='stockmaster-secret-key',
        SQLALCHEMY_DATABASE_URI='sqlite:///stockmaster.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # Initialize database
    from database.db_setup import db
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
    
    # Register only the auth blueprint
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Add root route to redirect to login
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # Add route to see available endpoints (for debugging)
    @app.route('/debug/routes')
    def list_routes():
        output = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            line = f"{rule.endpoint:30s} {methods:20s} {rule}"
            output.append(line)
        
        return "<pre>" + "\n".join(sorted(output)) + "</pre>"
    
    return app

def ensure_login_template_is_correct(app):
    """Ensure login templates point to the correct URL"""
    from flask import render_template_string
    
    with app.app_context():
        try:
            # Check login form in login_enhanced.html
            with open('templates/login_enhanced.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ensure form action is correct
            if 'action="/auth/login"' not in content:
                logger.info("Fixing login form action in login_enhanced.html")
                content = content.replace('action="/login"', 'action="/auth/login"')
                content = content.replace('action="login"', 'action="/auth/login"')
                
                with open('templates/login_enhanced.html', 'w', encoding='utf-8') as f:
                    f.write(content)
            
            logger.info("Login template checked and fixed if needed")
            
        except Exception as e:
            logger.error(f"Error checking login template: {e}")

def ensure_admin_user_exists(app):
    """Ensure an admin user exists in the database"""
    from database.db_setup import db
    from database.models import User, Role, Branch
    
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            logger.info("Admin user not found, creating one")
            
            # Check if we have a branch
            branch = Branch.query.first()
            
            if not branch:
                logger.info("No branch found, creating main branch")
                branch = Branch(name="Main Branch", is_active=True, is_main=True)
                db.session.add(branch)
                db.session.flush()
            
            # Check if admin role exists
            admin_role = Role.query.filter_by(name='admin').first()
            
            # Create admin user
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@example.com',
                is_active=True,
                branch_id=branch.id
            )
            
            # Assign admin role if it exists
            if admin_role:
                admin.roles.append(admin_role)
            
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")

def main():
    """Main function"""
    logger.info("Starting simple login fix for StockMaster Pro...")
    
    try:
        # Create app
        app = create_app()
        
        # Ensure login template is correct
        ensure_login_template_is_correct(app)
        
        # Ensure admin user exists
        ensure_admin_user_exists(app)
        
        logger.info("Login fixes applied. Running application...")
        logger.info("You can now access the application at http://localhost:5000")
        logger.info("Login with: admin / admin123")
        
        # Run the app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"Error during fix: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 