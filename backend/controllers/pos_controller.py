"""
POS Controller for StockMaster Pro
Handles POS mode operations and data management
"""

from flask import current_app
from database.db_setup import db
from database.models import (
    Product, Order, OrderItem, Client, Branch, User, Promotion, Shift
)
from utils.invoice import InvoiceGenerator
from utils.loyalty import calculate_loyalty_points
from notifications import create_notification
from datetime import datetime, timezone
import json

class POSController:
    """
    POS Controller for StockMaster Pro
    Handles POS mode operations and data management
    """

    @staticmethod
    def get_pos_data(branch_id):
        """
        Get all data needed for POS mode

        Args:
            branch_id: Branch ID

        Returns:
            dict: POS data
        """
        try:
            # Get branch
            branch = Branch.query.get_or_404(branch_id)

            # Get products
            products = Product.query.filter_by(branch_id=branch_id, is_active=True).all()

            # Get categories
            categories = db.session.query(Product.category).filter_by(branch_id=branch_id).distinct().all()
            categories = [c[0] for c in categories if c[0]]

            # Get active promotions
            promotions = Promotion.query.filter(
                Promotion.is_active == True,
                Promotion.end_date >= datetime.now(timezone.utc)
            ).all()

            # Get recent clients
            recent_clients = Client.query.filter_by(branch_id=branch_id).order_by(Client.last_visit.desc()).limit(10).all()

            # Get active shift
            active_shift = Shift.query.filter_by(branch_id=branch_id, status='active').first()

            # Format data for response
            pos_data = {
                'branch': {
                    'id': branch.id,
                    'name': branch.name,
                    'currency': branch.currency,
                    'tax_rate': branch.tax_rate,
                    'order_types': branch.order_types or ['dine_in', 'takeaway', 'delivery'],
                    'quick_pos_mode': branch.quick_pos_mode
                },
                'products': [{
                    'id': p.id,
                    'name': p.name,
                    'price': p.price,
                    'category': p.category,
                    'image': p.image,
                    'description': p.description,
                    'has_variants': bool(p.variants),
                    'variants': p.variants,
                    'in_stock': p.quantity > 0,
                    'quantity': p.quantity
                } for p in products],
                'categories': categories,
                'promotions': [{
                    'id': p.id,
                    'name': p.name,
                    'discount_type': p.discount_type,
                    'discount_value': p.discount_value,
                    'min_purchase': p.min_purchase,
                    'max_discount': p.max_discount,
                    'applicable_products': json.loads(p.applicable_products) if p.applicable_products else []
                } for p in promotions],
                'recent_clients': [{
                    'id': c.id,
                    'name': c.name,
                    'phone': c.phone,
                    'loyalty_points': c.loyalty_points
                } for c in recent_clients],
                'shift': {
                    'active': bool(active_shift),
                    'id': active_shift.id if active_shift else None,
                    'start_time': active_shift.start_time.isoformat() if active_shift else None,
                    'initial_cash': active_shift.initial_cash if active_shift else 0
                }
            }

            return pos_data

        except Exception as e:
            current_app.logger.error(f"Error getting POS data: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def create_order(order_data, user_id):
        """
        Create a new order from POS

        Args:
            order_data: Order data from request
            user_id: User ID creating the order

        Returns:
            dict: Order result
        """
        try:
            # Get user and branch
            user = User.query.get_or_404(user_id)
            branch = user.branch

            # Generate invoice number
            invoice_number = POSController.generate_invoice_number(branch.id)

            # Create order
            order = Order(
                invoice_number=invoice_number,
                customer_name=order_data.get('customer_name'),
                client_id=order_data.get('client_id'),
                subtotal=order_data['subtotal'],
                tax=order_data['tax'],
                total=order_data['total'],
                payment_method=order_data['payment_method'],
                created_by=user_id,
                branch_id=branch.id,
                status=order_data.get('status', 'completed'),
                notes=order_data.get('notes'),
                order_type=order_data.get('order_type', 'dine_in'),
                table_number=order_data.get('table_number'),
                delivery_address=order_data.get('delivery_address')
            )

            # Add order items
            for item_data in order_data['items']:
                item = OrderItem(
                    product_id=item_data['product_id'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                    notes=item_data.get('notes')
                )
                order.items.append(item)

                # Update product quantity
                product = Product.query.get(item_data['product_id'])
                if product:
                    product.quantity -= item_data['quantity']

                    # Check if below threshold
                    if product.quantity <= product.alert_threshold:
                        create_notification(
                            user_id=user_id,
                            title='Low Stock Alert',
                            message=f'{product.name} is running low ({product.quantity} remaining)',
                            type='warning'
                        )

                # We'll process inventory after the order is created using the new system

            # Calculate and add loyalty points
            if order.client_id:
                client = Client.query.get(order.client_id)
                if client:
                    points = calculate_loyalty_points(order.total)
                    order.loyalty_points_earned = points
                    client.loyalty_points += points
                    client.total_spent += order.total
                    client.last_visit = datetime.now(timezone.utc)

            # Update shift data
            active_shift = Shift.query.filter_by(branch_id=branch.id, status='active').first()
            if active_shift:
                active_shift.total_sales += order.total
                active_shift.total_orders += 1

            db.session.add(order)
            db.session.commit()

            # Process inventory using the new system
            try:
                inventory_result = order.process_inventory(user_id)

                if not inventory_result.get('success'):
                    current_app.logger.warning(f"Inventory processing warning: {inventory_result.get('error')}")
            except Exception as e:
                current_app.logger.error(f"Error processing inventory: {str(e)}")

            # Generate PDF invoice
            try:
                invoice = InvoiceGenerator(order)
                invoice_path = invoice.generate()
            except Exception as e:
                current_app.logger.error(f"Error generating invoice: {str(e)}")
                invoice_path = None

            return {
                'success': True,
                'order_id': order.id,
                'invoice_number': order.invoice_number,
                'invoice_path': invoice_path
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating order: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def generate_invoice_number(branch_id):
        """
        Generate a unique invoice number

        Args:
            branch_id: Branch ID

        Returns:
            str: Invoice number
        """
        # Generate a unique invoice number based on date and sequence
        today = datetime.now(timezone.utc).strftime('%Y%m%d')
        branch_prefix = f"B{branch_id}"

        # Get last order for this branch today
        last_order = Order.query.filter(
            Order.branch_id == branch_id,
            Order.invoice_number.like(f'{branch_prefix}{today}%')
        ).order_by(Order.invoice_number.desc()).first()

        if last_order and last_order.invoice_number:
            # Extract sequence number from last invoice
            try:
                sequence = int(last_order.invoice_number[-4:]) + 1
            except (ValueError, IndexError):
                sequence = 1
        else:
            sequence = 1

        return f'{branch_prefix}{today}{sequence:04d}'

    @staticmethod
    def get_client_info(client_id):
        """
        Get client information for POS

        Args:
            client_id: Client ID

        Returns:
            dict: Client information
        """
        try:
            client = Client.query.get_or_404(client_id)

            # Get recent orders
            recent_orders = Order.query.filter_by(client_id=client_id).order_by(Order.created_at.desc()).limit(5).all()

            return {
                'success': True,
                'client': {
                    'id': client.id,
                    'name': client.name,
                    'phone': client.phone,
                    'email': client.email,
                    'address': client.address,
                    'loyalty_points': client.loyalty_points,
                    'total_spent': client.total_spent,
                    'notes': client.notes,
                    'recent_orders': [{
                        'id': order.id,
                        'date': order.created_at.isoformat(),
                        'total': order.total,
                        'items': len(order.items)
                    } for order in recent_orders]
                }
            }

        except Exception as e:
            current_app.logger.error(f"Error getting client info: {str(e)}")
            return {'success': False, 'error': str(e)}
