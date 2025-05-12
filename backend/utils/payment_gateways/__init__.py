"""
Payment Gateway Package for StockMaster Pro
"""

from .gateway_factory import PaymentGatewayFactory
from .stripe_gateway import StripeGateway
from .manual_gateway import ManualGateway

# Create placeholder imports for other gateways
# These will be implemented later
try:
    from .tap_gateway import TapGateway
except ImportError:
    class TapGateway:
        """Placeholder for TapGateway"""
        pass

try:
    from .hyperpay_gateway import HyperPayGateway
except ImportError:
    class HyperPayGateway:
        """Placeholder for HyperPayGateway"""
        pass
