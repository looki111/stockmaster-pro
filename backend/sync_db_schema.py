"""
Comprehensive Database Schema Sync Tool for StockMaster Pro
This script checks all models against the database schema and fixes any discrepancies
"""

import os
import sqlite3
import inspect
import sys
from sqlalchemy import inspect as sa_inspect
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all models
from database.db_setup import db, init_db
from database.models import *
from database.inventory_models import *
from database.subscription_models import *

def get_all_models():
    """Get all SQLAlchemy models defined in the application"""
    models = []
    
    # Get all models from database.models
    for name, obj in inspect.getmembers(sys.modules['database.models']):
        if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
            models.append(obj)
    
    # Get all models from database.inventory_models
    for name, obj in inspect.getmembers(sys.modules['database.inventory_models']):
        if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
            models.append(obj)
    
    # Get all models from database.subscription_models
    for name, obj in inspect.getmembers(sys.modules['database.subscription_models']):
        if inspect.isclass(obj) and hasattr(obj, '__tablename__'):
            models.append(obj)
    
    return models

def get_db_tables_and_columns():
    """Get all tables and their columns from the SQLite database"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return {}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    db_schema = {}
    
    # Get columns for each table
    for table in tables:
        table_name = table[0]
        if table_name.startswith('sqlite_'):
            continue
            
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Column info format: (cid, name, type, notnull, dflt_value, pk)
        db_schema[table_name] = {col[1]: col[2] for col in columns}
    
    conn.close()
    return db_schema

def generate_alter_statements(models, db_schema):
    """Generate ALTER TABLE statements to sync the database schema with the models"""
    alter_statements = []
    
    for model in models:
        table_name = model.__tablename__
        
        # Skip if table doesn't exist in the database
        if table_name not in db_schema:
            print(f"Table {table_name} doesn't exist in the database")
            continue
        
        # Get model columns
        inspector = sa_inspect(db.engine)
        model_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        
        # Check for missing columns
        for column_name, column in model_columns.items():
            if column_name not in db_schema[table_name]:
                # Generate SQL type from SQLAlchemy type
                sql_type = column['type']
                
                # Handle default values
                default_value = ""
                if column.get('default') is not None:
                    if isinstance(column['default'], str):
                        default_value = f" DEFAULT '{column['default']}'"
                    else:
                        default_value = f" DEFAULT {column['default']}"
                
                # Handle nullable
                nullable = "" if column.get('nullable', True) else " NOT NULL"
                
                alter_statements.append(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}{nullable}{default_value};"
                )
    
    return alter_statements

def apply_schema_changes():
    """Apply schema changes to the database"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    # Get all models and database schema
    models = get_all_models()
    db_schema = get_db_tables_and_columns()
    
    # Generate ALTER statements
    alter_statements = generate_alter_statements(models, db_schema)
    
    if not alter_statements:
        print("Database schema is up to date!")
        return True
    
    print(f"Found {len(alter_statements)} schema changes to apply:")
    for stmt in alter_statements:
        print(f"  {stmt}")
    
    # Apply changes
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        for stmt in alter_statements:
            print(f"Executing: {stmt}")
            cursor.execute(stmt)
        
        conn.commit()
        print("All schema changes applied successfully!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error applying schema changes: {e}")
        return False
    finally:
        conn.close()

def manual_fixes():
    """Apply manual fixes for specific issues"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'stockmaster.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Fix specific issues that might not be caught by the automatic process
        fixes = [
            # Add any manual fixes here
            "PRAGMA foreign_keys = OFF;",
            
            # Ensure all User model columns exist
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS theme_color VARCHAR(20) DEFAULT 'blue';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS sidebar_collapsed BOOLEAN DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS dashboard_layout JSON DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(50) DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(50) DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image VARCHAR(255) DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS job_title VARCHAR(100) DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_system_admin BOOLEAN DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_password_change DATETIME DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until DATETIME DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active DATETIME DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_ip VARCHAR(45) DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at DATETIME DEFAULT NULL;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT NULL;",
            
            # Ensure all Branch model columns exist
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS email VARCHAR(120) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS phone VARCHAR(20) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS address VARCHAR(200) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT 1;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS is_main BOOLEAN DEFAULT 0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS created_at DATETIME DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS shop_id INTEGER DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS manager_name VARCHAR(100) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS opening_hours VARCHAR(100) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS location_lat FLOAT DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS location_lng FLOAT DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS description TEXT DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS image VARCHAR(255) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS weight_unit VARCHAR(10) DEFAULT 'kg';",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'SAR';",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS time_format VARCHAR(10) DEFAULT '24';",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS invoice_template VARCHAR(50) DEFAULT 'default';",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS invoice_fields JSON DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS order_types JSON DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS tax_rate FLOAT DEFAULT 15.0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS pos_printer VARCHAR(100) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS barcode_printer VARCHAR(100) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS pos_hardware JSON DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS quick_pos_mode BOOLEAN DEFAULT 0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS shift_closing_time TIME DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS inventory_sync BOOLEAN DEFAULT 1;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS whatsapp_api VARCHAR(200) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS sms_api VARCHAR(200) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS marketing_enabled BOOLEAN DEFAULT 0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS pos_integration VARCHAR(50) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS accounting_integration VARCHAR(50) DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS ai_analytics_enabled BOOLEAN DEFAULT 0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS sales_prediction_enabled BOOLEAN DEFAULT 0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS inventory_prediction_enabled BOOLEAN DEFAULT 0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS customer_insights_enabled BOOLEAN DEFAULT 0;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS last_inventory_count DATETIME DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS last_backup DATETIME DEFAULT NULL;",
            "ALTER TABLE branches ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT NULL;",
            
            "PRAGMA foreign_keys = ON;"
        ]
        
        for fix in fixes:
            print(f"Executing: {fix}")
            cursor.execute(fix)
        
        conn.commit()
        print("All manual fixes applied successfully!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error applying manual fixes: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting comprehensive database schema sync...")
    
    # Apply manual fixes first
    print("\n=== Applying manual fixes ===")
    manual_fixes()
    
    # Then apply automatic schema changes
    print("\n=== Applying automatic schema changes ===")
    apply_schema_changes()
    
    print("\nDatabase schema sync completed!")
