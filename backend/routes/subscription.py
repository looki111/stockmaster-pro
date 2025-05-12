"""
Subscription Management Routes for StockMaster Pro
Handles subscription creation, management, and payment processing
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from database.db_setup import db
from database.subscription_models import (
    Shop, SubscriptionPlan, Subscription, SubscriptionPayment, SubscriptionInvoice
)
from database.models import User, Branch
from auth import role_required
from werkzeug.security import generate_password_hash
import uuid
import os

# Blueprint setup
subscription_bp = Blueprint('subscription', __name__, url_prefix='/subscription')

# Admin routes for subscription management
@subscription_bp.route('/admin/shops', methods=['GET'])
@login_required
@role_required('admin')
def admin_shops():
    """Admin view of all shops and their subscription status"""
    shops = Shop.query.all()
    return render_template('subscription/admin_shops.html', shops=shops)

@subscription_bp.route('/admin/shop/<int:shop_id>', methods=['GET'])
@login_required
@role_required('admin')
def admin_shop_detail(shop_id):
    """Admin view of a specific shop's details"""
    shop = Shop.query.get_or_404(shop_id)
    branches = Branch.query.filter_by(shop_id=shop_id).all()
    users = User.query.join(Branch).filter(Branch.shop_id == shop_id).all()

    return render_template('subscription/admin_shop_detail.html',
                          shop=shop,
                          branches=branches,
                          users=users)

@subscription_bp.route('/admin/plans', methods=['GET'])
@login_required
@role_required('admin')
def admin_plans():
    """Admin view of all subscription plans"""
    plans = SubscriptionPlan.query.all()
    return render_template('subscription/admin_plans.html', plans=plans)

