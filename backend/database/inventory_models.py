"""
Enhanced Inventory Models for StockMaster Pro
These models handle advanced inventory tracking, consumption rules, and stock reports
"""

from datetime import datetime, timedelta
from .db_setup import db
from sqlalchemy.ext.hybrid import hybrid_property

class InventoryTransaction(db.Model):
    """
    Inventory Transaction model tracks all inventory movements
    """
    __tablename__ = 'inventory_transactions'
    id = db.Column(db.Integer, primary_key=True)
    
    # Transaction details
    transaction_type = db.Column(db.String(20), nullable=False)  # purchase, sale, adjustment, transfer, waste
    reference_type = db.Column(db.String(20))  # order, purchase, adjustment, transfer
    reference_id = db.Column(db.Integer)  # ID of the related entity
    
    # Item details
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    # Quantity details
    quantity = db.Column(db.Float, nullable=False)  # Positive for additions, negative for deductions
    unit = db.Column(db.String(20), nullable=False)
    unit_cost = db.Column(db.Float)  # Cost per unit at time of transaction
    
    # Location details
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    
    # User details
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relationships
    raw_material = db.relationship("RawMaterial", backref="transactions")
    product = db.relationship("Product", backref="transactions")
    branch = db.relationship("Branch", backref="inventory_transactions")
    user = db.relationship("User", backref="inventory_transactions")

class StockCount(db.Model):
    """
    Stock Count model for periodic inventory counts
    """
    __tablename__ = 'stock_counts'
    id = db.Column(db.Integer, primary_key=True)
    
    # Count details
    count_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='draft')  # draft, in_progress, completed, cancelled
    
    # Location details
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    
    # User details
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relationships
    branch = db.relationship("Branch", backref="stock_counts")
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_stock_counts")
    completer = db.relationship("User", foreign_keys=[completed_by], backref="completed_stock_counts")
    items = db.relationship("StockCountItem", back_populates="stock_count", cascade="all, delete-orphan")

class StockCountItem(db.Model):
    """
    Stock Count Item model for individual items in a stock count
    """
    __tablename__ = 'stock_count_items'
    id = db.Column(db.Integer, primary_key=True)
    
    # Count details
    stock_count_id = db.Column(db.Integer, db.ForeignKey('stock_counts.id'), nullable=False)
    
    # Item details
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'))
    
    # Quantity details
    expected_quantity = db.Column(db.Float)  # Quantity in system before count
    actual_quantity = db.Column(db.Float)  # Actual counted quantity
    unit = db.Column(db.String(20), nullable=False)
    
    # Variance details
    variance = db.Column(db.Float)  # Difference between expected and actual
    variance_percentage = db.Column(db.Float)  # Percentage variance
    variance_cost = db.Column(db.Float)  # Cost of variance
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, counted, adjusted
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relationships
    stock_count = db.relationship("StockCount", back_populates="items")
    raw_material = db.relationship("RawMaterial")

class ConsumptionRule(db.Model):
    """
    Consumption Rule model defines how raw materials are consumed by products
    This is an enhanced version of the Recipe model with more detailed tracking
    """
    __tablename__ = 'consumption_rules'
    id = db.Column(db.Integer, primary_key=True)
    
    # Product details
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Raw material details
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'), nullable=False)
    
    # Consumption details
    quantity = db.Column(db.Float, nullable=False)  # Amount of raw material used
    unit = db.Column(db.String(20), nullable=False)  # Unit of measurement
    
    # Waste factor (percentage of additional material to account for waste)
    waste_factor = db.Column(db.Float, default=0)  # e.g., 0.05 for 5% waste
    
    # Conditional consumption (e.g., only for large size)
    condition_type = db.Column(db.String(50))  # size, option, etc.
    condition_value = db.Column(db.String(50))  # large, extra_shot, etc.
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship("Product", backref="consumption_rules")
    raw_material = db.relationship("RawMaterial", backref="consumption_rules")

class InventoryAdjustment(db.Model):
    """
    Inventory Adjustment model for manual adjustments to inventory
    """
    __tablename__ = 'inventory_adjustments'
    id = db.Column(db.Integer, primary_key=True)
    
    # Adjustment details
    adjustment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    adjustment_type = db.Column(db.String(20), nullable=False)  # addition, deduction, waste, spoilage, correction
    
    # Location details
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    
    # User details
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    
    # Reason and notes
    reason = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # Relationships
    branch = db.relationship("Branch", backref="inventory_adjustments")
    creator = db.relationship("User", foreign_keys=[created_by], backref="created_adjustments")
    approver = db.relationship("User", foreign_keys=[approved_by], backref="approved_adjustments")
    items = db.relationship("InventoryAdjustmentItem", back_populates="adjustment", cascade="all, delete-orphan")

class InventoryAdjustmentItem(db.Model):
    """
    Inventory Adjustment Item model for individual items in an adjustment
    """
    __tablename__ = 'inventory_adjustment_items'
    id = db.Column(db.Integer, primary_key=True)
    
    # Adjustment details
    adjustment_id = db.Column(db.Integer, db.ForeignKey('inventory_adjustments.id'), nullable=False)
    
    # Item details
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'), nullable=False)
    
    # Quantity details
    quantity = db.Column(db.Float, nullable=False)  # Positive for additions, negative for deductions
    unit = db.Column(db.String(20), nullable=False)
    unit_cost = db.Column(db.Float)
    
    # Relationships
    adjustment = db.relationship("InventoryAdjustment", back_populates="items")
    raw_material = db.relationship("RawMaterial")

class DailyStockReport(db.Model):
    """
    Daily Stock Report model for tracking daily inventory status
    """
    __tablename__ = 'daily_stock_reports'
    id = db.Column(db.Integer, primary_key=True)
    
    # Report details
    report_date = db.Column(db.Date, nullable=False)
    
    # Location details
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    
    # Status
    status = db.Column(db.String(20), default='generated')  # generated, reviewed
    
    # Summary metrics
    total_items = db.Column(db.Integer)
    low_stock_items = db.Column(db.Integer)
    out_of_stock_items = db.Column(db.Integer)
    total_value = db.Column(db.Float)
    total_consumption = db.Column(db.Float)
    waste_percentage = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    branch = db.relationship("Branch", backref="daily_stock_reports")
    items = db.relationship("DailyStockReportItem", back_populates="report", cascade="all, delete-orphan")

class DailyStockReportItem(db.Model):
    """
    Daily Stock Report Item model for individual items in a daily report
    """
    __tablename__ = 'daily_stock_report_items'
    id = db.Column(db.Integer, primary_key=True)
    
    # Report details
    report_id = db.Column(db.Integer, db.ForeignKey('daily_stock_reports.id'), nullable=False)
    
    # Item details
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'), nullable=False)
    
    # Quantity details
    opening_quantity = db.Column(db.Float, nullable=False)
    received_quantity = db.Column(db.Float, default=0)
    consumed_quantity = db.Column(db.Float, default=0)
    waste_quantity = db.Column(db.Float, default=0)
    adjusted_quantity = db.Column(db.Float, default=0)
    closing_quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    
    # Value details
    unit_cost = db.Column(db.Float)
    total_value = db.Column(db.Float)
    
    # Status
    status = db.Column(db.String(20))  # normal, low_stock, out_of_stock, expiring_soon
    
    # Relationships
    report = db.relationship("DailyStockReport", back_populates="items")
    raw_material = db.relationship("RawMaterial")
