"""
Test database connection
"""

import os
import sys
from flask import Flask
from werkzeug.security import generate_password_hash

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_db_connection():
    """Test database connection"""
    from database.db_setup import db, init_db
    from database.models import User, Branch
    
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
    
    # Test database connection
    with app.app_context():
        try:
            # Check if users table exists
            users = User.query.all()
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")
            
            # Check if branches table exists
            branches = Branch.query.all()
            print(f"Found {len(branches)} branches:")
            for branch in branches:
                print(f"  ID: {branch.id}, Name: {branch.name}")
            
            # Create a test user if no users exist
            if not users:
                print("Creating a test user...")
                
                # Check if a branch exists
                if not branches:
                    print("Creating a test branch...")
                    branch = Branch(
                        name="Test Branch",
                        is_active=True,
                        is_main=True
                    )
                    db.session.add(branch)
                    db.session.commit()
                    branch_id = branch.id
                else:
                    branch_id = branches[0].id
                
                # Create a test user
                user = User(
                    username="testuser",
                    password=generate_password_hash("testpass"),
                    coffee_name="Test User",
                    branch_id=branch_id,
                    email="test@example.com",
                    is_active=True,
                    preferred_language="en",
                    theme="light",
                    theme_color="blue",
                    is_superuser=True,
                    is_system_admin=True
                )
                db.session.add(user)
                db.session.commit()
                print(f"Test user created with ID: {user.id}")
            
            return True
        except Exception as e:
            print(f"Error testing database connection: {e}")
            return False

if __name__ == "__main__":
    test_db_connection()
