"""
Stock Report Generator for StockMaster Pro
Generates daily stock reports and inventory analytics
"""

from datetime import datetime, timedelta, date
from flask import current_app
from database.db_setup import db
from database.models import RawMaterial, Branch
from database.inventory_models import (
    InventoryTransaction, DailyStockReport, DailyStockReportItem
)
from sqlalchemy import func, and_, or_
try:
    import pandas as pd
    import numpy as np
    print("Successfully imported pandas and numpy in stock_report.py")
except ImportError as e:
    print("Error importing pandas or numpy in stock_report.py:", e)
    # Use alternative implementations without pandas and numpy
    pd = None
    np = None
import io
import csv

class StockReportGenerator:
    """
    Stock Report Generator for StockMaster Pro
    Generates daily stock reports and inventory analytics
    """
    # Check if pandas and numpy are available
    has_pandas = pd is not None
    has_numpy = np is not None

    @staticmethod
    def generate_daily_report(branch_id, report_date=None):
        """
        Generate a daily stock report for a branch

        Args:
            branch_id: Branch ID
            report_date: Report date (defaults to today)

        Returns:
            dict: Report data
        """
        try:
            # Set report date
            if not report_date:
                report_date = date.today()
            elif isinstance(report_date, str):
                report_date = datetime.strptime(report_date, '%Y-%m-%d').date()

            # Check if report already exists
            existing_report = DailyStockReport.query.filter_by(
                branch_id=branch_id,
                report_date=report_date
            ).first()

            if existing_report:
                return StockReportGenerator.get_report(existing_report.id)

            # Get branch
            branch = Branch.query.get_or_404(branch_id)

            # Get all raw materials for the branch
            raw_materials = RawMaterial.query.filter_by(branch_id=branch_id).all()

            # Create report
            report = DailyStockReport(
                report_date=report_date,
                branch_id=branch_id,
                shop_id=branch.shop_id,
                status='generated',
                total_items=len(raw_materials),
                low_stock_items=0,
                out_of_stock_items=0,
                total_value=0,
                total_consumption=0,
                waste_percentage=0
            )

            db.session.add(report)
            db.session.flush()  # Get report ID without committing

            # Set date range for transactions
            start_date = datetime.combine(report_date, datetime.min.time())
            end_date = datetime.combine(report_date, datetime.max.time())

            # Track totals
            total_value = 0
            total_consumption = 0
            total_waste = 0
            low_stock_count = 0
            out_of_stock_count = 0

            # Process each raw material
            for material in raw_materials:
                # Get transactions for the day
                transactions = InventoryTransaction.query.filter(
                    InventoryTransaction.raw_material_id == material.id,
                    InventoryTransaction.branch_id == branch_id,
                    InventoryTransaction.created_at.between(start_date, end_date)
                ).all()

                # Calculate quantities
                received_qty = sum(t.quantity for t in transactions if t.quantity > 0)
                consumed_qty = abs(sum(t.quantity for t in transactions if t.quantity < 0 and t.transaction_type == 'sale'))
                waste_qty = abs(sum(t.quantity for t in transactions if t.quantity < 0 and t.transaction_type == 'waste'))
                adjusted_qty = sum(t.quantity for t in transactions if t.transaction_type == 'adjustment')

                # Calculate opening and closing quantities
                # Opening = current - (received - consumed - waste + adjusted)
                opening_qty = material.quantity - (received_qty - consumed_qty - waste_qty + adjusted_qty)
                closing_qty = material.quantity

                # Determine status
                if closing_qty <= 0:
                    status = 'out_of_stock'
                    out_of_stock_count += 1
                elif closing_qty <= material.alert_threshold:
                    status = 'low_stock'
                    low_stock_count += 1
                elif material.is_expiring_soon if hasattr(material, 'is_expiring_soon') else False:
                    status = 'expiring_soon'
                else:
                    status = 'normal'

                # Calculate value
                unit_cost = material.average_cost or material.cost_price or 0
                total_value += closing_qty * unit_cost

                # Track consumption and waste
                total_consumption += consumed_qty
                total_waste += waste_qty

                # Create report item
                report_item = DailyStockReportItem(
                    report_id=report.id,
                    raw_material_id=material.id,
                    opening_quantity=opening_qty,
                    received_quantity=received_qty,
                    consumed_quantity=consumed_qty,
                    waste_quantity=waste_qty,
                    adjusted_quantity=adjusted_qty,
                    closing_quantity=closing_qty,
                    unit=material.unit,
                    unit_cost=unit_cost,
                    total_value=closing_qty * unit_cost,
                    status=status
                )

                db.session.add(report_item)

            # Update report totals
            report.low_stock_items = low_stock_count
            report.out_of_stock_items = out_of_stock_count
            report.total_value = total_value
            report.total_consumption = total_consumption
            report.waste_percentage = (total_waste / total_consumption * 100) if total_consumption > 0 else 0

            db.session.commit()

            return StockReportGenerator.get_report(report.id)

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error generating daily stock report: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_report(report_id):
        """
        Get a stock report by ID

        Args:
            report_id: Report ID

        Returns:
            dict: Report data
        """
        try:
            # Get report
            report = DailyStockReport.query.get_or_404(report_id)

            # Get report items
            items = DailyStockReportItem.query.filter_by(report_id=report_id).all()

            # Format items
            formatted_items = []
            for item in items:
                raw_material = RawMaterial.query.get(item.raw_material_id)

                formatted_items.append({
                    'id': item.id,
                    'raw_material_id': item.raw_material_id,
                    'raw_material_name': raw_material.name if raw_material else 'Unknown',
                    'category': raw_material.category if raw_material else None,
                    'opening_quantity': item.opening_quantity,
                    'received_quantity': item.received_quantity,
                    'consumed_quantity': item.consumed_quantity,
                    'waste_quantity': item.waste_quantity,
                    'adjusted_quantity': item.adjusted_quantity,
                    'closing_quantity': item.closing_quantity,
                    'unit': item.unit,
                    'unit_cost': item.unit_cost,
                    'total_value': item.total_value,
                    'status': item.status
                })

            # Format report
            result = {
                'success': True,
                'report': {
                    'id': report.id,
                    'report_date': report.report_date.strftime('%Y-%m-%d'),
                    'branch_id': report.branch_id,
                    'status': report.status,
                    'total_items': report.total_items,
                    'low_stock_items': report.low_stock_items,
                    'out_of_stock_items': report.out_of_stock_items,
                    'total_value': report.total_value,
                    'total_consumption': report.total_consumption,
                    'waste_percentage': report.waste_percentage,
                    'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'items': formatted_items
                }
            }

            return result

        except Exception as e:
            current_app.logger.error(f"Error getting stock report: {str(e)}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def export_report_csv(report_id):
        """
        Export a stock report as CSV

        Args:
            report_id: Report ID

        Returns:
            str: CSV data
        """
        try:
            # Get report data
            report_data = StockReportGenerator.get_report(report_id)

            if not report_data['success']:
                return None

            report = report_data['report']
            items = report['items']

            # Create CSV buffer
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow([
                'Stock Report',
                f"Date: {report['report_date']}",
                f"Branch ID: {report['branch_id']}",
                f"Generated: {report['created_at']}"
            ])

            writer.writerow([])  # Empty row

            # Write summary
            writer.writerow(['Summary'])
            writer.writerow(['Total Items', report['total_items']])
            writer.writerow(['Low Stock Items', report['low_stock_items']])
            writer.writerow(['Out of Stock Items', report['out_of_stock_items']])
            writer.writerow(['Total Value', f"{report['total_value']:.2f}"])
            writer.writerow(['Total Consumption', f"{report['total_consumption']:.2f}"])
            writer.writerow(['Waste Percentage', f"{report['waste_percentage']:.2f}%"])

            writer.writerow([])  # Empty row

            # Write items header
            writer.writerow([
                'Item',
                'Category',
                'Opening',
                'Received',
                'Consumed',
                'Waste',
                'Adjusted',
                'Closing',
                'Unit',
                'Unit Cost',
                'Total Value',
                'Status'
            ])

            # Write items
            for item in items:
                writer.writerow([
                    item['raw_material_name'],
                    item['category'] or 'N/A',
                    f"{item['opening_quantity']:.2f}",
                    f"{item['received_quantity']:.2f}",
                    f"{item['consumed_quantity']:.2f}",
                    f"{item['waste_quantity']:.2f}",
                    f"{item['adjusted_quantity']:.2f}",
                    f"{item['closing_quantity']:.2f}",
                    item['unit'],
                    f"{item['unit_cost']:.2f}",
                    f"{item['total_value']:.2f}",
                    item['status'].replace('_', ' ').title()
                ])

            # Get CSV data
            csv_data = output.getvalue()
            output.close()

            return csv_data

        except Exception as e:
            current_app.logger.error(f"Error exporting stock report as CSV: {str(e)}")
            return None
