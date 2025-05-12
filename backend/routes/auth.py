from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from database.models import User, Role, Branch
from database.db_setup import db
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Blueprint setup
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route - handles login form submission and renders login page
    """
    # Clear session data except for language preference
    lang = session.get('lang', 'ar')
    session.clear()
    session['lang'] = lang

    # If user is already authenticated, redirect to dashboard
    if current_user.is_authenticated:
        logging.info(f"User {current_user.username} already authenticated")
        try:
            return redirect(url_for('dashboard.dashboard'))
        except Exception as e:
            logging.error(f"Error redirecting to dashboard: {e}")
            # Fallback to a static path if url_for fails
            return redirect('/dashboard')

    # Process login form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        logging.info(f"Login attempt for user: {username}")

        try:
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, password):
                logging.info(f"Valid credentials for user: {username}")

                # Ensure user has a branch
                if not user.branch_id:
                    logging.info("User has no branch, assigning one")
                    branch = Branch.query.first()
                    if not branch:
                        logging.info("Creating main branch")
                        branch = Branch(name="Main Branch", is_active=True, is_main=True)
                        db.session.add(branch)
                    user.branch_id = branch.id
                    db.session.commit()

                # Login user
                login_user(user)
                logging.info(f"User {username} logged in successfully")

                # Update last login time
                user.last_login = datetime.now(timezone.utc)
                db.session.commit()

                # Redirect to dashboard
                logging.info("Redirecting to dashboard")
                try:
                    return redirect(url_for('dashboard.dashboard'))
                except Exception as e:
                    logging.error(f"Error redirecting to dashboard: {e}")
                    # Fallback to a static path
                    return redirect('/dashboard')
            else:
                logging.warning(f"Invalid credentials for user: {username}")
                flash('Invalid username or password', 'error')
        except Exception as e:
            logging.error(f"Login error: {e}")
            flash('An error occurred. Please try again.', 'error')
            db.session.rollback()

    # GET request - render login page
    logging.info("Rendering modern login page")
    try:
        # Get language preference from session or default to English
        lang = session.get('lang', 'en')
        theme = session.get('theme', 'light')

        # Try to render the modern login template
        return render_template('login_modern.html', lang=lang, theme=theme)
    except Exception as e:
        logging.error(f"Error rendering login_modern.html: {e}")
        # Fallback to enhanced login template
        try:
            return render_template('login_enhanced.html', lang=lang, theme=theme)
        except Exception as e2:
            logging.error(f"Error rendering login_enhanced.html: {e2}")
            # Last resort - return a simple login form
            return render_template('login.html', lang=lang, theme=theme)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if User.query.filter_by(username=username).first():
            flash('اسم المستخدم موجود بالفعل', 'error')
            return redirect(url_for('auth.register'))

        # Ensure there is at least one branch
        branch = Branch.query.first()
        if not branch:
            branch = Branch(name="الفرع الرئيسي")
            db.session.add(branch)
            db.session.commit()

        # Create user with default role and assign branch
        user = User(
            username=username,
            password=generate_password_hash(password),
            email=email,
            coffee_name=username,  # Default coffee name
            is_active=True,
            branch_id=branch.id
        )

        # Assign default role (cashier)
        cashier_role = Role.query.filter_by(name='cashier').first()
        if cashier_role:
            user.roles.append(cashier_role)

        db.session.add(user)
        db.session.commit()

        flash('تم إنشاء الحساب بنجاح', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register_new.html')

@auth_bp.route('/logout')
def logout():
    """
    Logout route - ALWAYS renders the login page directly to break redirect loops
    """
    # Clear all session data
    session.clear()

    # Logout the user
    logout_user()

    # Redirect to login page
    return redirect(url_for('.login'))