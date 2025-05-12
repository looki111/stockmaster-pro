"""
Test login functionality directly
"""

import os
import sys
from flask import Flask
from werkzeug.security import check_password_hash

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_login_direct():
    """Test login functionality directly"""
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
    
    # Test login
    with app.app_context():
        try:
            # Get all users
            users = User.query.all()
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
            
            # Test login with admin user
            username = "admin"
            password = "admin123"
            
            user = User.query.filter_by(username=username).first()
            
            if user:
                print(f"Found user: {user.username}")
                print(f"Password hash: {user.password}")
                
                # Check password
                if check_password_hash(user.password, password):
                    print(f"Login successful for user {username}!")
                else:
                    print(f"Login failed for user {username}: Invalid password")
            else:
                print(f"Login failed for user {username}: User not found")
            
            return True
        except Exception as e:
            print(f"Error testing login: {e}")
            return False

if __name__ == "__main__":
    test_login_direct()
