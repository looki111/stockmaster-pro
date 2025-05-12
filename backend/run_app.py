#!/usr/bin/env python
import os
import sys
import logging
from flask import Flask, g, render_template
from dotenv import load_dotenv
from database.db_setup import db, init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_app():
    """Create a Flask application instance"""
    app = Flask(__name__)
    
    # Configuration
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        
    # Load configuration from environment variables
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'stockmaster-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(instance_path, "stockmaster.db")}'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TEMPLATES_AUTO_RELOAD=True,
        SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
        SUPABASE_URL=os.getenv('SUPABASE_URL', ''),
        SUPABASE_KEY=os.getenv('SUPABASE_KEY', ''),
        SUPABASE_SERVICE_ROLE_KEY=os.getenv('SUPABASE_SERVICE_ROLE_KEY', ''),
        FORCE_ADMIN_SECRET=os.getenv('FORCE_ADMIN_SECRET', 'stockmaster-admin-secret'),
    )
    
    # Initialize database
    init_db(app)
    
    # Import and register auth blueprint first
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Import Supabase auth blueprint and register it
    try:
        from routes.supabase_auth import supabase_auth_bp
        app.register_blueprint(supabase_auth_bp, url_prefix='/auth')
        logger.info("Registered Supabase authentication routes")
    except ImportError as e:
        logger.warning(f"Could not import Supabase auth blueprint: {e}")
    
    # Apply Supabase middleware
    try:
        from middleware.supabase_middleware import apply_supabase_middleware
        apply_supabase_middleware(app)
        logger.info("Applied Supabase authentication middleware")
    except ImportError as e:
        logger.warning(f"Could not apply Supabase middleware: {e}")
    
    # Import other routes after database is initialized
    from routes.dashboard import dashboard_bp
    from routes.clients import clients_bp
    from routes.promotions import promotions_bp
    from routes.subscription import subscription_bp
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(promotions_bp)
    app.register_blueprint(subscription_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    # Clean up context data
    @app.teardown_appcontext
    def close_db_connection(error):
        """Close database connection at the end of request"""
        db.session.remove()
    
    return app

def main():
    """Run the application"""
    app = create_app()
    app.run(debug=True)

if __name__ == "__main__":
    main()
