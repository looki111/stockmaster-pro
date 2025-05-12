import os
import sys
from flask import Flask
from database.db_setup import db
from database.models import User, Role, Permission, Notification, Shop, Branch
from werkzeug.security import generate_password_hash
import roles

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
        print("Dropping and recreating all tables...")
        db.drop_all()
        db.create_all()
        
        # Create shop
        print("Creating shop...")
        shop = Shop(name="Main Shop", is_active=True)
        db.session.add(shop)
        db.session.flush()
        
        # Create branch
        print("Creating branch...")
        branch = Branch(
            name="Main Branch", 
            is_active=True, 
            is_main=True,
            shop_id=shop.id
        )
        db.session.add(branch)
        db.session.commit()
        
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
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),
                email='admin@stockmaster.com',
                is_active=True,
                branch_id=branch.id
            )
            admin.roles.append(admin_role)
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
            print(f"Username: admin")
            print(f"Password: admin123")
            print(f"Login URL: /auth/login")
        else:
            print("Failed to create admin: superuser role not found.")
        
        print("Database setup completed.")

if __name__ == "__main__":
    main() 