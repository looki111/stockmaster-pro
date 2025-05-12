"""
Database Schema Fix Tool for StockMaster Pro
This script directly fixes the database schema to match the models
"""

import os
import sqlite3
import sys

def fix_database_schema():
    """Fix the database schema to match the models"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Existing tables: {tables}")
        
        # Check User table columns
        if 'users' in tables:
            cursor.execute("PRAGMA table_info(users)")
            user_columns = [column[1] for column in cursor.fetchall()]
            print(f"Existing user columns: {user_columns}")
            
            # Define expected User columns
            expected_user_columns = [
                'id', 'username', 'password', 'coffee_name', 'branch_id', 'email', 'phone', 
                'is_active', 'last_login', 'preferred_language', 'theme', 'theme_color', 
                'sidebar_collapsed', 'dashboard_layout', 'first_name', 'last_name', 
                'profile_image', 'job_title', 'bio', 'is_superuser', 'is_system_admin', 
                'last_password_change', 'failed_login_attempts', 'account_locked_until', 
                'last_active', 'login_ip', 'created_at', 'updated_at'
            ]
            
            # Add missing User columns
            for column in expected_user_columns:
                if column not in user_columns:
                    print(f"Adding missing column to users table: {column}")
                    
                    # Define column type based on name
                    if column in ['is_active', 'is_superuser', 'is_system_admin', 'sidebar_collapsed']:
                        column_type = "BOOLEAN DEFAULT 0"
                    elif column in ['last_login', 'last_password_change', 'account_locked_until', 'last_active', 'created_at', 'updated_at']:
                        column_type = "DATETIME DEFAULT NULL"
                    elif column in ['failed_login_attempts']:
                        column_type = "INTEGER DEFAULT 0"
                    elif column in ['dashboard_layout']:
                        column_type = "TEXT DEFAULT NULL"
                    elif column in ['theme_color']:
                        column_type = "VARCHAR(20) DEFAULT 'blue'"
                    elif column in ['preferred_language']:
                        column_type = "VARCHAR(2) DEFAULT 'ar'"
                    elif column in ['theme']:
                        column_type = "VARCHAR(10) DEFAULT 'light'"
                    else:
                        column_type = "VARCHAR(255) DEFAULT NULL"
                    
                    # Execute ALTER TABLE statement
                    try:
                        cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {column_type}")
                        print(f"Added column {column} to users table")
                    except sqlite3.OperationalError as e:
                        print(f"Error adding column {column}: {e}")
        
        # Check Branch table columns
        if 'branches' in tables:
            cursor.execute("PRAGMA table_info(branches)")
            branch_columns = [column[1] for column in cursor.fetchall()]
            print(f"Existing branch columns: {branch_columns}")
            
            # Define expected Branch columns
            expected_branch_columns = [
                'id', 'name', 'address', 'phone', 'email', 'is_active', 'is_main', 'created_at',
                'shop_id', 'manager_name', 'opening_hours', 'location_lat', 'location_lng',
                'description', 'image', 'weight_unit', 'currency', 'time_format',
                'invoice_template', 'invoice_fields', 'order_types', 'tax_rate',
                'pos_printer', 'barcode_printer', 'pos_hardware', 'quick_pos_mode',
                'shift_closing_time', 'inventory_sync', 'whatsapp_api', 'sms_api',
                'marketing_enabled', 'pos_integration', 'accounting_integration',
                'ai_analytics_enabled', 'sales_prediction_enabled', 'inventory_prediction_enabled',
                'customer_insights_enabled', 'last_inventory_count', 'last_backup', 'updated_at'
            ]
            
            # Add missing Branch columns
            for column in expected_branch_columns:
                if column not in branch_columns:
                    print(f"Adding missing column to branches table: {column}")
                    
                    # Define column type based on name
                    if column in ['is_active', 'is_main', 'quick_pos_mode', 'inventory_sync', 
                                 'marketing_enabled', 'ai_analytics_enabled', 'sales_prediction_enabled', 
                                 'inventory_prediction_enabled', 'customer_insights_enabled']:
                        column_type = "BOOLEAN DEFAULT 0"
                    elif column in ['created_at', 'last_inventory_count', 'last_backup', 'updated_at']:
                        column_type = "DATETIME DEFAULT NULL"
                    elif column in ['tax_rate']:
                        column_type = "FLOAT DEFAULT 15.0"
                    elif column in ['location_lat', 'location_lng']:
                        column_type = "FLOAT DEFAULT NULL"
                    elif column in ['invoice_fields', 'order_types', 'pos_hardware']:
                        column_type = "TEXT DEFAULT NULL"
                    elif column in ['weight_unit']:
                        column_type = "VARCHAR(10) DEFAULT 'kg'"
                    elif column in ['currency']:
                        column_type = "VARCHAR(10) DEFAULT 'SAR'"
                    elif column in ['time_format']:
                        column_type = "VARCHAR(10) DEFAULT '24'"
                    elif column in ['invoice_template']:
                        column_type = "VARCHAR(50) DEFAULT 'default'"
                    elif column in ['shift_closing_time']:
                        column_type = "TIME DEFAULT NULL"
                    else:
                        column_type = "VARCHAR(255) DEFAULT NULL"
                    
                    # Execute ALTER TABLE statement
                    try:
                        cursor.execute(f"ALTER TABLE branches ADD COLUMN {column} {column_type}")
                        print(f"Added column {column} to branches table")
                    except sqlite3.OperationalError as e:
                        print(f"Error adding column {column}: {e}")
        
        # Check Shop table columns
        if 'shops' in tables:
            cursor.execute("PRAGMA table_info(shops)")
            shop_columns = [column[1] for column in cursor.fetchall()]
            print(f"Existing shop columns: {shop_columns}")
            
            # Define expected Shop columns
            expected_shop_columns = [
                'id', 'name', 'owner_name', 'email', 'phone', 'address', 'logo',
                'primary_color', 'secondary_color', 'accent_color', 'font_family',
                'custom_domain', 'business_type', 'tax_number', 'currency', 'timezone',
                'website', 'social_facebook', 'social_instagram', 'social_twitter',
                'created_at', 'is_active', 'onboarding_completed', 'referral_code', 'referred_by'
            ]
            
            # Add missing Shop columns
            for column in expected_shop_columns:
                if column not in shop_columns:
                    print(f"Adding missing column to shops table: {column}")
                    
                    # Define column type based on name
                    if column in ['is_active', 'onboarding_completed']:
                        column_type = "BOOLEAN DEFAULT 0"
                    elif column in ['created_at']:
                        column_type = "DATETIME DEFAULT NULL"
                    elif column in ['primary_color']:
                        column_type = "VARCHAR(20) DEFAULT '#4A90E2'"
                    elif column in ['secondary_color']:
                        column_type = "VARCHAR(20) DEFAULT '#FFA726'"
                    elif column in ['accent_color']:
                        column_type = "VARCHAR(20) DEFAULT '#4CAF50'"
                    elif column in ['font_family']:
                        column_type = "VARCHAR(100) DEFAULT 'Cairo, sans-serif'"
                    elif column in ['business_type']:
                        column_type = "VARCHAR(50) DEFAULT 'coffee_shop'"
                    elif column in ['currency']:
                        column_type = "VARCHAR(10) DEFAULT 'SAR'"
                    elif column in ['timezone']:
                        column_type = "VARCHAR(50) DEFAULT 'Asia/Riyadh'"
                    else:
                        column_type = "VARCHAR(255) DEFAULT NULL"
                    
                    # Execute ALTER TABLE statement
                    try:
                        cursor.execute(f"ALTER TABLE shops ADD COLUMN {column} {column_type}")
                        print(f"Added column {column} to shops table")
                    except sqlite3.OperationalError as e:
                        print(f"Error adding column {column}: {e}")
        
        conn.commit()
        print("Database schema fixed successfully!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error fixing database schema: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database schema fix...")
    fix_database_schema()
    print("Database schema fix completed!")
