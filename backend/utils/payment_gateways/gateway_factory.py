"""
Payment Gateway Factory for StockMaster Pro
Provides a factory pattern for creating payment gateway instances
"""

import os
from flask import current_app
from .stripe_gateway import StripeGateway
from .tap_gateway import TapGateway
from .hyperpay_gateway import HyperPayGateway
from .manual_gateway import ManualGateway

class PaymentGatewayFactory:
    """
    Factory class for creating payment gateway instances
    """
    
    @staticmethod
    def create_gateway(gateway_type=None):
        """
        Create a payment gateway instance based on the specified type
        
        Args:
            gateway_type: Type of payment gateway ('stripe', 'tap', 'hyperpay', 'manual')
                          If None, uses the default gateway from environment variables
        
        Returns:
            Payment gateway instance
        """
        # If no gateway type specified, use default from environment
        if not gateway_type:
            gateway_type = os.getenv('DEFAULT_PAYMENT_GATEWAY', 'manual')
        
        # Create gateway instance based on type
        if gateway_type.lower() == 'stripe':
            return StripeGateway()
        elif gateway_type.lower() == 'tap':
            return TapGateway()
        elif gateway_type.lower() == 'hyperpay':
            return HyperPayGateway()
        elif gateway_type.lower() == 'manual':
            return ManualGateway()
        else:
            current_app.logger.error(f"Unknown payment gateway type: {gateway_type}")
            # Default to manual gateway
            return ManualGateway()
    
    @staticmethod
    def get_available_gateways():
        """
        Get a list of available payment gateways
        
        Returns:
            list: List of available payment gateway types and their display names
        """
        gateways = []
        
        # Check if Stripe is configured
        if os.getenv('STRIPE_SECRET_KEY'):
            gateways.append({
                'type': 'stripe',
                'name': 'Stripe',
                'description': 'Credit/debit cards, Apple Pay, Google Pay',
                'icon': 'ri-stripe-line',
                'is_default': os.getenv('DEFAULT_PAYMENT_GATEWAY') == 'stripe'
            })
        
        # Check if Tap is configured
        if os.getenv('TAP_SECRET_KEY'):
            gateways.append({
                'type': 'tap',
                'name': 'Tap Payments',
                'description': 'Popular in Middle East, supports MADA cards',
                'icon': 'ri-bank-card-line',
                'is_default': os.getenv('DEFAULT_PAYMENT_GATEWAY') == 'tap'
            })
        
        # Check if HyperPay is configured
        if os.getenv('HYPERPAY_ACCESS_TOKEN'):
            gateways.append({
                'type': 'hyperpay',
                'name': 'HyperPay',
                'description': 'Multiple payment methods for MENA region',
                'icon': 'ri-secure-payment-line',
                'is_default': os.getenv('DEFAULT_PAYMENT_GATEWAY') == 'hyperpay'
            })
        
        # Manual gateway is always available
        gateways.append({
            'type': 'manual',
            'name': 'Manual Payment',
            'description': 'Bank transfer or other manual payment methods',
            'icon': 'ri-bank-line',
            'is_default': os.getenv('DEFAULT_PAYMENT_GATEWAY') == 'manual' or not os.getenv('DEFAULT_PAYMENT_GATEWAY')
        })
        
        return gateways
