from database.db_setup import db
from database.models import Notification
from datetime import datetime

def create_notification(title, message, type='info', user_id=None):
    """
    Create a new notification
    type can be: 'info', 'success', 'warning', 'error'
    """
    notification = Notification(
        title=title,
        message=message,
        type=type,
        user_id=user_id,
        created_at=datetime.now()
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def get_notifications(user_id=None, unread_only=False, limit=10):
    """Get notifications for a user"""
    query = Notification.query

    if user_id:
        query = query.filter_by(user_id=user_id)

    if unread_only:
        query = query.filter_by(read=False)

    return query.order_by(Notification.created_at.desc()).limit(limit).all()

def mark_notification_read(notification_id):
    """Mark a notification as read"""
    notification = Notification.query.get(notification_id)
    if notification:
        notification.read = True
        notification.read_at = datetime.now()
        db.session.commit()
        return True
    return False

def mark_all_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    Notification.query.filter_by(
        user_id=user_id,
        read=False
    ).update({
        'read': True,
        'read_at': datetime.now()
    })
    db.session.commit()
