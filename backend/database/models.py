from flask_login import UserMixin
from datetime import datetime
from .db_setup import db
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property

# Association table for role-permission relationship
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True)
)

# Association table for user-role relationship
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

class Shop(db.Model):
    __tablename__ = 'shops'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=True)  # Made nullable to avoid errors
    email = db.Column(db.String(120), unique=True, nullable=True)  # Made nullable to avoid errors
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    logo = db.Column(db.String(255))  # Path to logo file
    
    # Branding and customization
    primary_color = db.Column(db.String(20), default="#4A90E2")
    secondary_color = db.Column(db.String(20), default="#FFA726")
    accent_color = db.Column(db.String(20), default="#4CAF50")
    font_family = db.Column(db.String(100), default="'Cairo', sans-serif") 
    custom_domain = db.Column(db.String(255))
    
    # Business details
    business_type = db.Column(db.String(50), default="coffee_shop")  # Type of business
    tax_number = db.Column(db.String(50))  # Tax registration number
    currency = db.Column(db.String(10), default="SAR")  # Default currency
    timezone = db.Column(db.String(50), default="Asia/Riyadh")  # Timezone
    
    # Contact and social
    website = db.Column(db.String(255))  # Website URL
    social_facebook = db.Column(db.String(255))  # Facebook page
    social_instagram = db.Column(db.String(255))  # Instagram handle
    social_twitter = db.Column(db.String(255))  # Twitter handle
    
    # System settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    onboarding_completed = db.Column(db.Boolean, default=False)  # Whether onboarding is complete
    referral_code = db.Column(db.String(20))  # Unique referral code
    referred_by = db.Column(db.Integer, db.ForeignKey('shops.id'))  # Shop that referred this one
    
    # Relationships
    branches = db.relationship("Branch", back_populates="shop")
    subscription = db.relationship("Subscription", back_populates="shop", uselist=False)
    
    def __repr__(self):
        return f'<Shop {self.name}>'
    
    @hybrid_property
    def has_active_subscription(self):
        """Check if the shop has an active subscription"""
        if not self.subscription:
            return False
        return self.subscription.is_active and self.subscription.end_date > datetime.utcnow()

