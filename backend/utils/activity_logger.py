from database.models import ActivityLog
from database.db_setup import db
from flask import request
from datetime import datetime

def log_activity(user_id, action, entity_type, entity_id, details=None):
    """
    Log user activity in the system

    Args:
        user_id (int): ID of the user performing the action
        action (str): Type of action (create, update, delete, etc.)
        entity_type (str): Type of entity being affected (order, product, etc.)
        entity_id (int): ID of the entity being affected
        details (str, optional): Additional details about the activity
    """
    try:
        # Get client IP address
        ip_address = request.remote_addr

        # Create activity log entry
        log = ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )

        db.session.add(log)
        db.session.commit()

        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error logging activity: {str(e)}")
        return False

def get_user_activities(user_id, limit=50):
    """
    Get recent activities for a specific user

    Args:
        user_id (int): ID of the user
        limit (int): Maximum number of activities to return

    Returns:
        list: List of activity log entries
    """
    return ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.created_at.desc())\
        .limit(limit)\
        .all()

def get_entity_activities(entity_type, entity_id, limit=50):
    """
    Get recent activities for a specific entity

    Args:
        entity_type (str): Type of entity
        entity_id (int): ID of the entity
        limit (int): Maximum number of activities to return

    Returns:
        list: List of activity log entries
    """
    return ActivityLog.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(ActivityLog.created_at.desc())\
     .limit(limit)\
     .all()

def get_recent_activities(limit=50):
    """
    Get most recent activities across all users

    Args:
        limit (int): Maximum number of activities to return

    Returns:
        list: List of activity log entries
    """
    return ActivityLog.query.order_by(ActivityLog.created_at.desc())\
        .limit(limit)\
        .all()

def format_activity_message(log):
    """
    Format activity log entry into a human-readable message

    Args:
        log (ActivityLog): Activity log entry

    Returns:
        str: Formatted message
    """
    action_map = {
        'create': 'created',
        'update': 'updated',
        'delete': 'deleted',
        'login': 'logged in',
        'logout': 'logged out',
        'view': 'viewed'
    }

    action = action_map.get(log.action, log.action)
    return f"{log.user.username} {action} {log.entity_type} #{log.entity_id}"