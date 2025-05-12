from app import app, db
from database.models import User, Branch
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Drop all tables first
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create default branch
        default_branch = Branch(
            name="الفرع الرئيسي",
            address="العنوان الرئيسي",
            phone="1234567890",
            is_active=True,
            weight_unit='kg',
            currency='SAR',
            time_format='24',
            invoice_template='default',
            invoice_fields={},
            order_types=['dine-in', 'takeaway', 'delivery']
        )
        db.session.add(default_branch)
        db.session.commit()
        
        # Create admin user
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            coffee_name="مدير النظام",
            branch_id=default_branch.id,
            email="admin@example.com",
            is_active=True,
            preferred_language="ar",
            theme="light",
            theme_color="blue",
            is_superuser=True,
            is_system_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == "__main__":
    init_db() 