class Branch(db.Model):
    __tablename__ = 'branches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    is_main = db.Column(db.Boolean, default=False)  # Whether this is the main branch
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))  # Foreign key to Shop model

    # Branch details
    manager_name = db.Column(db.String(100))
    opening_hours = db.Column(db.String(100))  # e.g., "9:00-22:00"
    location_lat = db.Column(db.Float)  # Latitude for maps
    location_lng = db.Column(db.Float)  # Longitude for maps
    description = db.Column(db.Text)
    image = db.Column(db.String(255))  # Path to branch image

    # Customization Settings
    weight_unit = db.Column(db.String(10), default='kg')  # kg/g
    time_format = db.Column(db.String(10), default='24')  # 12/24
    invoice_template = db.Column(db.String(50), default='default')
    invoice_fields = db.Column(db.JSON)  # Custom invoice fields
    order_types = db.Column(db.JSON)     # Available order types
    tax_rate = db.Column(db.Float, default=15.0)  # Default tax rate (%)

    # Operational Settings
    pos_printer = db.Column(db.String(100))  # POS printer settings
    barcode_printer = db.Column(db.String(100))  # Barcode printer settings
    pos_hardware = db.Column(db.JSON)  # POS hardware integration settings
    quick_pos_mode = db.Column(db.Boolean, default=False)
    shift_closing_time = db.Column(db.Time)
    inventory_sync = db.Column(db.Boolean, default=True)  # Whether to sync inventory with other branches

    # Integration Settings
    whatsapp_api = db.Column(db.String(200))  # WhatsApp API key
    sms_api = db.Column(db.String(200))      # SMS API key
    marketing_enabled = db.Column(db.Boolean, default=False)
    pos_integration = db.Column(db.String(50))  # External POS integration type
    accounting_integration = db.Column(db.String(50))  # Accounting software integration

    # AI Settings
    ai_analytics_enabled = db.Column(db.Boolean, default=False)
    sales_prediction_enabled = db.Column(db.Boolean, default=False)
    inventory_prediction_enabled = db.Column(db.Boolean, default=False)
    customer_insights_enabled = db.Column(db.Boolean, default=False)

    # Status tracking
    last_inventory_count = db.Column(db.DateTime)
    last_backup = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    shop = db.relationship("Shop", back_populates="branches")
    users = db.relationship("User", back_populates="branch")
    products = db.relationship("Product", back_populates="branch")
    orders = db.relationship("Order", back_populates="branch")
    shifts = db.relationship("Shift", back_populates="branch")
    clients = db.relationship("Client", back_populates="branch")

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True)
    coffee_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    preferred_language = db.Column(db.String(2), default='ar')
    theme = db.Column(db.String(10), default='light')
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    
    # Relationships
    branch = db.relationship('Branch', back_populates='users')
    roles = db.relationship('Role', secondary=user_roles, back_populates='users')
    notifications = db.relationship('Notification', back_populates='user', lazy=True)
    activity_logs = db.relationship('ActivityLog', back_populates='user')
    products = db.relationship('Product', back_populates='user')
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True if self.is_active else False
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission_name):
        if not self.is_active:
            return False
        return any(permission.name == permission_name for role in self.roles for permission in role.permissions)
    
    def has_module_permission(self, module_name):
        if not self.is_active:
            return False
        return any(permission.module == module_name for role in self.roles for permission in role.permissions)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))

    # Product details
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    image = db.Column(db.String(255))  # Path to image
    barcode = db.Column(db.String(100))
    sku = db.Column(db.String(50))  # Stock Keeping Unit

    # Pricing
    cost_price = db.Column(db.Float)  # Cost to make the product
    tax_rate = db.Column(db.Float)  # Product-specific tax rate
    discount_price = db.Column(db.Float)  # Discounted price if any

    # Inventory management
    alert_threshold = db.Column(db.Float, default=5)  # Low stock threshold
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)

    # Product variants and options
    has_variants = db.Column(db.Boolean, default=False)
    variants = db.Column(db.JSON)  # JSON array of variant options
    options = db.Column(db.JSON)  # JSON array of customization options

    # Preparation time in minutes
    preparation_time = db.Column(db.Integer)

    # Nutritional information
    calories = db.Column(db.Integer)
    nutritional_info = db.Column(db.JSON)  # JSON object with nutritional details

    # Allergens and dietary info
    allergens = db.Column(db.JSON)  # JSON array of allergens
    dietary_info = db.Column(db.JSON)  # JSON object with dietary flags (vegan, etc.)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="products")
    branch = db.relationship("Branch", back_populates="products")

    @property
    def is_low_stock(self):
        """Check if product is low on stock"""
        return self.quantity <= self.alert_threshold

    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if not self.cost_price or self.cost_price == 0:
            return None
        return ((self.price - self.cost_price) / self.price) * 100

    @property
    def current_price(self):
        """Get the current price (considering discounts)"""
        if self.discount_price and self.discount_price > 0:
            return self.discount_price
        return self.price

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    product = db.relationship("Product")
    user = db.relationship("User")