@subscription_bp.route('/admin/plan/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_create_plan():
    """Create a new subscription plan"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price_monthly = float(request.form.get('price_monthly'))
        price_yearly = float(request.form.get('price_yearly'))
        max_branches = int(request.form.get('max_branches'))
        max_users = int(request.form.get('max_users'))
        max_products = int(request.form.get('max_products'))

        # Create features JSON
        features = {
            'max_branches': max_branches,
            'max_users': max_users,
            'max_products': max_products,
            'pos': request.form.get('feature_pos') == 'on',
            'inventory': request.form.get('feature_inventory') == 'on',
            'reports': request.form.get('feature_reports') == 'on',
            'marketing': request.form.get('feature_marketing') == 'on',
            'ai': request.form.get('feature_ai') == 'on',
            'api': request.form.get('feature_api') == 'on',
        }

        plan = SubscriptionPlan(
            name=name,
            description=description,
            price_monthly=price_monthly,
            price_yearly=price_yearly,
            features=features,
            max_branches=max_branches,
            max_users=max_users,
            max_products=max_products,
            is_active=True
        )

        db.session.add(plan)
        db.session.commit()

        flash('Subscription plan created successfully', 'success')
        return redirect(url_for('subscription.admin_plans'))

    return render_template('subscription/admin_create_plan.html')

@subscription_bp.route('/admin/plan/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_edit_plan(plan_id):
    """Edit an existing subscription plan"""
    plan = SubscriptionPlan.query.get_or_404(plan_id)

    if request.method == 'POST':
        plan.name = request.form.get('name')
        plan.description = request.form.get('description')
        plan.price_monthly = float(request.form.get('price_monthly'))
        plan.price_yearly = float(request.form.get('price_yearly'))
        plan.max_branches = int(request.form.get('max_branches'))
        plan.max_users = int(request.form.get('max_users'))
        plan.max_products = int(request.form.get('max_products'))
        plan.is_active = request.form.get('is_active') == 'on'

        # Update features JSON
        plan.features = {
            'max_branches': plan.max_branches,
            'max_users': plan.max_users,
            'max_products': plan.max_products,
            'pos': request.form.get('feature_pos') == 'on',
            'inventory': request.form.get('feature_inventory') == 'on',
            'reports': request.form.get('feature_reports') == 'on',
            'marketing': request.form.get('feature_marketing') == 'on',
            'ai': request.form.get('feature_ai') == 'on',
            'api': request.form.get('feature_api') == 'on',
        }

        db.session.commit()

        flash('Subscription plan updated successfully', 'success')
        return redirect(url_for('subscription.admin_plans'))

    return render_template('subscription/admin_edit_plan.html', plan=plan)

@subscription_bp.route('/admin/subscription/<int:subscription_id>/activate', methods=['POST'])
@login_required
@role_required('admin')
def admin_activate_subscription(subscription_id):
    """Manually activate a subscription"""
    subscription = Subscription.query.get_or_404(subscription_id)

    # Get duration from form
    duration_months = int(request.form.get('duration_months', 1))

    # Activate subscription
    subscription.activate(duration_months=duration_months)
    subscription.payment_status = 'paid'
    subscription.last_payment_date = datetime.utcnow()

    # Create payment record
    payment = SubscriptionPayment(
        subscription_id=subscription.id,
        amount=subscription.plan.price_monthly if subscription.billing_cycle == 'monthly' else subscription.plan.price_yearly,
        payment_method='manual',
        status='completed',
        notes=f'Manually activated by admin for {duration_months} months'
    )

    db.session.add(payment)
    db.session.commit()

    flash('Subscription activated successfully', 'success')
    return redirect(url_for('subscription.admin_shop_detail', shop_id=subscription.shop_id))

@subscription_bp.route('/admin/subscription/<int:subscription_id>/deactivate', methods=['POST'])
@login_required
@role_required('admin')
def admin_deactivate_subscription(subscription_id):
    """Manually deactivate a subscription"""
    subscription = Subscription.query.get_or_404(subscription_id)

    # Deactivate subscription
    subscription.deactivate()
    db.session.commit()

    flash('Subscription deactivated successfully', 'success')
    return redirect(url_for('subscription.admin_shop_detail', shop_id=subscription.shop_id))

# Customer-facing subscription routes
@subscription_bp.route('/plans', methods=['GET'])
def plans():
    """Display available subscription plans to customers"""
    active_plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return render_template('subscription/plans.html', plans=active_plans)

@subscription_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new shop with a subscription plan"""
    if request.method == 'POST':
        # Get form data
        shop_name = request.form.get('shop_name')
        owner_name = request.form.get('owner_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        username = request.form.get('username')
        password = request.form.get('password')
        plan_id = int(request.form.get('plan_id'))
        billing_cycle = request.form.get('billing_cycle')

        # Check if email or username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('subscription.register'))

        if Shop.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('subscription.register'))

        # Create shop
        shop = Shop(
            name=shop_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            address=address,
            is_active=True
        )

        db.session.add(shop)
        db.session.flush()  # Get shop ID without committing

        # Create default branch
        branch = Branch(
            name="Main Branch",
            address=address,
            phone=phone,
            shop_id=shop.id,
            is_active=True,
            weight_unit='kg',
            currency='SAR',
            time_format='24',
            invoice_template='default',
            order_types=['dine-in', 'takeaway', 'delivery']
        )

        db.session.add(branch)
        db.session.flush()  # Get branch ID without committing

        # Create admin user for the shop
        user = User(
            username=username,
            password=generate_password_hash(password),
            coffee_name=shop_name,
            email=email,
            branch_id=branch.id,
            is_active=True,
            is_superuser=True  # Shop owner is superuser for their shop
        )

        db.session.add(user)

        # Create subscription
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            flash('Invalid subscription plan', 'error')
            return redirect(url_for('subscription.register'))

        # Set up trial period (7 days)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=7)  # 7-day trial

        subscription = Subscription(
            shop_id=shop.id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            billing_cycle=billing_cycle,
            auto_renew=True,
            is_active=True,
            payment_status='trial',
            next_payment_date=end_date
        )

        db.session.add(subscription)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    # GET request - show registration form
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return render_template('subscription/register.html', plans=plans)

@subscription_bp.route('/status', methods=['GET'])
@login_required
def subscription_status():
    """Show current subscription status to the shop owner"""
    # Get the shop associated with the current user's branch
    if not current_user.branch or not current_user.branch.shop:
        flash('No subscription found', 'error')
        return redirect(url_for('dashboard'))

    shop = current_user.branch.shop
    subscription = shop.subscription

    if not subscription:
        flash('No subscription found', 'error')
        return redirect(url_for('dashboard'))

    # Get payment history
    payments = SubscriptionPayment.query.filter_by(subscription_id=subscription.id).order_by(SubscriptionPayment.payment_date.desc()).all()

    return render_template('subscription/status.html',
                          shop=shop,
                          subscription=subscription,
                          payments=payments)

@subscription_bp.route('/renew', methods=['GET', 'POST'])
@login_required
def renew_subscription():
    """Renew an expired or expiring subscription"""
    # Get the shop associated with the current user's branch
    if not current_user.branch or not current_user.branch.shop:
        flash('No subscription found', 'error')
        return redirect(url_for('dashboard'))

    shop = current_user.branch.shop
    subscription = shop.subscription

    if not subscription:
        flash('No subscription found', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # In a real implementation, this would process payment
        # For now, we'll just create a pending payment and redirect to a payment page

        payment = SubscriptionPayment(
            subscription_id=subscription.id,
            amount=subscription.plan.price_monthly if subscription.billing_cycle == 'monthly' else subscription.plan.price_yearly,
            payment_method='manual',
            status='pending',
            notes='Renewal payment'
        )

        db.session.add(payment)
        db.session.commit()

        # Redirect to payment page (placeholder)
        return redirect(url_for('subscription.payment', payment_id=payment.id))

    return render_template('subscription/renew.html',
                          shop=shop,
                          subscription=subscription)

@subscription_bp.route('/payment/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def payment(payment_id):
    """Process payment for subscription"""
    payment = SubscriptionPayment.query.get_or_404(payment_id)
    subscription = payment.subscription

    # Ensure user has permission to access this payment
    if current_user.branch.shop_id != subscription.shop_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))

    # Get shop
    shop = Shop.query.get(subscription.shop_id)
    if not shop:
        flash('Shop not found', 'error')
        return redirect(url_for('dashboard'))

    # Get available payment gateways
    from utils.payment_gateways import PaymentGatewayFactory
    available_gateways = PaymentGatewayFactory.get_available_gateways()

    if request.method == 'POST':
        payment_method = request.form.get('payment_method', 'manual')

        if payment_method == 'manual':
            # Manual payment process
            payment.status = 'completed'
            payment.transaction_id = f'MANUAL-{uuid.uuid4().hex[:8]}'
            payment.payment_date = datetime.utcnow()
            payment.payment_method = 'manual'

            # Renew subscription
            subscription.renew(duration_months=1 if subscription.billing_cycle == 'monthly' else 12)
            subscription.payment_status = 'paid'
            subscription.last_payment_date = datetime.utcnow()

            db.session.commit()

            # Generate invoice
            from utils.invoice_generator import InvoiceGenerator

            # Create invoice record
            invoice = SubscriptionInvoice(
                subscription_id=subscription.id,
                payment_id=payment.id,
                invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                issue_date=datetime.utcnow(),
                amount=payment.amount,
                tax_amount=0,  # Tax can be calculated based on shop's country/region
                total_amount=payment.amount,
                status='paid'
            )

            db.session.add(invoice)
            db.session.commit()

            # Generate PDF invoice
            try:
                invoice_path = InvoiceGenerator.generate_subscription_invoice(invoice.id)
                invoice.pdf_path = invoice_path
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f"Error generating invoice: {str(e)}")

            # Send payment confirmation notification
            from utils.notification_manager import NotificationManager
            NotificationManager.send_subscription_payment_confirmation(subscription, payment)

            flash('Payment successful! Your subscription has been renewed.', 'success')
            return redirect(url_for('subscription.subscription_status'))
        else:
            # Process payment through payment gateway
            gateway = PaymentGatewayFactory.create_gateway(payment_method)

            # Get payment details from form
            payment_details = {
                'card_number': request.form.get('card_number', '').replace(' ', ''),
                'expiry_date': request.form.get('expiry_date', ''),
                'cvv': request.form.get('cvv', ''),
                'card_holder': request.form.get('card_holder', '')
            }

            try:
                # Process payment through gateway
                if payment_method == 'stripe':
                    # For Stripe, we need to create a payment method first
                    import stripe
                    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

                    # Parse expiry date
                    expiry_parts = payment_details['expiry_date'].split('/')
                    exp_month = int(expiry_parts[0])
                    exp_year = int(f"20{expiry_parts[1]}")

                    # Create payment method
                    payment_method = stripe.PaymentMethod.create(
                        type='card',
                        card={
                            'number': payment_details['card_number'],
                            'exp_month': exp_month,
                            'exp_year': exp_year,
                            'cvc': payment_details['cvv']
                        }
                    )

                    # Update subscription with payment method
                    result = gateway.update_subscription(subscription, new_payment_method=payment_method.id)

                    if result:
                        # Payment successful
                        payment.status = 'completed'
                        payment.transaction_id = payment_method.id
                        payment.payment_date = datetime.utcnow()
                        payment.payment_method = 'credit_card'

                        # Renew subscription
                        subscription.renew(duration_months=1 if subscription.billing_cycle == 'monthly' else 12)
                        subscription.payment_status = 'paid'
                        subscription.last_payment_date = datetime.utcnow()

                        db.session.commit()

                        # Generate invoice and send notification (same as manual payment)
                        invoice = SubscriptionInvoice(
                            subscription_id=subscription.id,
                            payment_id=payment.id,
                            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}",
                            issue_date=datetime.utcnow(),
                            amount=payment.amount,
                            tax_amount=0,
                            total_amount=payment.amount,
                            status='paid'
                        )

                        db.session.add(invoice)
                        db.session.commit()

                        try:
                            from utils.invoice_generator import InvoiceGenerator
                            invoice_path = InvoiceGenerator.generate_subscription_invoice(invoice.id)
                            invoice.pdf_path = invoice_path
                            db.session.commit()
                        except Exception as e:
                            current_app.logger.error(f"Error generating invoice: {str(e)}")

                        from utils.notification_manager import NotificationManager
                        NotificationManager.send_subscription_payment_confirmation(subscription, payment)

                        flash('Payment successful! Your subscription has been renewed.', 'success')
                        return redirect(url_for('subscription.subscription_status'))
                    else:
                        flash('Payment processing failed. Please try again.', 'error')
                else:
                    # For other gateways, implement similar logic
                    flash('Payment method not fully implemented yet.', 'error')
            except Exception as e:
                current_app.logger.error(f"Payment processing error: {str(e)}")
                flash(f'Payment processing error: {str(e)}', 'error')

    return render_template('subscription/payment.html',
                          payment=payment,
                          subscription=subscription,
                          shop=shop,
                          available_gateways=available_gateways)

