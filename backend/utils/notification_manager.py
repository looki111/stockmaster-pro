"""
Notification Manager for StockMaster Pro
Handles sending notifications via email, SMS, and in-app notifications
"""

import os
from datetime import datetime, timedelta
from flask import current_app, render_template
from backend.database.models import Notification, User
from backend.database.subscription_models import Subscription, Shop
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

class NotificationManager:
    """
    Notification Manager for StockMaster Pro
    Handles sending notifications via email, SMS, and in-app notifications
    """
    
    @staticmethod
    def send_subscription_expiry_notifications():
        """
        Send notifications for subscriptions that are about to expire
        
        This should be run daily via a scheduled task
        """
        try:
            # Get subscriptions expiring in the next 7 days
            now = datetime.utcnow()
            expiry_threshold = now + timedelta(days=7)
            
            expiring_subscriptions = Subscription.query.filter(
                Subscription.is_active == True,
                Subscription.end_date <= expiry_threshold,
                Subscription.end_date > now
            ).all()
            
            for subscription in expiring_subscriptions:
                # Calculate days until expiry
                days_remaining = (subscription.end_date - now).days
                
                # Get shop and admin users
                shop = Shop.query.get(subscription.shop_id)
                if not shop:
                    continue
                
                # Get admin users for the shop
                admin_users = User.query.join(User.branch).filter(
                    User.branch.has(shop_id=shop.id),
                    User.is_superuser == True
                ).all()
                
                # Send notifications based on days remaining
                if days_remaining <= 1:
                    # Urgent notification - 1 day or less
                    NotificationManager.send_urgent_expiry_notification(subscription, shop, admin_users)
                elif days_remaining <= 3:
                    # Warning notification - 3 days or less
                    NotificationManager.send_warning_expiry_notification(subscription, shop, admin_users)
                else:
                    # Regular reminder - 7 days or less
                    NotificationManager.send_reminder_expiry_notification(subscription, shop, admin_users)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending subscription expiry notifications: {str(e)}")
            return False
    
    @staticmethod
    def send_urgent_expiry_notification(subscription, shop, admin_users):
        """
        Send urgent notification for subscription expiring in 1 day or less
        
        Args:
            subscription: Subscription model instance
            shop: Shop model instance
            admin_users: List of admin User model instances
        """
        # Create notification message
        days_remaining = (subscription.end_date - datetime.utcnow()).days
        hours_remaining = int((subscription.end_date - datetime.utcnow()).total_seconds() / 3600)
        
        if days_remaining <= 0:
            time_text = f"{hours_remaining} hours" if hours_remaining > 0 else "less than an hour"
            subject = f"URGENT: Your StockMaster Pro subscription expires in {time_text}"
            message = f"Your {subscription.plan.name} subscription will expire in {time_text}. Renew now to avoid service interruption."
        else:
            subject = f"URGENT: Your StockMaster Pro subscription expires tomorrow"
            message = f"Your {subscription.plan.name} subscription will expire tomorrow. Renew now to avoid service interruption."
        
        # Send in-app notifications to all admin users
        for user in admin_users:
            notification = Notification(
                user_id=user.id,
                title=subject,
                message=message,
                type='subscription_expiry',
                priority='high',
                link='/subscription/renew'
            )
            current_app.db.session.add(notification)
        
        # Send email to shop owner
        NotificationManager.send_email(
            recipient=shop.email,
            subject=subject,
            template='emails/subscription_expiry_urgent.html',
            data={
                'shop_name': shop.name,
                'plan_name': subscription.plan.name,
                'expiry_date': subscription.end_date.strftime('%Y-%m-%d'),
                'time_remaining': f"{hours_remaining} hours" if hours_remaining > 0 else "less than an hour",
                'renewal_url': f"{current_app.config.get('BASE_URL')}/subscription/renew"
            }
        )
        
        # Send SMS if phone number is available
        if shop.phone:
            sms_message = f"URGENT: Your StockMaster Pro subscription expires in {time_text if days_remaining <= 0 else 'tomorrow'}. Renew now to avoid service interruption."
            NotificationManager.send_sms(shop.phone, sms_message)
        
        current_app.db.session.commit()
    
    @staticmethod
    def send_warning_expiry_notification(subscription, shop, admin_users):
        """
        Send warning notification for subscription expiring in 3 days or less
        
        Args:
            subscription: Subscription model instance
            shop: Shop model instance
            admin_users: List of admin User model instances
        """
        # Create notification message
        days_remaining = (subscription.end_date - datetime.utcnow()).days
        subject = f"Warning: Your StockMaster Pro subscription expires in {days_remaining} days"
        message = f"Your {subscription.plan.name} subscription will expire in {days_remaining} days. Renew now to ensure uninterrupted service."
        
        # Send in-app notifications to all admin users
        for user in admin_users:
            notification = Notification(
                user_id=user.id,
                title=subject,
                message=message,
                type='subscription_expiry',
                priority='medium',
                link='/subscription/renew'
            )
            current_app.db.session.add(notification)
        
        # Send email to shop owner
        NotificationManager.send_email(
            recipient=shop.email,
            subject=subject,
            template='emails/subscription_expiry_warning.html',
            data={
                'shop_name': shop.name,
                'plan_name': subscription.plan.name,
                'expiry_date': subscription.end_date.strftime('%Y-%m-%d'),
                'days_remaining': days_remaining,
                'renewal_url': f"{current_app.config.get('BASE_URL')}/subscription/renew"
            }
        )
        
        current_app.db.session.commit()
    
    @staticmethod
    def send_reminder_expiry_notification(subscription, shop, admin_users):
        """
        Send reminder notification for subscription expiring in 7 days or less
        
        Args:
            subscription: Subscription model instance
            shop: Shop model instance
            admin_users: List of admin User model instances
        """
        # Create notification message
        days_remaining = (subscription.end_date - datetime.utcnow()).days
        subject = f"Reminder: Your StockMaster Pro subscription expires in {days_remaining} days"
        message = f"Your {subscription.plan.name} subscription will expire in {days_remaining} days. Renew now for uninterrupted service."
        
        # Send in-app notifications to all admin users
        for user in admin_users:
            notification = Notification(
                user_id=user.id,
                title=subject,
                message=message,
                type='subscription_expiry',
                priority='low',
                link='/subscription/renew'
            )
            current_app.db.session.add(notification)
        
        # Send email to shop owner
        NotificationManager.send_email(
            recipient=shop.email,
            subject=subject,
            template='emails/subscription_expiry_reminder.html',
            data={
                'shop_name': shop.name,
                'plan_name': subscription.plan.name,
                'expiry_date': subscription.end_date.strftime('%Y-%m-%d'),
                'days_remaining': days_remaining,
                'renewal_url': f"{current_app.config.get('BASE_URL')}/subscription/renew"
            }
        )
        
        current_app.db.session.commit()
    
    @staticmethod
    def send_subscription_payment_confirmation(subscription, payment):
        """
        Send payment confirmation notification
        
        Args:
            subscription: Subscription model instance
            payment: SubscriptionPayment model instance
        """
        try:
            # Get shop and admin users
            shop = Shop.query.get(subscription.shop_id)
            if not shop:
                return False
            
            # Get admin users for the shop
            admin_users = User.query.join(User.branch).filter(
                User.branch.has(shop_id=shop.id),
                User.is_superuser == True
            ).all()
            
            # Create notification message
            subject = f"Payment Confirmation: Your StockMaster Pro subscription has been renewed"
            message = f"Your payment of {payment.amount} {shop.currency or 'SAR'} for the {subscription.plan.name} subscription has been processed successfully."
            
            # Send in-app notifications to all admin users
            for user in admin_users:
                notification = Notification(
                    user_id=user.id,
                    title=subject,
                    message=message,
                    type='payment_confirmation',
                    priority='medium',
                    link='/subscription/status'
                )
                current_app.db.session.add(notification)
            
            # Send email to shop owner
            NotificationManager.send_email(
                recipient=shop.email,
                subject=subject,
                template='emails/payment_confirmation.html',
                data={
                    'shop_name': shop.name,
                    'plan_name': subscription.plan.name,
                    'amount': payment.amount,
                    'currency': shop.currency or 'SAR',
                    'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                    'payment_method': payment.payment_method,
                    'invoice_url': f"{current_app.config.get('BASE_URL')}/subscription/invoice/{payment.id}"
                }
            )
            
            current_app.db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending payment confirmation notification: {str(e)}")
            return False
    
    @staticmethod
    def send_email(recipient, subject, template, data):
        """
        Send an email using SMTP
        
        Args:
            recipient: Email recipient
            subject: Email subject
            template: Email template path
            data: Template data
            
        Returns:
            bool: Success status
        """
        try:
            # Get email configuration
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            smtp_username = os.getenv('SMTP_USERNAME', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')
            sender_email = os.getenv('SENDER_EMAIL', 'noreply@stockmasterpro.com')
            sender_name = os.getenv('SENDER_NAME', 'StockMaster Pro')
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{sender_name} <{sender_email}>"
            msg['To'] = recipient
            
            # Render email template
            html_content = render_template(template, **data)
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def send_sms(phone_number, message):
        """
        Send an SMS using a third-party SMS gateway
        
        Args:
            phone_number: Recipient phone number
            message: SMS message
            
        Returns:
            bool: Success status
        """
        try:
            # Get SMS configuration
            sms_api_url = os.getenv('SMS_API_URL', '')
            sms_api_key = os.getenv('SMS_API_KEY', '')
            
            if not sms_api_url or not sms_api_key:
                current_app.logger.warning("SMS API not configured")
                return False
            
            # Prepare request data
            data = {
                'api_key': sms_api_key,
                'to': phone_number,
                'message': message,
                'sender': 'StockMaster'
            }
            
            # Send SMS
            response = requests.post(sms_api_url, json=data)
            
            if response.status_code == 200:
                return True
            else:
                current_app.logger.error(f"SMS API error: {response.text}")
                return False
        except Exception as e:
            current_app.logger.error(f"Error sending SMS: {str(e)}")
            return False
