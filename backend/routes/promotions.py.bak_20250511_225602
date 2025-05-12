from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database.models import Promotion
from database.db_setup import db
from utils.activity_logger import log_activity
from datetime import datetime
import json

promotions_bp = Blueprint('promotions', __name__)

@promotions_bp.route('/promotions')
@login_required
def promotions():
    active_promotions = Promotion.query.filter(
        Promotion.is_active == True,
        Promotion.end_date >= datetime.utcnow()
    ).all()
    return render_template('promotions.html', promotions=active_promotions)

@promotions_bp.route('/promotions/add', methods=['GET', 'POST'])
@login_required
def add_promotion():
    if request.method == 'POST':
        promotion = Promotion(
            name=request.form['name'],
            description=request.form['description'],
            discount_type=request.form['discount_type'],
            discount_value=float(request.form['discount_value']),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d'),
            min_purchase=float(request.form['min_purchase']),
            max_discount=float(request.form['max_discount']),
            applicable_products=json.dumps(request.form.getlist('products'))
        )
        db.session.add(promotion)
        db.session.commit()
        log_activity(current_user.id, 'create', 'promotion', promotion.id)
        flash('Promotion added successfully')
        return redirect(url_for('promotions.promotions'))
    return render_template('add_promotion.html')