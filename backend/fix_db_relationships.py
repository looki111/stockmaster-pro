import os
import sys
from flask import Flask
from database.db_setup import db
from database.models import User, Role, Permission, Notification, ActivityLog
import roles

def get_project_root():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockmaster.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'stockmaster-secret-key'
    
    # Initialize database
    db.init_app(app)
    
    return app

def main():
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("Dropping and recreating all tables...")
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        
        # Initialize roles and permissions
        print("Initializing roles and permissions...")
        try:
            roles.init_roles_and_permissions(app)
            print("Roles and permissions initialized successfully.")
        except Exception as e:
            print(f"Error initializing roles and permissions: {e}")
            return
        
        # Create admin user
        print("Creating admin user...")
        admin_role = Role.query.filter_by(name='superuser').first()
        
        if admin_role:
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@stockmaster.com',
                is_active=True
            )
            admin.roles.append(admin_role)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Failed to create admin: superuser role not found.")
        
        print("Database setup completed.")

if __name__ == "__main__":
    main() 