"""
Subscription Models for StockMaster Pro
These models handle the multi-tenant subscription system
"""

from datetime import datetime, timedelta
from .db_setup import db
from sqlalchemy.ext.hybrid import hybrid_property
from .models import Shop  # Import Shop model to avoid duplication

class SubscriptionPlan(db.Model):
    """
    SubscriptionPlan model defines the different subscription plans available.
    """
    __tablename__ = 'subscription_plans'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price_monthly = db.Column(db.Float, nullable=False)
    price_yearly = db.Column(db.Float, nullable=False)

    # Plan tiers and features
    tier = db.Column(db.String(20), default='basic')  # 'basic', 'standard', 'premium', 'enterprise'
    features = db.Column(db.JSON)  # JSON field to store plan features

    # Resource limits
    max_branches = db.Column(db.Integer, default=1)
    max_users = db.Column(db.Integer, default=5)
    max_products = db.Column(db.Integer, default=100)
    max_monthly_orders = db.Column(db.Integer, default=1000)
    max_storage_gb = db.Column(db.Float, default=1.0)

    # Feature flags
    has_pos = db.Column(db.Boolean, default=True)
    has_inventory = db.Column(db.Boolean, default=True)
    has_reports = db.Column(db.Boolean, default=True)
    has_marketing = db.Column(db.Boolean, default=False)
    has_api_access = db.Column(db.Boolean, default=False)
    has_advanced_analytics = db.Column(db.Boolean, default=False)
    has_ai_features = db.Column(db.Boolean, default=False)
    has_white_label = db.Column(db.Boolean, default=False)
    has_custom_domain = db.Column(db.Boolean, default=False)
    has_priority_support = db.Column(db.Boolean, default=False)

    # Plan metadata
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)  # Whether plan is publicly visible
    sort_order = db.Column(db.Integer, default=0)  # For ordering plans in UI
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Promotional
    has_trial = db.Column(db.Boolean, default=True)  # Whether plan offers a trial
    trial_days = db.Column(db.Integer, default=7)  # Length of trial in days
    discount_percentage = db.Column(db.Float, default=0)  # Discount percentage if any

    # Relationships
    subscriptions = db.relationship("Subscription", back_populates="plan")

    def __repr__(self):
        return f'<SubscriptionPlan {self.name}>'

class Subscription(db.Model):
    """
    Subscription model tracks a shop's subscription status.
    """
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)

    # Subscription dates
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    trial_end_date = db.Column(db.DateTime)  # When trial period ends
    canceled_at = db.Column(db.DateTime)  # When subscription was canceled

    # Billing information
    billing_cycle = db.Column(db.String(10), default='monthly')  # 'monthly' or 'yearly'
    auto_renew = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    payment_status = db.Column(db.String(20), default='pending')  # 'pending', 'paid', 'failed', 'trial'
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)

    # Payment gateway information
    payment_gateway = db.Column(db.String(50))  # 'stripe', 'tap', 'hyperpay', 'manual'
    gateway_customer_id = db.Column(db.String(255))  # Customer ID in payment gateway
    gateway_subscription_id = db.Column(db.String(255))  # Subscription ID in payment gateway

    # Subscription status
    status = db.Column(db.String(20), default='active')  # 'active', 'trial', 'past_due', 'canceled', 'expired'
    is_in_grace_period = db.Column(db.Boolean, default=False)  # Whether in grace period after failed payment
    grace_period_end_date = db.Column(db.DateTime)  # When grace period ends

    # Subscription metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    cancellation_reason = db.Column(db.String(255))  # Reason for cancellation
    notes = db.Column(db.Text)  # Admin notes

    # Relationships
    shop = db.relationship("Shop", back_populates="subscription")
    plan = db.relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = db.relationship("SubscriptionPayment", back_populates="subscription")

    def __repr__(self):
        return f'<Subscription {self.id} - Shop: {self.shop_id}>'

    @hybrid_property
    def is_expired(self):
        """Check if the subscription is expired"""
        return self.end_date < datetime.utcnow()

    @hybrid_property
    def days_remaining(self):
        """Calculate days remaining in the subscription"""
        if self.is_expired:
            return 0
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)

    @hybrid_property
    def status(self):
        """Get the subscription status"""
        if not self.is_active:
            return "inactive"
        if self.is_expired:
            return "expired"
        if self.days_remaining <= 7:
            return "expiring_soon"
        return "active"

    def activate(self, duration_months=1):
        """Activate the subscription for a specified duration"""
        self.is_active = True
        self.start_date = datetime.utcnow()

        # Calculate end date based on billing cycle
        if self.billing_cycle == 'yearly':
            self.end_date = self.start_date + timedelta(days=365)
        else:  # monthly
            self.end_date = self.start_date + timedelta(days=30 * duration_months)

        # Set next payment date
        self.next_payment_date = self.end_date

        return self

    def deactivate(self):
        """Deactivate the subscription"""
        self.is_active = False
        return self

    def renew(self, duration_months=1):
        """Renew the subscription for a specified duration"""
        # If subscription is expired, start from now
        if self.is_expired:
            self.start_date = datetime.utcnow()
        else:
            # If not expired, extend from the current end date
            self.start_date = self.end_date

        # Calculate new end date
        if self.billing_cycle == 'yearly':
            self.end_date = self.start_date + timedelta(days=365)
        else:  # monthly
            self.end_date = self.start_date + timedelta(days=30 * duration_months)

        self.is_active = True
        self.next_payment_date = self.end_date

        return self

class SubscriptionPayment(db.Model):
    """
    SubscriptionPayment model tracks payments for subscriptions.
    """
    __tablename__ = 'subscription_payments'
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))  # 'credit_card', 'bank_transfer', 'manual', etc.
    transaction_id = db.Column(db.String(100))  # External payment gateway transaction ID
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed', 'refunded'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subscription = db.relationship("Subscription", back_populates="payments")

    def __repr__(self):
        return f'<SubscriptionPayment {self.id} - Amount: {self.amount}>'

class SubscriptionInvoice(db.Model):
    """
    SubscriptionInvoice model for generating invoices for subscription payments.
    """
    __tablename__ = 'subscription_invoices'
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey('subscription_payments.id'))
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    amount = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='unpaid')  # 'unpaid', 'paid', 'overdue', 'cancelled'
    pdf_path = db.Column(db.String(255))  # Path to generated PDF invoice
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subscription = db.relationship("Subscription")
    payment = db.relationship("SubscriptionPayment")

    def __repr__(self):
        return f'<SubscriptionInvoice {self.invoice_number}>'
