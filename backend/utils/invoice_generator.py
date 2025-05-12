"""
Invoice Generator for StockMaster Pro
Generates PDF invoices for subscriptions and orders
"""

import os
import io
import qrcode
from datetime import datetime
from flask import current_app, render_template
from weasyprint import HTML, CSS
from backend.database.subscription_models import SubscriptionInvoice, Subscription

class InvoiceGenerator:
    """
    Invoice Generator for StockMaster Pro
    Generates PDF invoices for subscriptions and orders
    """
    
    @staticmethod
    def generate_subscription_invoice(invoice_id):
        """
        Generate a PDF invoice for a subscription
        
        Args:
            invoice_id: ID of the SubscriptionInvoice
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Get invoice data
            invoice = SubscriptionInvoice.query.get(invoice_id)
            if not invoice:
                raise ValueError(f"Invoice not found: {invoice_id}")
            
            subscription = Subscription.query.get(invoice.subscription_id)
            if not subscription:
                raise ValueError(f"Subscription not found: {invoice.subscription_id}")
            
            shop = subscription.shop
            plan = subscription.plan
            
            # Create invoice data
            invoice_data = {
                'invoice': invoice,
                'subscription': subscription,
                'shop': shop,
                'plan': plan,
                'invoice_date': invoice.issue_date.strftime('%Y-%m-%d'),
                'due_date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                'items': [
                    {
                        'description': f"{plan.name} Subscription ({subscription.billing_cycle})",
                        'quantity': 1,
                        'unit_price': invoice.amount,
                        'total': invoice.amount
                    }
                ],
                'subtotal': invoice.amount,
                'tax': invoice.tax_amount,
                'total': invoice.total_amount,
                'currency': shop.currency or 'SAR',
                'payment_status': invoice.status.upper(),
                'company': {
                    'name': 'StockMaster Pro',
                    'address': '123 Coffee Street, Riyadh, Saudi Arabia',
                    'phone': '+966 12 345 6789',
                    'email': 'billing@stockmasterpro.com',
                    'website': 'www.stockmasterpro.com',
                    'tax_number': '123456789'
                }
            }
            
            # Generate QR code for invoice
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f"Invoice: {invoice.invoice_number}\nAmount: {invoice.total_amount} {shop.currency or 'SAR'}\nDate: {invoice.issue_date.strftime('%Y-%m-%d')}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer)
            qr_base64 = f"data:image/png;base64,{qr_buffer.getvalue().hex()}"
            invoice_data['qr_code'] = qr_base64
            
            # Render HTML template
            html_content = render_template('invoices/subscription_invoice.html', **invoice_data)
            
            # Create PDF
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                }
                body {
                    font-family: Arial, sans-serif;
                }
                .invoice-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                }
                .invoice-title {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .invoice-details {
                    margin-bottom: 20px;
                }
                .invoice-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                .invoice-table th, .invoice-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                .invoice-table th {
                    background-color: #f2f2f2;
                }
                .invoice-total {
                    text-align: right;
                    margin-top: 20px;
                }
                .invoice-footer {
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }
                .paid-stamp {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-30deg);
                    font-size: 72px;
                    color: rgba(0, 128, 0, 0.3);
                    border: 10px solid rgba(0, 128, 0, 0.3);
                    padding: 10px 20px;
                    border-radius: 10px;
                    z-index: 100;
                }
                .unpaid-stamp {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-30deg);
                    font-size: 72px;
                    color: rgba(255, 0, 0, 0.3);
                    border: 10px solid rgba(255, 0, 0, 0.3);
                    padding: 10px 20px;
                    border-radius: 10px;
                    z-index: 100;
                }
            ''')
            
            # Create directory if it doesn't exist
            invoice_dir = os.path.join(current_app.static_folder, 'invoices')
            os.makedirs(invoice_dir, exist_ok=True)
            
            # Generate PDF file path
            pdf_filename = f"invoice_{invoice.invoice_number.replace('-', '_')}.pdf"
            pdf_path = os.path.join(invoice_dir, pdf_filename)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(pdf_path, stylesheets=[css])
            
            # Update invoice with PDF path
            invoice.pdf_path = f"/static/invoices/{pdf_filename}"
            current_app.db.session.commit()
            
            return invoice.pdf_path
            
        except Exception as e:
            current_app.logger.error(f"Error generating invoice PDF: {str(e)}")
            raise
    
    @staticmethod
    def generate_order_invoice(order_id):
        """
        Generate a PDF invoice for an order
        
        Args:
            order_id: ID of the Order
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Get order data
            from backend.database.models import Order, OrderItem, Product
            
            order = Order.query.get(order_id)
            if not order:
                raise ValueError(f"Order not found: {order_id}")
            
            # Get order items
            order_items = OrderItem.query.filter_by(order_id=order_id).all()
            
            # Get branch and shop data
            branch = order.branch
            shop = branch.shop if hasattr(branch, 'shop') else None
            
            # Create invoice data
            invoice_data = {
                'order': order,
                'branch': branch,
                'shop': shop,
                'invoice_number': f"ORD-{order.id}",
                'invoice_date': order.created_at.strftime('%Y-%m-%d'),
                'items': [],
                'subtotal': order.subtotal,
                'tax': order.tax,
                'total': order.total,
                'currency': branch.currency or 'SAR',
                'payment_status': order.payment_status.upper() if hasattr(order, 'payment_status') else 'PAID',
                'company': {
                    'name': shop.name if shop else branch.name,
                    'address': branch.address or '',
                    'phone': branch.phone or '',
                    'email': shop.email if shop else '',
                    'website': shop.website if shop and hasattr(shop, 'website') else '',
                    'tax_number': shop.tax_number if shop and hasattr(shop, 'tax_number') else ''
                }
            }
            
            # Add order items
            for item in order_items:
                product = Product.query.get(item.product_id)
                invoice_data['items'].append({
                    'description': product.name if product else f"Product #{item.product_id}",
                    'quantity': item.quantity,
                    'unit_price': item.unit_price,
                    'total': item.total
                })
            
            # Generate QR code for invoice
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f"Order: {order.id}\nAmount: {order.total} {branch.currency or 'SAR'}\nDate: {order.created_at.strftime('%Y-%m-%d')}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer)
            qr_base64 = f"data:image/png;base64,{qr_buffer.getvalue().hex()}"
            invoice_data['qr_code'] = qr_base64
            
            # Render HTML template
            html_content = render_template('invoices/order_invoice.html', **invoice_data)
            
            # Create PDF (using same CSS as subscription invoice)
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                }
                body {
                    font-family: Arial, sans-serif;
                }
                .invoice-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                }
                .invoice-title {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .invoice-details {
                    margin-bottom: 20px;
                }
                .invoice-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                .invoice-table th, .invoice-table td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                .invoice-table th {
                    background-color: #f2f2f2;
                }
                .invoice-total {
                    text-align: right;
                    margin-top: 20px;
                }
                .invoice-footer {
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                }
                .paid-stamp {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-30deg);
                    font-size: 72px;
                    color: rgba(0, 128, 0, 0.3);
                    border: 10px solid rgba(0, 128, 0, 0.3);
                    padding: 10px 20px;
                    border-radius: 10px;
                    z-index: 100;
                }
                .unpaid-stamp {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-30deg);
                    font-size: 72px;
                    color: rgba(255, 0, 0, 0.3);
                    border: 10px solid rgba(255, 0, 0, 0.3);
                    padding: 10px 20px;
                    border-radius: 10px;
                    z-index: 100;
                }
            ''')
            
            # Create directory if it doesn't exist
            invoice_dir = os.path.join(current_app.static_folder, 'invoices')
            os.makedirs(invoice_dir, exist_ok=True)
            
            # Generate PDF file path
            pdf_filename = f"order_invoice_{order.id}.pdf"
            pdf_path = os.path.join(invoice_dir, pdf_filename)
            
            # Generate PDF
            HTML(string=html_content).write_pdf(pdf_path, stylesheets=[css])
            
            return f"/static/invoices/{pdf_filename}"
            
        except Exception as e:
            current_app.logger.error(f"Error generating order invoice PDF: {str(e)}")
            raise
