from flask import Blueprint, render_template, request, redirect, url_for, g, session
from backend.auth.patched_token_verify import login_required

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

@clients_bp.route('/')
@login_required
def index():
    """Clients index route - shows clients overview"""
    # Get current user from Supabase
    user = getattr(g, 'supabase_user', None)
    if not user:
        # Store the current URL in session for redirect after login
        session['next_url'] = request.path
        return redirect(url_for('supabase_auth.login'))

    # Simplified version without database access
    return render_template('clients.html', lang=request.args.get('lang', 'en'), base_template='base_new.html')

@clients_bp.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        notes = request.form.get('notes')

        # Create new client
        client = Client(
            name=name,
            email=email,
            phone=phone,
            address=address,
            notes=notes,
            branch_id=current_user.branch_id,
            created_at=datetime.utcnow()
        )

        try:
            db.session.add(client)
            db.session.commit()

            # Log activity
            activity = ActivityLog(
                user_id=current_user.id,
                branch_id=current_user.branch_id,
                action='add_client',
                details=f'Added new client: {name}',
                created_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()

            flash('Client added successfully', 'success')
            return redirect(url_for('clients.clients_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding client', 'error')
            return redirect(url_for('clients.add_client'))

    return render_template('add_client.html')

@clients_bp.route('/clients/<int:client_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.filter_by(id=client_id, branch_id=current_user.branch_id).first_or_404()

    if request.method == 'POST':
        client.name = request.form.get('name')
        client.email = request.form.get('email')
        client.phone = request.form.get('phone')
        client.address = request.form.get('address')
        client.notes = request.form.get('notes')
        client.updated_at = datetime.utcnow()

        try:
            db.session.commit()

            # Log activity
            activity = ActivityLog(
                user_id=current_user.id,
                branch_id=current_user.branch_id,
                action='edit_client',
                details=f'Edited client: {client.name}',
                created_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()

            flash('Client updated successfully', 'success')
            return redirect(url_for('clients.clients_list'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating client', 'error')
            return redirect(url_for('clients.edit_client', client_id=client_id))

    return render_template('edit_client.html', client=client)

@clients_bp.route('/clients/<int:client_id>/delete', methods=['POST'])
@login_required
def delete_client(client_id):
    client = Client.query.filter_by(id=client_id, branch_id=current_user.branch_id).first_or_404()

    try:
        # Log activity before deleting
        activity = ActivityLog(
            user_id=current_user.id,
            branch_id=current_user.branch_id,
            action='delete_client',
            details=f'Deleted client: {client.name}',
            created_at=datetime.utcnow()
        )
        db.session.add(activity)

        db.session.delete(client)
        db.session.commit()
        flash('Client deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting client', 'error')

    return redirect(url_for('clients.clients_list'))

@clients_bp.route('/clients/search')
@login_required
def search_clients():
    query = request.args.get('q', '')
    clients = Client.query.filter(
        Client.branch_id == current_user.branch_id,
        Client.name.ilike(f'%{query}%')
    ).all()

    return jsonify([{
        'id': client.id,
        'name': client.name,
        'email': client.email,
        'phone': client.phone,
        'address': client.address,
        'loyalty_points': client.loyalty_points,
        'total_spent': client.total_spent
    } for client in clients])