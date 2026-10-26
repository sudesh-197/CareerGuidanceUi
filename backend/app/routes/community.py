"""Community groups, recommendations, feed, reach-out and group chat rooms."""

import datetime
import os

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.auth import token_required
from app.config import COMMUNITY_IMAGE_DIR
from app.extensions import db
from app.models.community import Community, CommunityMember, UserProfile
from app.services.community_service import CommunityService

bp = Blueprint('community', __name__)


@bp.route('/api/community/groups', methods=['GET'])
@token_required
def get_community_groups(current_user):
    """
    Get list of community groups
    Returns: {success, communities}
    """
    try:
        communities = CommunityService.get_communities(current_user)
        
        return jsonify({
            'success': True,
            'communities': communities
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/create', methods=['POST'])
@token_required
def create_community(current_user):
    """
    Create a new community
    
    Rules:
    - Only authenticated users can create
    - Creator becomes ADMIN automatically
    - Community name must be unique
    - Automatically joins as first member
    
    Accepts: {name, description, category, tags}
    Returns: {success, community, message}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'name' not in data or 'description' not in data:
            return jsonify({
                'success': False,
                'message': 'Name and description are required'
            }), 400
        
        # Create community
        result = CommunityService.create_community(
            user_id=current_user,
            name=data['name'],
            description=data['description'],
            category=data.get('category', 'General'),
            tags=data.get('tags', [])
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


@bp.route('/api/community/join', methods=['POST'])
@token_required
def join_community(current_user):
    """
    Join a community
    
    Rules:
    - Only authenticated users can join
    - Prevents duplicate membership
    - Creates notification for community admins
    - Updates member count
    
    Accepts: {community_id}
    Returns: {success, message, community}
    """
    try:
        data = request.get_json()
        
        if 'community_id' not in data:
            return jsonify({
                'success': False,
                'message': 'Community ID is required'
            }), 400
        
        # Join community
        result = CommunityService.join_community(
            user_id=current_user,
            community_id=data['community_id']
        )
        
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


@bp.route('/api/community/groups/<int:community_id>', methods=['GET'])
@token_required
def get_community_group(current_user, community_id):
    """Get a single community by ID"""
    try:
        community = Community.query.get(community_id)
        if not community or community.is_deleted:
            return jsonify({'success': False, 'message': 'Community not found'}), 404
        is_member = CommunityMember.query.filter_by(
            community_id=community_id, user_id=current_user, is_deleted=False
        ).first() is not None
        data = community.to_dict()
        data['is_member'] = is_member
        return jsonify({'success': True, 'community': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/community/groups', methods=['POST'])
@token_required
def create_community_group_legacy(current_user):
    """
    Legacy endpoint - redirects to /api/community/create
    """
    return create_community(current_user)


@bp.route('/api/community/groups/<int:community_id>/join', methods=['POST'])
@token_required
def join_community_legacy(current_user, community_id):
    """
    Legacy endpoint - Join a community by ID in URL
    Redirects to /api/community/join
    """
    try:
        result = CommunityService.join_community(current_user, community_id)
        
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


@bp.route('/api/community/groups/<int:community_id>', methods=['DELETE'])
@token_required
def delete_community_group(current_user, community_id):
    """
    Delete a community group (soft delete)
    Only admins/creators can delete
    """
    try:
        result = CommunityService.delete_community(community_id, current_user)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 403
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/recommended', methods=['GET'])
@token_required
def get_recommended_communities(current_user):
    """
    Get recommended communities based on user interests
    Uses vector-based cosine similarity matching
    
    Algorithm:
    1. Get user interests from UserProfile
    2. Get all communities with tags
    3. Build vocabulary from all terms
    4. Convert user interests to binary vector
    5. Convert community tags to binary vectors
    6. Compute cosine similarity for each
    7. Sort by similarity descending
    8. Return top 5 communities
    
    Returns: {success, recommendations, has_profile}
    """
    try:
        # Get limit from query params (default 5)
        limit = int(request.args.get('limit', 5))
        limit = min(max(limit, 1), 20)  # Clamp between 1 and 20
        
        # Get recommendations
        recommendations = CommunityService.get_recommended_communities(
            user_id=current_user,
            limit=limit
        )
        
        # Check if user has profile
        has_profile = UserProfile.query.filter_by(user_id=current_user).first() is not None
        
        # If no recommendations (no profile or no matches), return trending
        if not recommendations:
            recommendations = CommunityService.get_trending_communities(limit=limit)
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'has_profile': has_profile,
                'recommendation_type': 'trending',
                'message': 'Showing trending communities' if not has_profile else 'No matching communities found, showing trending'
            }), 200
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'has_profile': has_profile,
            'recommendation_type': 'personalized'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/feed', methods=['GET'])
@token_required
def get_community_feed(current_user):
    """
    Get personalized ranked feed for user
    
    Ranking Formula:
    rankScore = (0.5 × recencyScore) + (0.3 × engagementScore) + (0.2 × relevanceScore)
    
    Where:
    - recencyScore = e^(-0.1 × hoursSincePost)
    - engagementScore = normalized(likes + 2 × comments)
    - relevanceScore = cosine(userInterests, postTags)
    
    Query Parameters:
    - type: Filter by post type ('blog', 'feedback', or omit for all)
    - limit: Maximum number of posts (default 50, max 100)
    - include_scores: Include score breakdown (true/false, default false)
    
    Returns: {success, feed, stats}
    """
    try:
        # Get query parameters
        post_type = request.args.get('type', None)
        limit = int(request.args.get('limit', 50))
        limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
        include_scores = request.args.get('include_scores', 'false').lower() == 'true'
        
        # Get ranked feed
        feed = CommunityService.get_ranked_feed(
            user_id=current_user,
            post_type=post_type,
            limit=limit,
            include_scores=include_scores
        )
        
        # Get feed stats
        stats = CommunityService.get_feed_stats(current_user)
        
        return jsonify({
            'success': True,
            'feed': feed,
            'stats': stats,
            'personalized': stats['personalization_enabled']
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/feed/trending', methods=['GET'])
@token_required
def get_trending_feed(current_user):
    """
    Get trending posts based on recent engagement
    
    Query Parameters:
    - type: Filter by post type ('blog', 'feedback', or omit for all)
    - hours: Time window in hours (default 24, max 168)
    - limit: Maximum number of posts (default 10, max 50)
    
    Returns: {success, trending}
    """
    try:
        # Get query parameters
        post_type = request.args.get('type', None)
        time_window_hours = int(request.args.get('hours', 24))
        time_window_hours = min(max(time_window_hours, 1), 168)  # Clamp 1-168 hours
        limit = int(request.args.get('limit', 10))
        limit = min(max(limit, 1), 50)  # Clamp between 1 and 50
        
        # Get trending posts
        trending = CommunityService.get_trending_posts(
            post_type=post_type,
            time_window_hours=time_window_hours,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'trending': trending,
            'time_window_hours': time_window_hours
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/reach-out', methods=['GET'])
@bp.route('/api/community/reachout', methods=['GET'])
@token_required
def get_related_profiles(current_user):
    """
    Get related user profiles based on weighted similarity scoring
    
    Phase 7 Weighted Formula:
    score = 0.4 × domainMatch + 0.3 × skillOverlap + 0.2 × experienceMatch + 0.1 × interestMatch
    
    Query Parameters:
    - limit: Maximum number of profiles (default 10, max 50)
    - min_score: Minimum similarity score 0-100 (default 0)
    - include_breakdown: Include detailed score breakdown (true/false, default false)
    
    Returns: {success, profiles, has_profile, count}
    """
    try:
        
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
        
        min_score = float(request.args.get('min_score', 0))
        min_score = min(max(min_score, 0), 100)  # Clamp between 0 and 100
        
        include_breakdown = request.args.get('include_breakdown', 'false').lower() == 'true'
        
        # Check if user has profile (informational only, don't block)
        has_profile = UserProfile.query.filter_by(user_id=current_user).first() is not None
        
        # Get matching profiles
        profiles = CommunityService.get_related_profiles(
            user_id=current_user,
            limit=limit,
            min_score=min_score,
            include_breakdown=include_breakdown
        )
        
        return jsonify({
            'success': True,
            'profiles': profiles,
            'has_profile': True,
            'count': len(profiles),
            'min_score_threshold': min_score
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/<int:community_id>/messages', methods=['GET'])
@token_required
def get_community_messages(current_user, community_id):
    """
    Get all messages in a community chat room
    Only members can view messages
    """
    try:
        # Check if user is a member
        membership = CommunityMember.query.filter_by(
            community_id=community_id,
            user_id=current_user,
            is_deleted=False
        ).first()
        
        if not membership:
            return jsonify({
                'success': False,
                'message': 'You must be a member to view messages'
            }), 403
        
        # Get messages
        messages = CommunityService.get_community_messages(community_id, limit=100)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'count': len(messages)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/message/send', methods=['POST'])
@token_required
def send_community_message(current_user):
    """
    Send a message to a community chat room
    Supports text and image uploads
    """
    try:
        
        community_id = request.form.get('community_id')
        content = request.form.get('content', '').strip()
        image = request.files.get('image')
        
        if not community_id:
            return jsonify({
                'success': False,
                'message': 'Community ID is required'
            }), 400
        
        community_id = int(community_id)
        
        # Check if user is a member
        membership = CommunityMember.query.filter_by(
            community_id=community_id,
            user_id=current_user,
            is_deleted=False
        ).first()
        
        if not membership:
            return jsonify({
                'success': False,
                'message': 'You must be a member to send messages'
            }), 403
        
        # Validate content or image
        if not content and not image:
            return jsonify({
                'success': False,
                'message': 'Message content or image is required'
            }), 400
        
        # Handle image upload
        image_url = None
        if image:
            # Create uploads directory if it doesn't exist
            upload_dir = COMMUNITY_IMAGE_DIR
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            filename = secure_filename(image.filename)
            timestamp = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{current_user}_{timestamp}_{filename}"
            filepath = os.path.join(upload_dir, unique_filename)
            
            # Save image
            image.save(filepath)
            image_url = f"/uploads/community_images/{unique_filename}"
        
        # Send message
        result = CommunityService.send_community_message(
            community_id=community_id,
            user_id=current_user,
            content=content,
            image_url=image_url
        )
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/<int:community_id>/members', methods=['GET'])
@token_required
def get_community_members(current_user, community_id):
    """
    Get all members of a community
    Only members can view the member list
    """
    try:
        # Check if user is a member
        membership = CommunityMember.query.filter_by(
            community_id=community_id,
            user_id=current_user,
            is_deleted=False
        ).first()
        
        if not membership:
            return jsonify({
                'success': False,
                'message': 'You must be a member to view members'
            }), 403
        
        # Get members
        members = CommunityService.get_community_members(community_id)
        
        return jsonify({
            'success': True,
            'members': members,
            'count': len(members)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
