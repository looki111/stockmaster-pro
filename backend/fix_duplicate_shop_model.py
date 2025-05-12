#!/usr/bin/env python
import os
import sys
import importlib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_shop_model_duplication():
    """
    Ensures that both Shop model definitions in models.py and subscription_models.py 
    have the extend_existing=True option to avoid table already exists errors.
    """
    # First, check if the files exist
    models_path = os.path.join('database', 'models.py')
    subscription_models_path = os.path.join('database', 'subscription_models.py')
    
    if not os.path.exists(models_path):
        logger.error(f"Could not find {models_path}")
        return False
    
    if not os.path.exists(subscription_models_path):
        logger.error(f"Could not find {subscription_models_path}")
        return False
    
    # Check if the changes are already applied
    with open(models_path, 'r', encoding='utf-8') as f:
        models_content = f.read()
    
    with open(subscription_models_path, 'r', encoding='utf-8') as f:
        subscription_models_content = f.read()
    
    models_fixed = '__table_args__ = {\'extend_existing\': True}' in models_content
    subscription_models_fixed = '__table_args__ = {\'extend_existing\': True}' in subscription_models_content
    
    # Apply fixes if needed
    if not models_fixed:
        logger.info("Adding extend_existing=True to Shop model in models.py")
        models_content = models_content.replace("class Shop(db.Model):\n    __tablename__ = 'shops'", 
                                               "class Shop(db.Model):\n    __tablename__ = 'shops'\n    __table_args__ = {'extend_existing': True}")
        
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(models_content)
    else:
        logger.info("models.py already fixed")
    
    if not subscription_models_fixed:
        logger.info("Adding extend_existing=True to Shop model in subscription_models.py")
        subscription_models_content = subscription_models_content.replace("class Shop(db.Model):\n    \"\"\"", 
                                                                         "class Shop(db.Model):\n    __table_args__ = {'extend_existing': True}\n    \"\"\"")
        
        with open(subscription_models_path, 'w', encoding='utf-8') as f:
            f.write(subscription_models_content)
    else:
        logger.info("subscription_models.py already fixed")
    
    return True

def create_app_runner():
    """Create a clean runner script that imports modules in the correct order"""
    runner_path = "run_app.py"
    
    script_content = """#!/usr/bin/env python
import os
import sys
from flask import Flask
from database.db_setup import db, init_db

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
    init_db(app)
    
    # Import and register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Import other routes after database is initialized
    from routes.dashboard import dashboard_bp
    from routes.clients import clients_bp
    from routes.promotions import promotions_bp
    from routes.subscription import subscription_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(promotions_bp)
    app.register_blueprint(subscription_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
    
    with open(runner_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    logger.info(f"Created {runner_path} for running the app with fixed imports")
    return True

def main():
    logger.info("Starting fix for duplicate Shop model definitions")
    
    # Fix the model files
    if fix_shop_model_duplication():
        logger.info("Shop model duplication issue fixed successfully")
    else:
        logger.error("Failed to fix Shop model duplication")
        return False
    
    # Create a runner script
    if create_app_runner():
        logger.info("Created runner script for fixed application")
        logger.info("You can now run the application with: python run_app.py")
    
    return True

if __name__ == "__main__":
    main() 