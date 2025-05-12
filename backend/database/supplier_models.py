"""
Supplier Models for StockMaster Pro
"""

from datetime import datetime
from .db_setup import db

class Supplier(db.Model):
    """
    Supplier model for tracking suppliers of raw materials
    """
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Foreign keys
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('SupplierOrder', back_populates='supplier', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Supplier {self.name}>'

class SupplierOrder(db.Model):
    """
    Supplier Order model for tracking orders from suppliers
    """
    __tablename__ = 'supplier_orders'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, cancelled
    notes = db.Column(db.Text)
    
    # Payment details
    total_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partial, paid
    payment_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = db.relationship('Supplier', back_populates='orders')
    items = db.relationship('SupplierOrderItem', back_populates='order', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SupplierOrder {self.id} - {self.supplier.name}>'

class SupplierOrderItem(db.Model):
    """
    Supplier Order Item model for tracking items in supplier orders
    """
    __tablename__ = 'supplier_order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('supplier_orders.id'), nullable=False)
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = db.relationship('SupplierOrder', back_populates='items')
    raw_material = db.relationship('RawMaterial')
    
    def __repr__(self):
        return f'<SupplierOrderItem {self.id} - {self.raw_material.name}>'
