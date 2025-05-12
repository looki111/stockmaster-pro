
"""
Inventory Routes for StockMaster Pro
Handles inventory management, consumption rules, and stock reports
"""

from flask import Blueprint, render_template, request, redirect, url_for, g, session
from backend.auth.patched_token_verify import login_required

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

# Raw Materials Routes
@inventory_bp.route('/raw-materials')
@login_required
def raw_materials():
    """View raw materials inventory"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/raw_materials.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')

# Add recipes route
@inventory_bp.route('/recipes')
@login_required
def recipes():
    """View product recipes"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/recipes.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')

@inventory_bp.route('/raw-materials/add', methods=['GET', 'POST'])
@login_required
@require_permission('manage_inventory')
def add_raw_material():
    """Add a new raw material"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        unit = request.form.get('unit')
        quantity = request.form.get('quantity')
        alert_threshold = request.form.get('alert_threshold')
        category = request.form.get('category')
        cost_price = request.form.get('cost_price')
        vendor_id = request.form.get('vendor_id')
        expiry_date = request.form.get('expiry_date')
        description = request.form.get('description')

        # Validate required fields
        if not name or not unit:
            flash('Name and unit are required', 'error')
            return redirect(url_for('inventory.add_raw_material'))

        # Create raw material
        raw_material = RawMaterial(
            name=name,
            unit=unit,
            quantity=float(quantity) if quantity else 0,
            alert_threshold=float(alert_threshold) if alert_threshold else 0,
            branch_id=current_user.branch_id,
            shop_id=current_user.branch.shop_id if current_user.branch else None,
            category=category,
            cost_price=float(cost_price) if cost_price else None,
            vendor_id=int(vendor_id) if vendor_id else None,
            expiry_date=datetime.strptime(expiry_date, '%Y-%m-%d') if expiry_date else None,
            description=description,
            status='in_stock'
        )

        db.session.add(raw_material)

        # Create inventory transaction
        if quantity and float(quantity) > 0:
            transaction = InventoryTransaction(
                transaction_type='purchase',
                raw_material_id=raw_material.id,
                quantity=float(quantity),
                unit=unit,
                unit_cost=float(cost_price) if cost_price else None,
                branch_id=current_user.branch_id,
                shop_id=current_user.branch.shop_id if current_user.branch else None,
                created_by=current_user.id,
                notes='Initial inventory'
            )

            db.session.add(transaction)

        db.session.commit()

        flash(f'Raw material {name} added successfully', 'success')
        return redirect(url_for('inventory.raw_materials'))

    # Get vendors for dropdown
    vendors = []  # TODO: Implement vendors

    return render_template(
        'inventory/add_raw_material.html',
        vendors=vendors
    )

@inventory_bp.route('/raw-materials/<int:material_id>/edit', methods=['GET', 'POST'])
@login_required
@require_permission('manage_inventory')
def edit_raw_material(material_id):
    """Edit a raw material"""
    # Get raw material
    raw_material = RawMaterial.query.get_or_404(material_id)

    # Check if user has access to this raw material
    if raw_material.branch_id != current_user.branch_id:
        flash('You do not have permission to edit this raw material', 'error')
        return redirect(url_for('inventory.raw_materials'))

    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        unit = request.form.get('unit')
        alert_threshold = request.form.get('alert_threshold')
        category = request.form.get('category')
        cost_price = request.form.get('cost_price')
        vendor_id = request.form.get('vendor_id')
        expiry_date = request.form.get('expiry_date')
        description = request.form.get('description')

        # Validate required fields
        if not name or not unit:
            flash('Name and unit are required', 'error')
            return redirect(url_for('inventory.edit_raw_material', material_id=material_id))

        # Update raw material
        raw_material.name = name
        raw_material.unit = unit
        raw_material.alert_threshold = float(alert_threshold) if alert_threshold else 0
        raw_material.category = category
        raw_material.cost_price = float(cost_price) if cost_price else None
        raw_material.vendor_id = int(vendor_id) if vendor_id else None
        raw_material.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d') if expiry_date else None
        raw_material.description = description

        db.session.commit()

        flash(f'Raw material {name} updated successfully', 'success')
        return redirect(url_for('inventory.raw_materials'))

    # Get vendors for dropdown
    vendors = []  # TODO: Implement vendors

    return render_template(
        'inventory/edit_raw_material.html',
        raw_material=raw_material,
        vendors=vendors
    )

@inventory_bp.route('/raw-materials/<int:material_id>/adjust', methods=['GET', 'POST'])
@login_required
@require_permission('manage_inventory')
def adjust_raw_material(material_id):
    """Adjust raw material quantity"""
    # Get raw material
    raw_material = RawMaterial.query.get_or_404(material_id)

    # Check if user has access to this raw material
    if raw_material.branch_id != current_user.branch_id:
        flash('You do not have permission to adjust this raw material', 'error')
        return redirect(url_for('inventory.raw_materials'))

    if request.method == 'POST':
        # Get form data
        adjustment_type = request.form.get('adjustment_type')
        quantity = request.form.get('quantity')
        reason = request.form.get('reason')
        notes = request.form.get('notes')

        # Validate required fields
        if not adjustment_type or not quantity or not reason:
            flash('Adjustment type, quantity, and reason are required', 'error')
            return redirect(url_for('inventory.adjust_raw_material', material_id=material_id))

        # Convert quantity to float
        quantity = float(quantity)

        # Calculate new quantity
        if adjustment_type == 'add':
            new_quantity = raw_material.quantity + quantity
            transaction_quantity = quantity
        elif adjustment_type == 'subtract':
            if quantity > raw_material.quantity:
                flash('Cannot subtract more than current quantity', 'error')
                return redirect(url_for('inventory.adjust_raw_material', material_id=material_id))
            new_quantity = raw_material.quantity - quantity
            transaction_quantity = -quantity
        else:
            new_quantity = quantity
            transaction_quantity = quantity - raw_material.quantity

        # Update raw material
        raw_material.quantity = new_quantity

        # Create inventory transaction
        transaction = InventoryTransaction(
            transaction_type='adjustment',
            raw_material_id=raw_material.id,
            quantity=transaction_quantity,
            unit=raw_material.unit,
            unit_cost=raw_material.cost_price,
            branch_id=current_user.branch_id,
            shop_id=current_user.branch.shop_id if current_user.branch else None,
            created_by=current_user.id,
            notes=f"{reason}: {notes}"
        )

        db.session.add(transaction)
        db.session.commit()

        flash(f'Raw material quantity adjusted successfully', 'success')
        return redirect(url_for('inventory.raw_materials'))

    return render_template(
        'inventory/adjust_raw_material.html',
        raw_material=raw_material
    )

# Consumption Rules Routes
@inventory_bp.route('/consumption-rules')
@login_required
@require_permission('view_inventory')
def consumption_rules():
    """View consumption rules"""
    # Get query parameters
    product_id = request.args.get('product_id')
    raw_material_id = request.args.get('raw_material_id')

    # Get consumption rules
    rules = InventoryController.get_consumption_rules(
        product_id=product_id,
        raw_material_id=raw_material_id
    )

    # Get products and raw materials for filters
    branch_id = current_user.branch_id
    products = Product.query.filter_by(branch_id=branch_id).all()
    raw_materials = RawMaterial.query.filter_by(branch_id=branch_id).all()

    return render_template(
        'inventory/consumption_rules.html',
        rules=rules,
        products=products,
        raw_materials=raw_materials,
        selected_product_id=product_id,
        selected_raw_material_id=raw_material_id
    )

@inventory_bp.route('/consumption-rules/add', methods=['GET', 'POST'])
@login_required
@require_permission('manage_inventory')
def add_consumption_rule():
    """Add a new consumption rule"""
    if request.method == 'POST':
        # Get form data
        product_id = request.form.get('product_id')
        raw_material_id = request.form.get('raw_material_id')
        quantity = request.form.get('quantity')
        unit = request.form.get('unit')
        waste_factor = request.form.get('waste_factor')
        condition_type = request.form.get('condition_type')
        condition_value = request.form.get('condition_value')

        # Create consumption rule
        result = InventoryController.create_consumption_rule(
            data={
                'product_id': product_id,
                'raw_material_id': raw_material_id,
                'quantity': quantity,
                'unit': unit,
                'waste_factor': waste_factor,
                'condition_type': condition_type,
                'condition_value': condition_value
            },
            user_id=current_user.id
        )

        if result['success']:
            flash('Consumption rule added successfully', 'success')
            return redirect(url_for('inventory.consumption_rules'))
        else:
            flash(f'Error adding consumption rule: {result["error"]}', 'error')
            return redirect(url_for('inventory.add_consumption_rule'))

    # Get products and raw materials for dropdowns
    branch_id = current_user.branch_id
    products = Product.query.filter_by(branch_id=branch_id).all()
    raw_materials = RawMaterial.query.filter_by(branch_id=branch_id).all()

    return render_template(
        'inventory/add_consumption_rule.html',
        products=products,
        raw_materials=raw_materials
    )

# Stock Reports Routes
@inventory_bp.route('/reports')
@login_required
def reports():
    """View stock reports"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('inventory/stock_reports.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')

