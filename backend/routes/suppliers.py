"""
Suppliers Management Routes for StockMaster Pro
Handles supplier creation, management, and ordering
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.database.db_setup import db
from backend.database.supplier_models import Supplier, SupplierOrder, SupplierOrderItem
from backend.database.models import RawMaterial
from backend.auth.supabase_auth import role_required
from datetime import datetime

# Blueprint setup
suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@suppliers_bp.route('/')
@login_required
@role_required('manager')
def index():
    """Suppliers index page - list all suppliers"""
    # Get suppliers for current branch
    suppliers = Supplier.query.filter_by(branch_id=current_user.branch_id).all()
    return render_template('suppliers/index.html', suppliers=suppliers)

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_supplier():
    """Add a new supplier"""
    if request.method == 'POST':
        name = request.form.get('name')
        contact_name = request.form.get('contact_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        notes = request.form.get('notes')

        # Create new supplier
        supplier = Supplier(
            name=name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            address=address,
            notes=notes,
            branch_id=current_user.branch_id
        )

        db.session.add(supplier)
        db.session.commit()

        flash('Supplier added successfully', 'success')
        return redirect(url_for('suppliers.index'))

    return render_template('suppliers/add.html')

@suppliers_bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def edit_supplier(supplier_id):
    """Edit an existing supplier"""
    supplier = Supplier.query.get_or_404(supplier_id)

    # Check if supplier belongs to current branch
    if supplier.branch_id != current_user.branch_id:
        flash('You do not have permission to edit this supplier', 'error')
        return redirect(url_for('suppliers.index'))

    if request.method == 'POST':
        supplier.name = request.form.get('name')
        supplier.contact_name = request.form.get('contact_name')
        supplier.email = request.form.get('email')
        supplier.phone = request.form.get('phone')
        supplier.address = request.form.get('address')
        supplier.notes = request.form.get('notes')

        db.session.commit()

        flash('Supplier updated successfully', 'success')
        return redirect(url_for('suppliers.index'))

    return render_template('suppliers/edit.html', supplier=supplier)

@suppliers_bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required
@role_required('manager')
def delete_supplier(supplier_id):
    """Delete a supplier"""
    supplier = Supplier.query.get_or_404(supplier_id)

    # Check if supplier belongs to current branch
    if supplier.branch_id != current_user.branch_id:
        flash('You do not have permission to delete this supplier', 'error')
        return redirect(url_for('suppliers.index'))

    # Check if supplier has orders
    if SupplierOrder.query.filter_by(supplier_id=supplier_id).count() > 0:
        flash('Cannot delete supplier with existing orders', 'error')
        return redirect(url_for('suppliers.index'))

    db.session.delete(supplier)
    db.session.commit()

    flash('Supplier deleted successfully', 'success')
    return redirect(url_for('suppliers.index'))

@suppliers_bp.route('/orders')
@login_required
@role_required('manager')
def orders():
    """List all supplier orders"""
    # Get orders for current branch
    orders = SupplierOrder.query.join(Supplier).filter(Supplier.branch_id == current_user.branch_id).all()
    return render_template('suppliers/orders.html', orders=orders)

@suppliers_bp.route('/orders/add', methods=['GET', 'POST'])
@login_required
@role_required('manager')
def add_order():
    """Add a new supplier order"""
    suppliers = Supplier.query.filter_by(branch_id=current_user.branch_id).all()
    raw_materials = RawMaterial.query.filter_by(branch_id=current_user.branch_id).all()

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        order_date = datetime.now()
        expected_delivery = request.form.get('expected_delivery')
        status = 'pending'
        notes = request.form.get('notes')

        # Create new order
        order = SupplierOrder(
            supplier_id=supplier_id,
            order_date=order_date,
            expected_delivery=expected_delivery,
            status=status,
            notes=notes
        )

        db.session.add(order)
        db.session.commit()

        flash('Order created successfully', 'success')
        return redirect(url_for('suppliers.orders'))

    return render_template('suppliers/add_order.html', suppliers=suppliers, raw_materials=raw_materials)
