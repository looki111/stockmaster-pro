"""
Stripe Payment Gateway Integration for StockMaster Pro
Handles subscription creation, management, and payment processing
"""

import os
import stripe
from datetime import datetime, timedelta
from flask import current_app, url_for
from backend.database.db_setup import db
from backend.database.subscription_models import Subscription, SubscriptionPayment, SubscriptionInvoice

# Initialize Stripe with API key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = '2023-10-16'  # Use the latest stable API version

class StripeGateway:
    """
    Stripe Payment Gateway Integration
    Handles subscription creation, management, and payment processing
    """
    
    @staticmethod
    def create_customer(shop):
        """
        Create a Stripe customer for a shop
        
        Args:
            shop: Shop model instance
            
        Returns:
            str: Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=shop.email,
                name=shop.name,
                phone=shop.phone,
                metadata={
                    'shop_id': shop.id,
                    'owner_name': shop.owner_name
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe customer creation error: {str(e)}")
            raise
    
    @staticmethod
    def create_subscription(shop, subscription, payment_method_id=None):
        """
        Create a Stripe subscription for a shop
        
        Args:
            shop: Shop model instance
            subscription: Subscription model instance
            payment_method_id: Stripe payment method ID
            
        Returns:
            str: Stripe subscription ID
        """
        try:
            # Ensure shop has a Stripe customer ID
            if not shop.stripe_customer_id:
                customer_id = StripeGateway.create_customer(shop)
                shop.stripe_customer_id = customer_id
                db.session.commit()
            else:
                customer_id = shop.stripe_customer_id
            
            # Attach payment method to customer if provided
            if payment_method_id:
                stripe.PaymentMethod.attach(
                    payment_method_id,
                    customer=customer_id
                )
                
                # Set as default payment method
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={
                        'default_payment_method': payment_method_id
                    }
                )
            
            # Create subscription
            stripe_subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[
                    {
                        'price': subscription.plan.stripe_price_id,
                    },
                ],
                metadata={
                    'shop_id': shop.id,
                    'subscription_id': subscription.id,
                    'plan_name': subscription.plan.name
                },
                trial_end=int(subscription.trial_end_date.timestamp()) if subscription.trial_end_date else 'now',
                billing_cycle_anchor='now',
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
                collection_method='charge_automatically'
            )
            
            # Update subscription with Stripe subscription ID
            subscription.gateway_subscription_id = stripe_subscription.id
            subscription.status = 'active' if not subscription.trial_end_date else 'trial'
            db.session.commit()
            
            return {
                'subscription_id': stripe_subscription.id,
                'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret if stripe_subscription.latest_invoice.payment_intent else None,
                'status': stripe_subscription.status
            }
            
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe subscription creation error: {str(e)}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription, at_period_end=True):
        """
        Cancel a Stripe subscription
        
        Args:
            subscription: Subscription model instance
            at_period_end: Whether to cancel at the end of the billing period
            
        Returns:
            bool: Success status
        """
        try:
            if not subscription.gateway_subscription_id:
                return False
            
            stripe_subscription = stripe.Subscription.modify(
                subscription.gateway_subscription_id,
                cancel_at_period_end=at_period_end
            )
            
            # Update subscription status
            subscription.status = 'canceled' if not at_period_end else 'active'
            subscription.canceled_at = datetime.now()
            db.session.commit()
            
            return True
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe subscription cancellation error: {str(e)}")
            return False
    
    @staticmethod
    def update_subscription(subscription, new_plan=None, new_payment_method=None):
        """
        Update a Stripe subscription
        
        Args:
            subscription: Subscription model instance
            new_plan: New SubscriptionPlan model instance
            new_payment_method: New Stripe payment method ID
            
        Returns:
            bool: Success status
        """
        try:
            if not subscription.gateway_subscription_id:
                return False
            
            update_params = {}
            
            # Update plan if provided
            if new_plan and new_plan.stripe_price_id:
                update_params['items'] = [
                    {
                        'id': stripe.Subscription.retrieve(subscription.gateway_subscription_id)['items']['data'][0].id,
                        'price': new_plan.stripe_price_id
                    }
                ]
                update_params['proration_behavior'] = 'create_prorations'
            
            # Update payment method if provided
            if new_payment_method:
                # Attach payment method to customer
                stripe.PaymentMethod.attach(
                    new_payment_method,
                    customer=subscription.shop.stripe_customer_id
                )
                
                # Set as default payment method
                stripe.Customer.modify(
                    subscription.shop.stripe_customer_id,
                    invoice_settings={
                        'default_payment_method': new_payment_method
                    }
                )
            
            # Update subscription if there are changes
            if update_params:
                stripe_subscription = stripe.Subscription.modify(
                    subscription.gateway_subscription_id,
                    **update_params
                )
                
                # Update subscription in database
                if new_plan:
                    subscription.plan_id = new_plan.id
                
                db.session.commit()
                
                return True
            
            return False
        except stripe.error.StripeError as e:
            current_app.logger.error(f"Stripe subscription update error: {str(e)}")
            return False
    
    @staticmethod
    def handle_webhook_event(payload, signature):
        """
        Handle Stripe webhook events
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            
        Returns:
            dict: Response data
        """
        try:
            # Verify webhook signature
            webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            # Handle different event types
            if event['type'] == 'invoice.payment_succeeded':
                return StripeGateway._handle_payment_succeeded(event)
            elif event['type'] == 'invoice.payment_failed':
                return StripeGateway._handle_payment_failed(event)
            elif event['type'] == 'customer.subscription.updated':
                return StripeGateway._handle_subscription_updated(event)
            elif event['type'] == 'customer.subscription.deleted':
                return StripeGateway._handle_subscription_deleted(event)
            
            return {'success': True, 'message': f"Unhandled event type: {event['type']}"}
            
        except stripe.error.SignatureVerificationError:
            current_app.logger.error("Invalid webhook signature")
            return {'success': False, 'message': 'Invalid signature'}
        except Exception as e:
            current_app.logger.error(f"Webhook error: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _handle_payment_succeeded(event):
        """Handle invoice.payment_succeeded webhook event"""
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        
        # Find subscription in database
        subscription = Subscription.query.filter_by(gateway_subscription_id=subscription_id).first()
        if not subscription:
            return {'success': False, 'message': 'Subscription not found'}
        
        # Create payment record
        payment = SubscriptionPayment(
            subscription_id=subscription.id,
            amount=invoice['amount_paid'] / 100,  # Convert from cents
            payment_date=datetime.fromtimestamp(invoice['created']),
            payment_method='credit_card',
            transaction_id=invoice['payment_intent'],
            status='completed',
            notes=f"Invoice {invoice['number']}"
        )
        
        # Update subscription status
        subscription.payment_status = 'paid'
        subscription.last_payment_date = datetime.fromtimestamp(invoice['created'])
        subscription.status = 'active'
        subscription.is_in_grace_period = False
        
        # Create invoice record
        invoice_record = SubscriptionInvoice(
            subscription_id=subscription.id,
            payment_id=payment.id,
            invoice_number=invoice['number'],
            issue_date=datetime.fromtimestamp(invoice['created']),
            due_date=datetime.fromtimestamp(invoice['due_date']) if invoice['due_date'] else None,
            amount=invoice['subtotal'] / 100,
            tax_amount=invoice['tax'] / 100,
            total_amount=invoice['total'] / 100,
            status='paid'
        )
        
        db.session.add(payment)
        db.session.add(invoice_record)
        db.session.commit()
        
        return {'success': True, 'message': 'Payment recorded successfully'}
    
    @staticmethod
    def _handle_payment_failed(event):
        """Handle invoice.payment_failed webhook event"""
        invoice = event['data']['object']
        subscription_id = invoice['subscription']
        
        # Find subscription in database
        subscription = Subscription.query.filter_by(gateway_subscription_id=subscription_id).first()
        if not subscription:
            return {'success': False, 'message': 'Subscription not found'}
        
        # Create payment record
        payment = SubscriptionPayment(
            subscription_id=subscription.id,
            amount=invoice['amount_due'] / 100,  # Convert from cents
            payment_date=datetime.fromtimestamp(invoice['created']),
            payment_method='credit_card',
            transaction_id=invoice['payment_intent'],
            status='failed',
            notes=f"Invoice {invoice['number']} - {invoice['billing_reason']}"
        )
        
        # Update subscription status
        subscription.payment_status = 'failed'
        subscription.status = 'past_due'
        
        # Set grace period (7 days)
        subscription.is_in_grace_period = True
        subscription.grace_period_end_date = datetime.now() + timedelta(days=7)
        
        db.session.add(payment)
        db.session.commit()
        
        return {'success': True, 'message': 'Failed payment recorded'}
    
    @staticmethod
    def _handle_subscription_updated(event):
        """Handle customer.subscription.updated webhook event"""
        stripe_subscription = event['data']['object']
        
        # Find subscription in database
        subscription = Subscription.query.filter_by(gateway_subscription_id=stripe_subscription['id']).first()
        if not subscription:
            return {'success': False, 'message': 'Subscription not found'}
        
        # Update subscription status
        subscription.status = stripe_subscription['status']
        
        # Update subscription dates
        if stripe_subscription['current_period_end']:
            subscription.end_date = datetime.fromtimestamp(stripe_subscription['current_period_end'])
        
        if stripe_subscription['current_period_start']:
            subscription.start_date = datetime.fromtimestamp(stripe_subscription['current_period_start'])
        
        if stripe_subscription['trial_end']:
            subscription.trial_end_date = datetime.fromtimestamp(stripe_subscription['trial_end'])
        
        db.session.commit()
        
        return {'success': True, 'message': 'Subscription updated'}
    
    @staticmethod
    def _handle_subscription_deleted(event):
        """Handle customer.subscription.deleted webhook event"""
        stripe_subscription = event['data']['object']
        
        # Find subscription in database
        subscription = Subscription.query.filter_by(gateway_subscription_id=stripe_subscription['id']).first()
        if not subscription:
            return {'success': False, 'message': 'Subscription not found'}
        
        # Update subscription status
        subscription.status = 'canceled'
        subscription.is_active = False
        subscription.canceled_at = datetime.now()
        
        db.session.commit()
        
        return {'success': True, 'message': 'Subscription canceled'}
