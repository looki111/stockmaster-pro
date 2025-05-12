"""
Inventory Upgrade Migration Script for StockMaster Pro
Updates the database schema to support the enhanced inventory system
"""

import sqlite3
import os
import sys
from datetime import datetime

def upgrade_database(db_path):
    """
    Upgrade the database schema to support the enhanced inventory system
    
    Args:
        db_path: Path to the SQLite database file
    """
    print(f"Upgrading database at {db_path}...")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Update the raw_materials table
        print("Updating raw_materials table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(raw_materials)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'branch_id' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN branch_id INTEGER")
        
        if 'shop_id' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN shop_id INTEGER")
        
        if 'average_cost' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN average_cost REAL")
        
        if 'last_purchase_price' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN last_purchase_price REAL")
        
        if 'manufacturing_date' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN manufacturing_date TIMESTAMP")
        
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN updated_at TIMESTAMP")
        
        if 'storage_location' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN storage_location TEXT")
        
        if 'barcode' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN barcode TEXT")
        
        if 'sku' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN sku TEXT")
        
        if 'daily_usage_rate' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN daily_usage_rate REAL")
        
        if 'reorder_point' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN reorder_point REAL")
        
        if 'reorder_quantity' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN reorder_quantity REAL")
        
        if 'waste_percentage' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN waste_percentage REAL DEFAULT 0")
        
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN is_active INTEGER DEFAULT 1")
        
        if 'status' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN status TEXT DEFAULT 'in_stock'")
        
        if 'description' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN description TEXT")
        
        if 'notes' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN notes TEXT")
        
        if 'image' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN image TEXT")
        
        if 'category' not in columns:
            cursor.execute("ALTER TABLE raw_materials ADD COLUMN category TEXT")
        
        # 2. Update the products table
        print("Updating products table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(products)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'shop_id' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN shop_id INTEGER")
        
        if 'description' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN description TEXT")
        
        if 'category' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
        
        if 'image' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN image TEXT")
        
        if 'barcode' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
        
        if 'sku' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN sku TEXT")
        
        if 'cost_price' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN cost_price REAL")
        
        if 'tax_rate' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN tax_rate REAL")
        
        if 'discount_price' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN discount_price REAL")
        
        if 'alert_threshold' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN alert_threshold REAL DEFAULT 5")
        
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN is_active INTEGER DEFAULT 1")
        
        if 'is_featured' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN is_featured INTEGER DEFAULT 0")
        
        if 'has_variants' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN has_variants INTEGER DEFAULT 0")
        
        if 'variants' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN variants JSON")
        
        if 'options' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN options JSON")
        
        if 'preparation_time' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN preparation_time INTEGER")
        
        if 'calories' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN calories INTEGER")
        
        if 'nutritional_info' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN nutritional_info JSON")
        
        if 'allergens' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN allergens JSON")
        
        if 'dietary_info' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN dietary_info JSON")
        
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN updated_at TIMESTAMP")
        
        # 3. Update the recipes table
        print("Updating recipes table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(recipes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'unit' not in columns:
            cursor.execute("ALTER TABLE recipes ADD COLUMN unit TEXT DEFAULT 'g'")
        
        if 'created_at' not in columns:
            cursor.execute("ALTER TABLE recipes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE recipes ADD COLUMN updated_at TIMESTAMP")
        
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE recipes ADD COLUMN is_active INTEGER DEFAULT 1")
        
        # 4. Update the orders table
        print("Updating orders table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(orders)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'order_type' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN order_type TEXT DEFAULT 'dine_in'")
        
        if 'table_number' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN table_number TEXT")
        
        if 'delivery_address' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN delivery_address TEXT")
        
        if 'discount_amount' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN discount_amount REAL DEFAULT 0")
        
        if 'discount_type' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN discount_type TEXT")
        
        if 'discount_reason' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN discount_reason TEXT")
        
        if 'loyalty_points_used' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN loyalty_points_used INTEGER DEFAULT 0")
        
        if 'preparation_status' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN preparation_status TEXT DEFAULT 'ready'")
        
        if 'preparation_time' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN preparation_time INTEGER")
        
        if 'inventory_processed' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN inventory_processed INTEGER DEFAULT 0")
        
        if 'completed_at' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN completed_at TIMESTAMP")
        
        if 'shop_id' not in columns:
            cursor.execute("ALTER TABLE orders ADD COLUMN shop_id INTEGER")
        
        # 5. Update the order_items table
        print("Updating order_items table...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(order_items)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'variant' not in columns:
            cursor.execute("ALTER TABLE order_items ADD COLUMN variant TEXT")
        
        if 'options' not in columns:
            cursor.execute("ALTER TABLE order_items ADD COLUMN options JSON")
        
        if 'discount_amount' not in columns:
            cursor.execute("ALTER TABLE order_items ADD COLUMN discount_amount REAL DEFAULT 0")
        
        if 'discount_type' not in columns:
            cursor.execute("ALTER TABLE order_items ADD COLUMN discount_type TEXT")
        
        if 'notes' not in columns:
            cursor.execute("ALTER TABLE order_items ADD COLUMN notes TEXT")
        
        if 'inventory_processed' not in columns:
            cursor.execute("ALTER TABLE order_items ADD COLUMN inventory_processed INTEGER DEFAULT 0")
        
        # 6. Create new inventory tables
        print("Creating new inventory tables...")
        
        # Create inventory_transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            reference_type TEXT,
            reference_id INTEGER,
            raw_material_id INTEGER,
            product_id INTEGER,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            unit_cost REAL,
            branch_id INTEGER NOT NULL,
            shop_id INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (raw_material_id) REFERENCES raw_materials (id),
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (branch_id) REFERENCES branches (id),
            FOREIGN KEY (shop_id) REFERENCES shops (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        """)
        
        # Create consumption_rules table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumption_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            raw_material_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            waste_factor REAL DEFAULT 0,
            condition_type TEXT,
            condition_value TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (raw_material_id) REFERENCES raw_materials (id)
        )
        """)
        
        # Create stock_counts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count_date TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'draft',
            branch_id INTEGER NOT NULL,
            shop_id INTEGER,
            created_by INTEGER,
            completed_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (branch_id) REFERENCES branches (id),
            FOREIGN KEY (shop_id) REFERENCES shops (id),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (completed_by) REFERENCES users (id)
        )
        """)
        
        # Create stock_count_items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_count_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_count_id INTEGER NOT NULL,
            raw_material_id INTEGER,
            expected_quantity REAL,
            actual_quantity REAL,
            unit TEXT NOT NULL,
            variance REAL,
            variance_percentage REAL,
            variance_cost REAL,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            FOREIGN KEY (stock_count_id) REFERENCES stock_counts (id),
            FOREIGN KEY (raw_material_id) REFERENCES raw_materials (id)
        )
        """)
        
        # Create inventory_adjustments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adjustment_date TIMESTAMP NOT NULL,
            adjustment_type TEXT NOT NULL,
            branch_id INTEGER NOT NULL,
            shop_id INTEGER,
            created_by INTEGER,
            approved_by INTEGER,
            status TEXT DEFAULT 'pending',
            reason TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            FOREIGN KEY (branch_id) REFERENCES branches (id),
            FOREIGN KEY (shop_id) REFERENCES shops (id),
            FOREIGN KEY (created_by) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
        """)
        
        # Create inventory_adjustment_items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_adjustment_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adjustment_id INTEGER NOT NULL,
            raw_material_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            unit_cost REAL,
            FOREIGN KEY (adjustment_id) REFERENCES inventory_adjustments (id),
            FOREIGN KEY (raw_material_id) REFERENCES raw_materials (id)
        )
        """)
        
        # Create daily_stock_reports table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stock_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date DATE NOT NULL,
            branch_id INTEGER NOT NULL,
            shop_id INTEGER,
            status TEXT DEFAULT 'generated',
            total_items INTEGER,
            low_stock_items INTEGER,
            out_of_stock_items INTEGER,
            total_value REAL,
            total_consumption REAL,
            waste_percentage REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (branch_id) REFERENCES branches (id),
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        )
        """)
        
        # Create daily_stock_report_items table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_stock_report_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            raw_material_id INTEGER NOT NULL,
            opening_quantity REAL NOT NULL,
            received_quantity REAL DEFAULT 0,
            consumed_quantity REAL DEFAULT 0,
            waste_quantity REAL DEFAULT 0,
            adjusted_quantity REAL DEFAULT 0,
            closing_quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            unit_cost REAL,
            total_value REAL,
            status TEXT,
            FOREIGN KEY (report_id) REFERENCES daily_stock_reports (id),
            FOREIGN KEY (raw_material_id) REFERENCES raw_materials (id)
        )
        """)
        
        # Commit the transaction
        conn.commit()
        print("Database upgrade completed successfully!")
        
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"Error upgrading database: {str(e)}")
        return False
    finally:
        # Close the connection
        conn.close()
    
    return True

if __name__ == "__main__":
    # Get database path from command line argument or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else "instance/stockmaster.db"
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        sys.exit(1)
    
    # Upgrade the database
    if upgrade_database(db_path):
        print("Database upgrade completed successfully!")
        sys.exit(0)
    else:
        print("Database upgrade failed!")
        sys.exit(1)
