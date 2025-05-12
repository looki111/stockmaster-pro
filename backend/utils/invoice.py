from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
import os
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import qrcode
import json

class InvoiceGenerator:
    def __init__(self, order):
        self.order = order
        self.styles = getSampleStyleSheet()
        self.setup_fonts()
        
    def setup_fonts(self):
        """Setup fonts for both Arabic and English text"""
        # Register fonts (you'll need to add the font files to your project)
        font_path = os.path.join(os.path.dirname(__file__), '../static/fonts')
        
        # English font
        pdfmetrics.registerFont(TTFont('Helvetica', os.path.join(font_path, 'Helvetica.ttf')))
        
        # Arabic font
        pdfmetrics.registerFont(TTFont('Arial', os.path.join(font_path, 'arial.ttf')))
        
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='Arabic',
            fontName='Arial',
            fontSize=12,
            alignment=2  # Right alignment
        ))
        
        self.styles.add(ParagraphStyle(
            name='English',
            fontName='Helvetica',
            fontSize=12,
            alignment=0  # Left alignment
        ))
    
    def generate_qr_code(self):
        """Generate QR code with order information"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add order data to QR code
        qr_data = {
            'invoice_number': self.order.invoice_number,
            'date': self.order.created_at.isoformat(),
            'total': self.order.total,
            'items': len(self.order.items)
        }
        
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code temporarily
        qr_path = os.path.join(os.path.dirname(__file__), f'../static/temp/qr_{self.order.invoice_number}.png')
        qr_img.save(qr_path)
        
        return qr_path
    
    def create_header(self):
        """Create invoice header with logo and business information"""
        elements = []
        
        # Add logo
        logo_path = os.path.join(os.path.dirname(__file__), '../static/images/logo.png')
        if os.path.exists(logo_path):
            img = Image(logo_path, width=2*inch, height=1*inch)
            elements.append(img)
        
        # Add business information
        elements.append(Paragraph(f"<b>Invoice #{self.order.invoice_number}</b>", self.styles['English']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add date
        date_str = self.order.created_at.strftime("%Y-%m-%d %H:%M")
        elements.append(Paragraph(f"Date: {date_str}", self.styles['English']))
        
        return elements
    
    def create_customer_info(self):
        """Create customer information section"""
        elements = []
        
        if self.order.client:
            client = self.order.client
            elements.append(Paragraph("<b>Customer Information</b>", self.styles['English']))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(f"Name: {client.name}", self.styles['English']))
            elements.append(Paragraph(f"Phone: {client.phone}", self.styles['English']))
            if client.email:
                elements.append(Paragraph(f"Email: {client.email}", self.styles['English']))
        
        return elements
    
    def create_items_table(self):
        """Create table of ordered items"""
        elements = []
        
        # Table header
        data = [['Item', 'Quantity', 'Unit Price', 'Total']]
        
        # Add items
        for item in self.order.items:
            data.append([
                item.product.name,
                str(item.quantity),
                f"${item.unit_price:.2f}",
                f"${item.total_price:.2f}"
            ])
        
        # Create table
        table = Table(data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def create_totals(self):
        """Create totals section"""
        elements = []
        
        # Add subtotal, tax, and total
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"Subtotal: ${self.order.subtotal:.2f}", self.styles['English']))
        elements.append(Paragraph(f"Tax: ${self.order.tax:.2f}", self.styles['English']))
        elements.append(Paragraph(f"<b>Total: ${self.order.total:.2f}</b>", self.styles['English']))
        
        # Add loyalty points if applicable
        if self.order.loyalty_points_earned > 0:
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph(
                f"Loyalty Points Earned: {self.order.loyalty_points_earned}",
                self.styles['English']
            ))
        
        return elements
    
    def generate(self):
        """Generate the complete PDF invoice"""
        # Create PDF document
        output_path = os.path.join(
            os.path.dirname(__file__),
            f'../static/invoices/invoice_{self.order.invoice_number}.pdf'
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build document content
        elements = []
        
        # Add header
        elements.extend(self.create_header())
        elements.append(Spacer(1, 0.5*inch))
        
        # Add customer information
        elements.extend(self.create_customer_info())
        elements.append(Spacer(1, 0.3*inch))
        
        # Add items table
        elements.extend(self.create_items_table())
        
        # Add totals
        elements.extend(self.create_totals())
        
        # Add QR code
        qr_path = self.generate_qr_code()
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Image(qr_path, width=1.5*inch, height=1.5*inch))
        
        # Build PDF
        doc.build(elements)
        
        # Clean up temporary QR code
        os.remove(qr_path)
        
        return output_path
