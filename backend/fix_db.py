import os
import sys
from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles
from flask import Flask

# Make sure the working directory is correct
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Custom SQL compiler directive for SQLite
@compiles(DropTable, "sqlite")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " IF EXISTS"

def fix_database():
    from database.db_setup import db, init_db
    from app import app

    # Check if the database file exists
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'stockmaster.db')
    if os.path.exists(db_path):
        # Backup the old database
        backup_path = db_path + '.backup'
        try:
            os.rename(db_path, backup_path)
            print(f"Existing database backed up to {backup_path}")
        except Exception as e:
            print(f"Could not backup database: {str(e)}")
    
    # Initialize the database with the app context
    with app.app_context():
        # Drop all tables and recreate them
        try:
            db.drop_all()
            print("All tables dropped successfully")
            db.create_all()
            print("All tables recreated successfully")
            
            # Create admin user
            from database.models import User, Branch
            from werkzeug.security import generate_password_hash
            
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
                is_main=True
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
            
            print("Admin user created successfully")
            return True
        except Exception as e:
            print(f"Error fixing database: {str(e)}")
            return False

if __name__ == "__main__":
    print("Starting database fix process...")
    if fix_database():
        print("Database fix completed successfully!")
    else:
        print("Database fix failed.") 