"""
Manual Payment Gateway for StockMaster Pro
Handles manual subscription management and payment processing
"""

from datetime import datetime, timedelta
from flask import current_app
from backend.database.db_setup import db
from backend.database.subscription_models import Subscription, SubscriptionPayment, SubscriptionInvoice
import uuid

class ManualGateway:
    """
    Manual Payment Gateway
    Handles subscription management and payment processing for manual payments
    """
    
    @staticmethod
    def create_customer(shop):
        """
        Create a customer record for a shop (no-op for manual gateway)
        
        Args:
            shop: Shop model instance
            
        Returns:
            str: Customer ID (generated UUID)
        """
        customer_id = f"manual_{uuid.uuid4().hex}"
        return customer_id
    
    @staticmethod
    def create_subscription(shop, subscription, payment_method_id=None):
        """
        Create a subscription record
        
        Args:
            shop: Shop model instance
            subscription: Subscription model instance
            payment_method_id: Not used for manual gateway
            
        Returns:
            dict: Subscription details
        """
        try:
            # Generate a subscription ID
            subscription_id = f"manual_{uuid.uuid4().hex}"
            
            # Update subscription with manual subscription ID
            subscription.gateway_subscription_id = subscription_id
            subscription.payment_gateway = 'manual'
            subscription.status = 'pending' if not subscription.trial_end_date else 'trial'
            
            # Create an invoice
            invoice = SubscriptionInvoice(
                subscription_id=subscription.id,
                invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                issue_date=datetime.now(),
                due_date=datetime.now() + timedelta(days=7),
                amount=subscription.plan.price_monthly if subscription.billing_cycle == 'monthly' else subscription.plan.price_yearly,
                tax_amount=0,  # Tax can be calculated based on shop's country/region
                total_amount=subscription.plan.price_monthly if subscription.billing_cycle == 'monthly' else subscription.plan.price_yearly,
                status='unpaid'
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            return {
                'subscription_id': subscription_id,
                'invoice_id': invoice.id,
                'status': subscription.status,
                'bank_details': {
                    'bank_name': 'Saudi National Bank',
                    'account_name': 'StockMaster Pro LLC',
                    'account_number': '1234567890',
                    'iban': 'SA0380000000001234567890',
                    'reference': f"SUB-{subscription.id}"
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"Manual subscription creation error: {str(e)}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription, at_period_end=True):
        """
        Cancel a subscription
        
        Args:
            subscription: Subscription model instance
            at_period_end: Whether to cancel at the end of the billing period
            
        Returns:
            bool: Success status
        """
        try:
            # Update subscription status
            subscription.status = 'canceled' if not at_period_end else 'active'
            subscription.canceled_at = datetime.now()
            db.session.commit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Manual subscription cancellation error: {str(e)}")
            return False
    
    @staticmethod
    def update_subscription(subscription, new_plan=None, new_payment_method=None):
        """
        Update a subscription
        
        Args:
            subscription: Subscription model instance
            new_plan: New SubscriptionPlan model instance
            new_payment_method: Not used for manual gateway
            
        Returns:
            bool: Success status
        """
        try:
            # Update plan if provided
            if new_plan:
                subscription.plan_id = new_plan.id
                
                # Create a new invoice for the plan change
                invoice = SubscriptionInvoice(
                    subscription_id=subscription.id,
                    invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                    issue_date=datetime.now(),
                    due_date=datetime.now() + timedelta(days=7),
                    amount=new_plan.price_monthly if subscription.billing_cycle == 'monthly' else new_plan.price_yearly,
                    tax_amount=0,
                    total_amount=new_plan.price_monthly if subscription.billing_cycle == 'monthly' else new_plan.price_yearly,
                    status='unpaid'
                )
                
                db.session.add(invoice)
            
            db.session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Manual subscription update error: {str(e)}")
            return False
    
    @staticmethod
    def record_payment(subscription, amount, payment_method='bank_transfer', transaction_id=None, notes=None):
        """
        Record a manual payment
        
        Args:
            subscription: Subscription model instance
            amount: Payment amount
            payment_method: Payment method ('bank_transfer', 'cash', etc.)
            transaction_id: External transaction ID
            notes: Payment notes
            
        Returns:
            bool: Success status
        """
        try:
            # Create payment record
            payment = SubscriptionPayment(
                subscription_id=subscription.id,
                amount=amount,
                payment_date=datetime.now(),
                payment_method=payment_method,
                transaction_id=transaction_id or f"MANUAL-{uuid.uuid4().hex[:8]}",
                status='completed',
                notes=notes or 'Manual payment'
            )
            
            # Update subscription status
            subscription.payment_status = 'paid'
            subscription.last_payment_date = datetime.now()
            subscription.status = 'active'
            subscription.is_in_grace_period = False
            
            # Update invoice status
            invoice = SubscriptionInvoice.query.filter_by(
                subscription_id=subscription.id,
                status='unpaid'
            ).order_by(SubscriptionInvoice.issue_date.desc()).first()
            
            if invoice:
                invoice.status = 'paid'
                invoice.payment_id = payment.id
            
            db.session.add(payment)
            db.session.commit()
            
            return True
        except Exception as e:
            current_app.logger.error(f"Manual payment recording error: {str(e)}")
            return False