@inventory_bp.route('/reports/generate', methods=['GET', 'POST'])
@login_required
@require_permission('manage_inventory')
def generate_report():
    """Generate a new stock report"""
    if request.method == 'POST':
        # Get form data
        report_date = request.form.get('report_date')

        # Generate report
        result = StockReportGenerator.generate_daily_report(
            branch_id=current_user.branch_id,
            report_date=report_date
        )

        if result['success']:
            flash('Stock report generated successfully', 'success')
            return redirect(url_for('inventory.view_report', report_id=result['report']['id']))
        else:
            flash(f'Error generating report: {result["error"]}', 'error')
            return redirect(url_for('inventory.generate_report'))

    return render_template(
        'inventory/generate_report.html',
        today=date.today().strftime('%Y-%m-%d')
    )

@inventory_bp.route('/reports/<int:report_id>')
@login_required
@require_permission('view_reports')
def view_report(report_id):
    """View a stock report"""
    # Get report
    result = StockReportGenerator.get_report(report_id)

    if not result['success']:
        flash(f'Error loading report: {result["error"]}', 'error')
        return redirect(url_for('inventory.reports'))

    report = result['report']

    # Check if user has access to this report
    if report['branch_id'] != current_user.branch_id:
        flash('You do not have permission to view this report', 'error')
        return redirect(url_for('inventory.reports'))

    return render_template(
        'inventory/view_report.html',
        report=report
    )

@inventory_bp.route('/reports/<int:report_id>/export')
@login_required
@require_permission('view_reports')
def export_report(report_id):
    """Export a stock report as CSV"""
    # Get report
    result = StockReportGenerator.get_report(report_id)

    if not result['success']:
        flash(f'Error loading report: {result["error"]}', 'error')
        return redirect(url_for('inventory.reports'))

    report = result['report']

    # Check if user has access to this report
    if report['branch_id'] != current_user.branch_id:
        flash('You do not have permission to export this report', 'error')
        return redirect(url_for('inventory.reports'))

    # Generate CSV
    csv_data = StockReportGenerator.export_report_csv(report_id)

    if not csv_data:
        flash('Error generating CSV', 'error')
        return redirect(url_for('inventory.view_report', report_id=report_id))

    # Create in-memory file
    buffer = io.StringIO(csv_data)

    # Generate filename
    filename = f"stock_report_{report['report_date']}.csv"

    # Send file
    return send_file(
        io.BytesIO(buffer.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

