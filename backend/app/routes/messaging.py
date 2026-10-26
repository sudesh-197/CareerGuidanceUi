"""Direct messages between users."""

from flask import Blueprint, jsonify, request

from app.auth import token_required
from app.extensions import db
from app.models.community import Conversation
from app.services.community_service import CommunityService

bp = Blueprint('messaging', __name__)


@bp.route('/api/community/message', methods=['POST'])
@token_required
def send_message_v2(current_user):
    """
    Phase 8: Send a message to another user
    
    Logic:
    - Create conversation if not exists
    - Store message
    - Mark unread for receiver
    - Trigger notification event
    
    Accepts: {recipient_id, content}
    Returns: {success, message, conversation_id}
    """
    try:
        data = request.get_json()
        
        if 'recipient_id' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'Recipient ID and content are required'
            }), 400
        
        result = CommunityService.send_message(
            sender_id=current_user,
            recipient_id=data['recipient_id'],
            content=data['content']
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/messages/<int:conversation_id>', methods=['GET'])
@token_required
def get_conversation_messages(current_user, conversation_id):
    """
    Phase 8: Get messages from a specific conversation
    
    Query Parameters:
    - limit: Maximum number of messages (default 100, max 500)
    
    Returns: {success, messages, conversation_id}
    """
    try:
        
        # Get conversation
        conversation = Conversation.query.get(conversation_id)
        
        if not conversation or conversation.is_deleted:
            return jsonify({
                'success': False,
                'message': 'Conversation not found'
            }), 404
        
        # Verify user is participant
        if conversation.user1_id != current_user and conversation.user2_id != current_user:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access to conversation'
            }), 403
        
        # Get other user ID
        other_user_id = conversation.user2_id if conversation.user1_id == current_user else conversation.user1_id
        
        # Get limit from query params
        limit = int(request.args.get('limit', 100))
        limit = min(max(limit, 1), 500)  # Clamp between 1 and 500
        
        # Get messages (this also marks them as read)
        messages = CommunityService.get_messages(current_user, other_user_id, limit=limit)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'conversation_id': conversation_id,
            'count': len(messages)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/conversations', methods=['GET'])
@token_required
def get_conversations(current_user):
    """
    Get all conversations for the current user
    
    Query Parameters:
    - limit: Maximum number of conversations (default 50, max 100)
    
    Returns: {success, conversations, unread_total}
    """
    try:
        # Get limit from query params
        limit = int(request.args.get('limit', 50))
        limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
        
        # Get conversations
        conversations = CommunityService.get_conversations(current_user, limit=limit)
        
        # Calculate total unread
        unread_total = sum(conv['unread_count'] for conv in conversations)
        
        return jsonify({
            'success': True,
            'conversations': conversations,
            'count': len(conversations),
            'unread_total': unread_total
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/conversations/<int:conversation_id>/read', methods=['POST'])
@token_required
def mark_conversation_read(current_user, conversation_id):
    """
    Mark all messages in a conversation as read
    
    Returns: {success, marked_read}
    """
    try:
        result = CommunityService.mark_conversation_read(current_user, conversation_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/messages/user/<int:recipient_id>', methods=['GET'])
@token_required
def get_messages_legacy(current_user, recipient_id):
    """
    Legacy: Get message history with a specific user
    Returns: {success, messages}
    """
    try:
        messages = CommunityService.get_messages(current_user, recipient_id)
        
        return jsonify({
            'success': True,
            'messages': messages
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/messages', methods=['POST'])
@token_required
def send_message_legacy(current_user):
    """
    Legacy: Send a message to another user
    Accepts: {recipient_id, content}
    Returns: {success, message}
    """
    try:
        data = request.get_json()
        
        if 'recipient_id' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'Recipient ID and content are required'
            }), 400
        
        result = CommunityService.send_message(
            sender_id=current_user,
            recipient_id=data['recipient_id'],
            content=data['content']
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/conversations/<int:conversation_id>', methods=['DELETE'])
@token_required
def delete_conversation(current_user, conversation_id):
    """Soft-delete a conversation for the current user"""
    try:
        conv = Conversation.query.filter_by(id=conversation_id).first()
        if not conv:
            return jsonify({'success': False, 'message': 'Conversation not found'}), 404
        if conv.user1_id != current_user and conv.user2_id != current_user:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        conv.is_deleted = True
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
