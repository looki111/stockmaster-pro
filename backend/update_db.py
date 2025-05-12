from database.db_setup import db, init_db
from database.models import User
import sqlite3
import os

def add_missing_columns():
    """Add missing columns to the database"""
    print("Adding missing columns to the database...")

    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')

    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Update users table
        print("\n=== Updating users table ===")
        cursor.execute("PRAGMA table_info(users)")
        existing_user_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing user columns: {existing_user_columns}")

        # Define missing columns for users table
        missing_user_columns = {
            'theme_color': "VARCHAR(20) DEFAULT 'blue'",
            'sidebar_collapsed': "BOOLEAN DEFAULT 0",
            'dashboard_layout': "JSON DEFAULT NULL",
            'first_name': "VARCHAR(50) DEFAULT NULL",
            'last_name': "VARCHAR(50) DEFAULT NULL",
            'profile_image': "VARCHAR(255) DEFAULT NULL",
            'job_title': "VARCHAR(100) DEFAULT NULL",
            'bio': "TEXT DEFAULT NULL",
            'is_superuser': "BOOLEAN DEFAULT 0",
            'is_system_admin': "BOOLEAN DEFAULT 0",
            'last_password_change': "DATETIME DEFAULT NULL",
            'failed_login_attempts': "INTEGER DEFAULT 0",
            'account_locked_until': "DATETIME DEFAULT NULL",
            'last_active': "DATETIME DEFAULT NULL",
            'login_ip': "VARCHAR(45) DEFAULT NULL",
            'created_at': "DATETIME DEFAULT NULL",
            'updated_at': "DATETIME DEFAULT NULL"
        }

        # Add missing columns to users table
        for column_name, column_def in missing_user_columns.items():
            if column_name not in existing_user_columns:
                print(f"Adding {column_name} column to users table...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                conn.commit()
                print(f"Column {column_name} added successfully!")
            else:
                print(f"Column {column_name} already exists.")

        # Update branches table
        print("\n=== Updating branches table ===")
        cursor.execute("PRAGMA table_info(branches)")
        existing_branch_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing branch columns: {existing_branch_columns}")

        # Define missing columns for branches table
        missing_branch_columns = {
            'email': "VARCHAR(120) DEFAULT NULL",
            'phone': "VARCHAR(20) DEFAULT NULL",
            'address': "VARCHAR(200) DEFAULT NULL",
            'is_active': "BOOLEAN DEFAULT 1",
            'is_main': "BOOLEAN DEFAULT 0",
            'created_at': "DATETIME DEFAULT NULL",
            'shop_id': "INTEGER DEFAULT NULL",
            'manager_name': "VARCHAR(100) DEFAULT NULL",
            'opening_hours': "VARCHAR(100) DEFAULT NULL",
            'location_lat': "FLOAT DEFAULT NULL",
            'location_lng': "FLOAT DEFAULT NULL",
            'description': "TEXT DEFAULT NULL",
            'image': "VARCHAR(255) DEFAULT NULL",
            'weight_unit': "VARCHAR(10) DEFAULT 'kg'",
            'currency': "VARCHAR(10) DEFAULT 'SAR'",
            'time_format': "VARCHAR(10) DEFAULT '24'",
            'invoice_template': "VARCHAR(50) DEFAULT 'default'",
            'invoice_fields': "JSON DEFAULT NULL",
            'order_types': "JSON DEFAULT NULL",
            'tax_rate': "FLOAT DEFAULT 15.0",
            'pos_printer': "VARCHAR(100) DEFAULT NULL",
            'barcode_printer': "VARCHAR(100) DEFAULT NULL",
            'pos_hardware': "JSON DEFAULT NULL",
            'quick_pos_mode': "BOOLEAN DEFAULT 0",
            'shift_closing_time': "TIME DEFAULT NULL",
            'inventory_sync': "BOOLEAN DEFAULT 1",
            'whatsapp_api': "VARCHAR(200) DEFAULT NULL",
            'sms_api': "VARCHAR(200) DEFAULT NULL",
            'marketing_enabled': "BOOLEAN DEFAULT 0",
            'pos_integration': "VARCHAR(50) DEFAULT NULL",
            'accounting_integration': "VARCHAR(50) DEFAULT NULL",
            'ai_analytics_enabled': "BOOLEAN DEFAULT 0",
            'sales_prediction_enabled': "BOOLEAN DEFAULT 0",
            'inventory_prediction_enabled': "BOOLEAN DEFAULT 0",
            'customer_insights_enabled': "BOOLEAN DEFAULT 0",
            'last_inventory_count': "DATETIME DEFAULT NULL",
            'last_backup': "DATETIME DEFAULT NULL",
            'updated_at': "DATETIME DEFAULT NULL"
        }

        # Add missing columns to branches table
        for column_name, column_def in missing_branch_columns.items():
            if column_name not in existing_branch_columns:
                print(f"Adding {column_name} column to branches table...")
                cursor.execute(f"ALTER TABLE branches ADD COLUMN {column_name} {column_def}")
                conn.commit()
                print(f"Column {column_name} added successfully!")
            else:
                print(f"Column {column_name} already exists.")

        # Close the connection
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating database: {e}")
        return False

if __name__ == "__main__":
    add_missing_columns()