# Invoice routes
@subscription_bp.route('/invoice/<int:invoice_id>', methods=['GET'])
@login_required
def view_invoice(invoice_id):
    """View subscription invoice"""
    invoice = SubscriptionInvoice.query.get_or_404(invoice_id)
    subscription = invoice.subscription

    # Ensure user has permission to access this invoice
    if current_user.branch.shop_id != subscription.shop_id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('dashboard'))

    # If invoice PDF doesn't exist, generate it
    if not invoice.pdf_path:
        try:
            from backend.utils.invoice_generator import InvoiceGenerator
            invoice_path = InvoiceGenerator.generate_subscription_invoice(invoice.id)
            invoice.pdf_path = invoice_path
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error generating invoice: {str(e)}")
            flash('Error generating invoice PDF', 'error')
            return redirect(url_for('subscription.subscription_status'))

    # Redirect to the PDF file
    return redirect(invoice.pdf_path)

@subscription_bp.route('/invoices', methods=['GET'])
@login_required
def list_invoices():
    """List all invoices for the current shop"""
    # Get the shop associated with the current user's branch
    if not current_user.branch or not current_user.branch.shop:
        flash('No subscription found', 'error')
        return redirect(url_for('dashboard'))

    shop = current_user.branch.shop
    subscription = shop.subscription

    if not subscription:
        flash('No subscription found', 'error')
        return redirect(url_for('dashboard'))

    # Get all invoices for the subscription
    invoices = SubscriptionInvoice.query.filter_by(subscription_id=subscription.id).order_by(SubscriptionInvoice.issue_date.desc()).all()

    return render_template('subscription/invoices.html',
                          shop=shop,
                          subscription=subscription,
                          invoices=invoices)

