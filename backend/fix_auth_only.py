#!/usr/bin/env python
"""
Minimal Auth-Only Fix for StockMaster Pro
This script creates a minimal app with only auth functionality
"""

import os
import sys
from flask import Flask, render_template_string, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'auth-fix-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockmaster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize SQLAlchemy
from database.db_setup import db
db.init_app(app)

# User model (simplified)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True)
    is_active = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in
    if current_user.is_authenticated:
        return redirect(url_for('success'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.info(f"Login attempt for user: {username}")
        
        try:
            # Find user
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                logger.info(f"Valid credentials for user: {username}")
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('success'))
            else:
                logger.warning(f"Invalid credentials for user: {username}")
                flash('Invalid username or password', 'error')
        except Exception as e:
            logger.error(f"Login error: {e}")
            flash('An error occurred. Please try again.', 'error')
    
    # Render simple login form
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f7f7f7; }
                .container { max-width: 400px; margin: 100px auto; padding: 20px; background-color: white; border-radius: 5px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
                h1 { text-align: center; color: #333; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; }
                input[type="text"], input[type="password"] { width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ddd; border-radius: 3px; }
                button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background-color: #45a049; }
                .flash { padding: 10px; margin-bottom: 10px; border-radius: 3px; }
                .flash.error { background-color: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }
                .flash.success { background-color: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>StockMaster Pro Login</h1>
                
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="flash {{ category }}">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <form method="POST" action="{{ url_for('login') }}">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">Password</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
    ''')

@app.route('/success')
@login_required
def success():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Success</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f7f7f7; }
                .container { max-width: 600px; margin: 100px auto; padding: 20px; background-color: white; border-radius: 5px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
                h1 { text-align: center; color: #333; }
                p { text-align: center; }
                .success-icon { text-align: center; font-size: 48px; color: #4CAF50; margin-bottom: 20px; }
                .button { display: inline-block; padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 3px; }
                .button:hover { background-color: #45a049; }
                .center { text-align: center; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✓</div>
                <h1>Login Successful!</h1>
                <p>You are now logged in as <strong>{{ current_user.username }}</strong>.</p>
                <p>This confirms that the login functionality is working correctly.</p>
                <div class="center">
                    <a href="{{ url_for('logout') }}" class="button">Logout</a>
                </div>
            </div>
        </body>
        </html>
    ''')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

def ensure_admin_exists():
    """Make sure we have at least one admin user"""
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            logger.info("Admin user not found, creating one")
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@example.com',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")

def main():
    """Main function"""
    try:
        # Initialize database
        with app.app_context():
            db.create_all()
        
        # Ensure admin user exists
        ensure_admin_exists()
        
        # Print instructions
        logger.info("============================================")
        logger.info("Auth-only fix started successfully!")
        logger.info("Access the application at: http://localhost:5000")
        logger.info("Login with: admin / admin123")
        logger.info("============================================")
        
        # Run the app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 