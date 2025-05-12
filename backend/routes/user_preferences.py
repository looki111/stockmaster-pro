"""
User Preferences API for StockMaster Pro
Handles saving and retrieving user preferences like theme, language, etc.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from database.models import UserPreference
from database.db_setup import db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Blueprint setup
user_preferences_bp = Blueprint('user_preferences', __name__, url_prefix='/api/user')

@user_preferences_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Get all user preferences"""
    try:
        # Get all preferences for the current user
        preferences = UserPreference.query.filter_by(user_id=current_user.id).all()
        
        # Convert to dictionary format
        prefs_dict = {pref.key: pref.value for pref in preferences}
        
        return jsonify({
            'success': True,
            'preferences': prefs_dict
        })
    except Exception as e:
        logging.error(f"Error retrieving user preferences: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve preferences'
        }), 500

@user_preferences_bp.route('/preferences', methods=['POST'])
@login_required
def save_preference():
    """Save a user preference"""
    try:
        # Get data from request
        data = request.json
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        key = data['key']
        value = data['value']
        
        # Validate key
        allowed_keys = ['theme', 'theme_color', 'language', 'sidebar_collapsed', 'dashboard_layout']
        if key not in allowed_keys:
            return jsonify({
                'success': False,
                'error': f'Invalid preference key. Allowed keys: {", ".join(allowed_keys)}'
            }), 400
        
        # Check if preference already exists
        preference = UserPreference.query.filter_by(
            user_id=current_user.id,
            key=key
        ).first()
        
        if preference:
            # Update existing preference
            preference.value = value
        else:
            # Create new preference
            preference = UserPreference(
                user_id=current_user.id,
                key=key,
                value=value
            )
            db.session.add(preference)
        
        # Save changes
        db.session.commit()
        
        # Apply certain preferences to the user's session
        if key == 'language':
            # Set session language variable if language preference is changed
            session['lang'] = value
        
        return jsonify({
            'success': True,
            'message': 'Preference saved successfully'
        })
    except Exception as e:
        logging.error(f"Error saving user preference: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to save preference'
        }), 500

@user_preferences_bp.route('/preferences/<key>', methods=['DELETE'])
@login_required
def delete_preference(key):
    """Delete a user preference"""
    try:
        # Find preference
        preference = UserPreference.query.filter_by(
            user_id=current_user.id,
            key=key
        ).first()
        
        if not preference:
            return jsonify({
                'success': False,
                'error': 'Preference not found'
            }), 404
        
        # Delete preference
        db.session.delete(preference)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preference deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting user preference: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete preference'
        }), 500 