# Webhook endpoint for payment gateway callbacks
@subscription_bp.route('/webhook/<gateway>', methods=['POST'])
def webhook(gateway):
    """Webhook endpoint for payment gateway callbacks"""
    try:
        # Get the appropriate gateway handler
        from backend.utils.payment_gateways import PaymentGatewayFactory
        gateway_handler = PaymentGatewayFactory.create_gateway(gateway)

        # Handle webhook based on gateway type
        if gateway == 'stripe':
            # Get Stripe signature from headers
            signature = request.headers.get('Stripe-Signature')

            # Handle webhook event
            result = gateway_handler.handle_webhook_event(request.data, signature)

            return jsonify(result)
        elif gateway == 'tap':
            # Handle Tap webhook
            result = gateway_handler.handle_webhook_event(request.json, None)
            return jsonify(result)
        elif gateway == 'hyperpay':
            # Handle HyperPay webhook
            result = gateway_handler.handle_webhook_event(request.json, None)
            return jsonify(result)
        else:
            return jsonify({'success': False, 'message': f'Unknown gateway: {gateway}'})
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)})

# API endpoints for subscription status
@subscription_bp.route('/api/status', methods=['GET'])
@login_required
def api_subscription_status():
    """API endpoint to check subscription status"""
    # Get the shop associated with the current user's branch
    if not current_user.branch or not current_user.branch.shop:
        return jsonify({
            'success': False,
            'error': 'No subscription found'
        }), 404

    shop = current_user.branch.shop
    subscription = shop.subscription

    if not subscription:
        return jsonify({
            'success': False,
            'error': 'No subscription found'
        }), 404

    return jsonify({
        'success': True,
        'subscription': {
            'id': subscription.id,
            'plan_name': subscription.plan.name,
            'status': subscription.status,
            'is_active': subscription.is_active,
            'is_expired': subscription.is_expired,
            'days_remaining': subscription.days_remaining,
            'start_date': subscription.start_date.isoformat(),
            'end_date': subscription.end_date.isoformat(),
            'billing_cycle': subscription.billing_cycle,
            'payment_status': subscription.payment_status
        }
    })
