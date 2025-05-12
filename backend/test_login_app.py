"""
Test login functionality
"""

import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_app():
    """Create a test Flask application"""
    from database.db_setup import db, init_db
    from database.models import User
    
    # Create a Flask app
    app = Flask(__name__)
    
    # Make sure the instance directory exists
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Configure the app
    app.config.update(
        SECRET_KEY='your-secret-key-here',
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{os.path.join(instance_path, "stockmaster.db")}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=True
    )
    
    # Initialize database
    init_db(app)
    
    # Define routes
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            with app.app_context():
                user = User.query.filter_by(username=username).first()
                
                if user and check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    session['username'] = user.username
                    return redirect(url_for('dashboard'))
                
                flash('Invalid username or password', 'error')
        
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        with app.app_context():
            user = User.query.get(session['user_id'])
            return render_template('dashboard.html', user=user)
    
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('username', None)
        return redirect(url_for('login'))
    
    return app

if __name__ == "__main__":
    app = create_test_app()
    app.run(debug=True)
