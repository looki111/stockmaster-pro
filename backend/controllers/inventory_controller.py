"""
Inventory Controller for StockMaster Pro
Handles inventory management, consumption rules, and stock reports
"""

from flask import current_app, jsonify, request, session
from database.db_setup import db
from database.models import (
    Product, RawMaterial, Recipe, Order, OrderItem, Branch, User
)
from database.inventory_models import (
    InventoryTransaction, StockCount, StockCountItem, ConsumptionRule,
    InventoryAdjustment, InventoryAdjustmentItem, DailyStockReport, DailyStockReportItem
)
from notifications import create_notification
from middleware.tenant_context import TenantContext
from datetime import datetime, timedelta, timezone
import json
import uuid

class InventoryController:
    """
    Inventory Controller for StockMaster Pro
    Handles inventory management, consumption rules, and stock reports
    """

    @staticmethod
    def get_raw_materials(branch_id, category=None, search=None, status=None, low_stock=False):
        """
        Get raw materials for a branch with optional filtering

        Args:
            branch_id: Branch ID
            category: Filter by category
            search: Search term
            status: Filter by status
            low_stock: Only show low stock items

        Returns:
            list: Raw materials
        """
        try:
            # Build query
            query = RawMaterial.query.filter_by(branch_id=branch_id)

            # Apply filters
            if category:
                query = query.filter_by(category=category)

            if search:
                query = query.filter(RawMaterial.name.ilike(f'%{search}%'))

            if status:
                query = query.filter_by(status=status)

            if low_stock:
                query = query.filter(RawMaterial.quantity <= RawMaterial.alert_threshold)

            # Execute query
            raw_materials = query.all()

            # Format response
            result = []
            for material in raw_materials:
                result.append({
                    'id': material.id,
                    'name': material.name,
                    'quantity': material.quantity,
                    'unit': material.unit,
                    'category': material.category,
                    'alert_threshold': material.alert_threshold,
                    'cost_price': material.cost_price,
                    'status': material.status,
                    'is_low_stock': material.quantity <= material.alert_threshold,
                    'is_expiring_soon': material.is_expiring_soon if hasattr(material, 'is_expiring_soon') else False,
                    'days_until_expiry': material.days_until_expiry if hasattr(material, 'days_until_expiry') else None,
                    'stock_value': material.stock_value if hasattr(material, 'stock_value') else (material.quantity * material.cost_price if material.cost_price else 0)
                })

            return result

        except Exception as e:
            current_app.logger.error(f"Error getting raw materials: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def get_consumption_rules(product_id=None, raw_material_id=None):
        """
        Get consumption rules for a product or raw material

        Args:
            product_id: Product ID
            raw_material_id: Raw Material ID

        Returns:
            list: Consumption rules
        """
        try:
            # Build query
            query = ConsumptionRule.query.filter_by(is_active=True)

            # Apply filters
            if product_id:
                query = query.filter_by(product_id=product_id)

            if raw_material_id:
                query = query.filter_by(raw_material_id=raw_material_id)

            # Execute query
            rules = query.all()

            # Format response
            result = []
            for rule in rules:
                product = Product.query.get(rule.product_id)
                raw_material = RawMaterial.query.get(rule.raw_material_id)

                result.append({
                    'id': rule.id,
                    'product_id': rule.product_id,
                    'product_name': product.name if product else 'Unknown',
                    'raw_material_id': rule.raw_material_id,
                    'raw_material_name': raw_material.name if raw_material else 'Unknown',
                    'quantity': rule.quantity,
                    'unit': rule.unit,
                    'waste_factor': rule.waste_factor,
                    'condition_type': rule.condition_type,
                    'condition_value': rule.condition_value
                })

            return result

        except Exception as e:
            current_app.logger.error(f"Error getting consumption rules: {str(e)}")
            return {'error': str(e)}

    @staticmethod
    def create_consumption_rule(data, user_id):
        """
        Create a new consumption rule

        Args:
            data: Consumption rule data
            user_id: User ID creating the rule

        Returns:
            dict: Result
        """
        try:
            # Validate data
            if not data.get('product_id'):
                return {'success': False, 'error': 'Product ID is required'}

            if not data.get('raw_material_id'):
                return {'success': False, 'error': 'Raw Material ID is required'}

            if not data.get('quantity'):
                return {'success': False, 'error': 'Quantity is required'}

            # Create consumption rule
            rule = ConsumptionRule(
                product_id=data['product_id'],
                raw_material_id=data['raw_material_id'],
                quantity=float(data['quantity']),
                unit=data.get('unit', 'g'),
                waste_factor=float(data.get('waste_factor', 0)),
                condition_type=data.get('condition_type'),
                condition_value=data.get('condition_value'),
                is_active=True
            )

            db.session.add(rule)
            db.session.commit()

            # Get product and raw material names for response
            product = Product.query.get(rule.product_id)
            raw_material = RawMaterial.query.get(rule.raw_material_id)

            return {
                'success': True,
                'rule': {
                    'id': rule.id,
                    'product_id': rule.product_id,
                    'product_name': product.name if product else 'Unknown',
                    'raw_material_id': rule.raw_material_id,
                    'raw_material_name': raw_material.name if raw_material else 'Unknown',
                    'quantity': rule.quantity,
                    'unit': rule.unit,
                    'waste_factor': rule.waste_factor,
                    'condition_type': rule.condition_type,
                    'condition_value': rule.condition_value
                }
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating consumption rule: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def process_inventory_consumption(order_id, user_id):
        """
        Process inventory consumption for an order

        Args:
            order_id: Order ID
            user_id: User ID processing the order

        Returns:
            dict: Result with consumed materials
        """
        try:
            # Get order
            order = Order.query.get_or_404(order_id)

            # Get order items
            order_items = OrderItem.query.filter_by(order_id=order_id).all()

            # Track consumed materials
            consumed_materials = {}

            # Process each order item
            for item in order_items:
                # Get product
                product = Product.query.get(item.product_id)
                if not product:
                    continue

                # Get consumption rules for product
                consumption_rules = ConsumptionRule.query.filter_by(
                    product_id=product.id,
                    is_active=True
                ).all()

                # If no consumption rules, try legacy recipes
                if not consumption_rules:
                    recipes = Recipe.query.filter_by(product_id=product.id).all()

                    # Process legacy recipes
                    for recipe in recipes:
                        raw_material = RawMaterial.query.get(recipe.raw_material_id)
                        if not raw_material:
                            continue

                        # Calculate consumption amount
                        consumption_amount = recipe.amount * item.quantity

                        # Update raw material quantity
                        raw_material.quantity -= consumption_amount

                        # Track consumption
                        if raw_material.id in consumed_materials:
                            consumed_materials[raw_material.id]['amount'] += consumption_amount
                        else:
                            consumed_materials[raw_material.id] = {
                                'id': raw_material.id,
                                'name': raw_material.name,
                                'amount': consumption_amount,
                                'unit': raw_material.unit,
                                'remaining': raw_material.quantity
                            }

                        # Create inventory transaction
                        transaction = InventoryTransaction(
                            transaction_type='sale',
                            reference_type='order',
                            reference_id=order.id,
                            raw_material_id=raw_material.id,
                            product_id=product.id,
                            quantity=-consumption_amount,  # Negative for consumption
                            unit=raw_material.unit,
                            unit_cost=raw_material.cost_price,
                            branch_id=order.branch_id,
                            created_by=user_id,
                            notes=f"Consumed for Order #{order.id}"
                        )

                        db.session.add(transaction)

                        # Check if below threshold
                        if raw_material.quantity <= raw_material.alert_threshold:
                            create_notification(
                                user_id=user_id,
                                title='Low Stock Alert',
                                message=f'{raw_material.name} is running low ({raw_material.quantity} {raw_material.unit} remaining)',
                                type='warning'
                            )
                else:
                    # Process consumption rules
                    for rule in consumption_rules:
                        raw_material = RawMaterial.query.get(rule.raw_material_id)
                        if not raw_material:
                            continue

                        # Calculate consumption amount with waste factor
                        base_consumption = rule.quantity * item.quantity
                        waste_amount = base_consumption * rule.waste_factor
                        total_consumption = base_consumption + waste_amount

                        # Update raw material quantity
                        raw_material.quantity -= total_consumption

                        # Track consumption
                        if raw_material.id in consumed_materials:
                            consumed_materials[raw_material.id]['amount'] += total_consumption
                        else:
                            consumed_materials[raw_material.id] = {
                                'id': raw_material.id,
                                'name': raw_material.name,
                                'amount': total_consumption,
                                'unit': rule.unit,
                                'remaining': raw_material.quantity
                            }

                        # Create inventory transaction for consumption
                        consumption_transaction = InventoryTransaction(
                            transaction_type='sale',
                            reference_type='order',
                            reference_id=order.id,
                            raw_material_id=raw_material.id,
                            product_id=product.id,
                            quantity=-base_consumption,  # Negative for consumption
                            unit=rule.unit,
                            unit_cost=raw_material.cost_price,
                            branch_id=order.branch_id,
                            created_by=user_id,
                            notes=f"Consumed for Order #{order.id}"
                        )

                        db.session.add(consumption_transaction)

                        # Create separate transaction for waste if applicable
                        if waste_amount > 0:
                            waste_transaction = InventoryTransaction(
                                transaction_type='waste',
                                reference_type='order',
                                reference_id=order.id,
                                raw_material_id=raw_material.id,
                                product_id=product.id,
                                quantity=-waste_amount,  # Negative for waste
                                unit=rule.unit,
                                unit_cost=raw_material.cost_price,
                                branch_id=order.branch_id,
                                created_by=user_id,
                                notes=f"Waste for Order #{order.id}"
                            )

                            db.session.add(waste_transaction)

                        # Check if below threshold
                        if raw_material.quantity <= raw_material.alert_threshold:
                            create_notification(
                                user_id=user_id,
                                title='Low Stock Alert',
                                message=f'{raw_material.name} is running low ({raw_material.quantity} {raw_material.unit} remaining)',
                                type='warning'
                            )

            db.session.commit()

            return {
                'success': True,
                'consumed_materials': list(consumed_materials.values())
            }

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error processing inventory consumption: {str(e)}")
            return {'success': False, 'error': str(e)}