class RawMaterial(db.Model):
    __tablename__ = 'raw_materials'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=0)
    alert_threshold = db.Column(db.Float, nullable=False, default=0)

    # Enhanced inventory tracking
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

    # Cost and pricing
    cost_price = db.Column(db.Float)
    average_cost = db.Column(db.Float)  # Weighted average cost
    last_purchase_price = db.Column(db.Float)

    # Dates and tracking
    last_purchase_date = db.Column(db.DateTime)
    expiry_date = db.Column(db.DateTime)
    manufacturing_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Storage and location
    storage_location = db.Column(db.String(100))  # e.g., "Shelf A-3"
    barcode = db.Column(db.String(100))
    sku = db.Column(db.String(50))  # Stock Keeping Unit

    # Consumption metrics
    daily_usage_rate = db.Column(db.Float)  # Average daily consumption
    reorder_point = db.Column(db.Float)  # When to reorder (may differ from alert_threshold)
    reorder_quantity = db.Column(db.Float)  # How much to order when reordering

    # Waste tracking
    waste_percentage = db.Column(db.Float, default=0)  # Historical waste percentage

    # Status
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='in_stock')  # in_stock, low_stock, out_of_stock, discontinued

    # Additional info
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    image = db.Column(db.String(255))  # Path to image
    category = db.Column(db.String(50))  # e.g., "Coffee Beans", "Milk", "Syrups"

    # Relationships
    vendor = db.relationship("Vendor", back_populates="raw_materials")
    branch = db.relationship("Branch", backref="raw_materials")

    @property
    def days_until_expiry(self):
        """Calculate days until expiry"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.utcnow()
        return delta.days

    @property
    def is_expiring_soon(self):
        """Check if item is expiring within 7 days"""
        if not self.days_until_expiry:
            return False
        return 0 < self.days_until_expiry <= 7

    @property
    def is_expired(self):
        """Check if item is expired"""
        if not self.days_until_expiry:
            return False
        return self.days_until_expiry <= 0

    @property
    def stock_value(self):
        """Calculate current stock value"""
        if self.average_cost:
            return self.quantity * self.average_cost
        elif self.cost_price:
            return self.quantity * self.cost_price
        return 0

class Recipe(db.Model):
    """
    Legacy Recipe model - use ConsumptionRule for new implementations
    This model is kept for backward compatibility
    """
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    raw_material_id = db.Column(db.Integer, db.ForeignKey('raw_materials.id'))
    amount = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='g')  # Unit of measurement

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    product = db.relationship("Product", backref="recipes")
    raw_material = db.relationship("RawMaterial", backref="recipes")

    def to_consumption_rule(self):
        """Convert this recipe to a ConsumptionRule"""
        from .inventory_models import ConsumptionRule

        return ConsumptionRule(
            product_id=self.product_id,
            raw_material_id=self.raw_material_id,
            quantity=self.amount,
            unit=self.unit,
            waste_factor=0.0,
            is_active=self.is_active
        )

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True)
    customer_name = db.Column(db.String(100))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    subtotal = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)

    # Order details
    order_type = db.Column(db.String(20), default='dine_in')  # dine_in, takeaway, delivery
    table_number = db.Column(db.String(20))  # For dine-in orders
    delivery_address = db.Column(db.Text)  # For delivery orders

    # Discounts
    discount_amount = db.Column(db.Float, default=0)
    discount_type = db.Column(db.String(20))  # percentage, fixed
    discount_reason = db.Column(db.String(100))

    # Loyalty
    loyalty_points_earned = db.Column(db.Integer, default=0)
    loyalty_points_used = db.Column(db.Integer, default=0)

    # Status and tracking
    status = db.Column(db.String(20), default='completed')  # pending, processing, completed, cancelled
    preparation_status = db.Column(db.String(20), default='ready')  # preparing, ready, delivered
    preparation_time = db.Column(db.Integer)  # Estimated preparation time in minutes

    # Inventory tracking
    inventory_processed = db.Column(db.Boolean, default=False)  # Whether inventory has been deducted

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # User and branch
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))

    # Additional info
    notes = db.Column(db.Text)

    # Relationships
    items = db.relationship('OrderItem', back_populates='order')
    client = db.relationship('Client', back_populates='orders')
    branch = db.relationship('Branch', back_populates='orders')

    @property
    def is_completed(self):
        """Check if order is completed"""
        return self.status == 'completed'

    @property
    def is_cancelled(self):
        """Check if order is cancelled"""
        return self.status == 'cancelled'

    def process_inventory(self, user_id):
        """Process inventory consumption for this order"""
        from controllers.inventory_controller import InventoryController

        if not self.inventory_processed:
            result = InventoryController.process_inventory_consumption(self.id, user_id)
            if result.get('success'):
                self.inventory_processed = True
                return result

        return {'success': False, 'error': 'Inventory already processed'}

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    # Variant and customization
    variant = db.Column(db.String(50))  # e.g., "Large", "Medium", "Small"
    options = db.Column(db.JSON)  # JSON array of selected options

    # Discounts
    discount_amount = db.Column(db.Float, default=0)
    discount_type = db.Column(db.String(20))  # percentage, fixed

    # Notes
    notes = db.Column(db.Text)  # Special instructions

    # Inventory tracking
    inventory_processed = db.Column(db.Boolean, default=False)  # Whether inventory has been deducted

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product')

    @property
    def has_variant(self):
        """Check if item has a variant"""
        return bool(self.variant)

    @property
    def has_options(self):
        """Check if item has options"""
        return bool(self.options and len(self.options) > 0)

    @property
    def has_discount(self):
        """Check if item has a discount"""
        return self.discount_amount > 0

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='notifications')

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    loyalty_points = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    branch = db.relationship('Branch', back_populates='clients')
    orders = db.relationship('Order', back_populates='client')

    def __repr__(self):
        return f'<Client {self.name}>'

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    payment_terms = db.Column(db.String(100))
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    raw_materials = db.relationship("RawMaterial", back_populates="vendor")

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))

    user = db.relationship('User', back_populates='activity_logs')

class Promotion(db.Model):
    __tablename__ = 'promotions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20))  # percentage, fixed_amount
    discount_value = db.Column(db.Float)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    min_purchase = db.Column(db.Float)
    max_discount = db.Column(db.Float)
    applicable_products = db.Column(db.Text)  # JSON string of product IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    initial_cash = db.Column(db.Float, default=0)
    final_cash = db.Column(db.Float)
    total_sales = db.Column(db.Float, default=0)
    total_orders = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active/closed

    branch = db.relationship("Branch", back_populates="shifts")
    user = db.relationship("User")

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # inventory/order/system
    status = db.Column(db.String(20), default='open')  # open/in_progress/closed
    priority = db.Column(db.String(20), default='medium')  # low/medium/high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User")
    branch = db.relationship("Branch")
    responses = db.relationship("TicketResponse", back_populates="ticket")

class TicketResponse(db.Model):
    __tablename__ = 'ticket_responses'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship("SupportTicket", back_populates="responses")
    user = db.relationship("User")

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    tags = db.Column(db.JSON)
    views = db.Column(db.Integer, default=0)
    helpful_votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class AIPrediction(db.Model):
    __tablename__ = 'ai_predictions'
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    type = db.Column(db.String(50))  # sales/inventory
    target_id = db.Column(db.Integer)  # product_id or time_slot
    prediction = db.Column(db.Float)
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    branch = db.relationship("Branch")

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    module = db.Column(db.String(50))  # e.g., 'inventory', 'sales', 'reports'
    action = db.Column(db.String(50))  # e.g., 'create', 'read', 'update', 'delete'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship('Role', secondary=role_permissions, back_populates='permissions')

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_system = db.Column(db.Boolean, default=False)  # System roles cannot be deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))  # If role is branch-specific

    permissions = db.relationship('Permission', secondary=role_permissions, back_populates='roles')
    users = db.relationship('User', secondary=user_roles, back_populates='roles')
    branch = db.relationship('Branch')

class UserPreference(db.Model):
    """User Preferences Model"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(255))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('preferences', lazy=True))
    
    # Indexes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'key', name='_user_preference_uc'),
    )
    
    def __repr__(self):
        return f"<UserPreference {self.key}={self.value} (user_id={self.user_id})>"
