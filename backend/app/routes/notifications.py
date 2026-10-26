"""User notifications."""

from flask import Blueprint, jsonify, request

from app.auth import token_required
from app.extensions import db
from app.models.community import Notification
from app.models.user import User as UserModel

bp = Blueprint('notifications', __name__)


@bp.route('/api/community/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    """
    Phase 9: Get user notifications
    
    Notification fields:
    - user_id: Recipient of notification
    - type: Notification type (NEW_MESSAGE, NEW_COMMENT, COMMUNITY_JOIN, POST_LIKE, etc.)
    - reference_id: Entity ID (entity_id in model)
    - is_read: Read status
    - timestamp: Created at
    
    Query Parameters:
    - unread_only: Filter unread notifications (true/false, default false)
    - limit: Maximum number of notifications (default 50, max 100)
    - type: Filter by notification type (optional)
    
    Returns: {success, notifications, unread_count, total_count}
    """
    try:
        
        # Get query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = int(request.args.get('limit', 50))
        limit = min(max(limit, 1), 100)
        notification_type = request.args.get('type', None)
        
        # Build query
        query = Notification.query.filter_by(user_id=current_user, is_deleted=False)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        if notification_type:
            query = query.filter_by(type=notification_type)
        
        # Get notifications
        notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
        
        # Get unread count
        unread_count = Notification.query.filter_by(
            user_id=current_user,
            is_read=False,
            is_deleted=False
        ).count()
        
        # Get total count
        total_count = Notification.query.filter_by(
            user_id=current_user,
            is_deleted=False
        ).count()
        
        # Format notifications for Phase 9
        formatted_notifications = []
        for n in notifications:
            notification_data = n.to_dict(include_actor=True)
            # Add Phase 9 fields
            notification_data['reference_id'] = n.entity_id
            notification_data['timestamp'] = n.created_at.isoformat() if n.created_at else None
            # Ensure actor_name is always present if actor_id exists but relationship wasn't loaded
            if n.actor_id and 'actor_name' not in notification_data:
                actor = UserModel.query.get(n.actor_id)
                if actor:
                    notification_data['actor_name'] = actor.name
            formatted_notifications.append(notification_data)
        
        return jsonify({
            'success': True,
            'notifications': formatted_notifications,
            'unread_count': unread_count,
            'total_count': total_count,
            'count': len(formatted_notifications)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/notifications/read', methods=['POST'])
@token_required
def mark_notifications_read(current_user):
    """
    Phase 9: Mark notification(s) as read
    
    Accepts:
    - notification_id: Single notification ID (optional)
    - notification_ids: Array of notification IDs (optional)
    - all: Mark all as read (true/false, optional)
    
    Returns: {success, message, count}
    """
    try:
        from datetime import datetime
        
        data = request.get_json() or {}
        
        # Option 1: Mark all as read
        if data.get('all') == True:
            notifications = Notification.query.filter_by(
                user_id=current_user,
                is_read=False,
                is_deleted=False
            ).all()
            
            count = len(notifications)
            for notification in notifications:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Marked {count} notifications as read',
                'count': count
            }), 200
        
        # Option 2: Mark multiple by IDs
        elif 'notification_ids' in data:
            notification_ids = data['notification_ids']
            
            if not isinstance(notification_ids, list):
                return jsonify({
                    'success': False,
                    'message': 'notification_ids must be an array'
                }), 400
            
            notifications = Notification.query.filter(
                Notification.id.in_(notification_ids),
                Notification.user_id == current_user,
                Notification.is_deleted == False
            ).all()
            
            count = 0
            for notification in notifications:
                if not notification.is_read:
                    notification.is_read = True
                    notification.read_at = datetime.utcnow()
                    count += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Marked {count} notifications as read',
                'count': count
            }), 200
        
        # Option 3: Mark single by ID
        elif 'notification_id' in data:
            notification_id = data['notification_id']
            
            notification = Notification.query.filter_by(
                id=notification_id,
                user_id=current_user,
                is_deleted=False
            ).first()
            
            if not notification:
                return jsonify({
                    'success': False,
                    'message': 'Notification not found'
                }), 404
            
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Notification marked as read',
                'count': 1
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'message': 'Must provide notification_id, notification_ids, or all=true'
            }), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/notifications/<int:notification_id>/read', methods=['POST'])
@token_required
def mark_notification_read_legacy(current_user, notification_id):
    """
    Legacy: Mark notification as read
    Returns: {success, message}
    """
    try:
        from datetime import datetime
        
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user,
            is_deleted=False
        ).first()
        
        if not notification:
            return jsonify({
                'success': False,
                'message': 'Notification not found'
            }), 404
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/notifications/read-all', methods=['POST'])
@token_required
def mark_all_notifications_read_legacy(current_user):
    """
    Legacy: Mark all notifications as read
    Returns: {success, message, count}
    """
    try:
        from datetime import datetime
        
        notifications = Notification.query.filter_by(
            user_id=current_user,
            is_read=False,
            is_deleted=False
        ).all()
        
        count = len(notifications)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Marked {count} notifications as read',
            'count': count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/notifications/<int:notification_id>', methods=['DELETE'])
@token_required
def delete_notification(current_user, notification_id):
    """Delete a single notification for the current user"""
    try:
        notif = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user
        ).first()
        if not notif:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
        notif.is_deleted = True
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
