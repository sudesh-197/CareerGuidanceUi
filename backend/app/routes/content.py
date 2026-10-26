"""Community content: blogs, feedback, posts, comments and likes."""

import os
import uuid

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.auth import token_required
from app.config import VIDEO_DIR
from app.extensions import db
from app.services.community_service import CommunityService

bp = Blueprint('content', __name__)


@bp.route('/api/community/feedback', methods=['GET'])
@token_required
def get_feedback(current_user):
    """
    Get all feedback posts
    Returns: {success, feedbacks}
    """
    try:
        feedbacks = CommunityService.get_feedback()
        
        return jsonify({
            'success': True,
            'feedbacks': feedbacks
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/feedback', methods=['POST'])
@token_required
def submit_feedback(current_user):
    """
    Submit new feedback
    Accepts: {content, category}
    Returns: {success, feedback}
    """
    try:
        data = request.get_json()
        
        if 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'Content is required'
            }), 400
        
        feedback = CommunityService.submit_feedback(
            user_id=current_user,
            content=data['content'],
            category=data.get('category', 'General')
        )
        
        return jsonify({
            'success': True,
            'feedback': feedback
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/feedback/<int:post_id>', methods=['DELETE'])
@token_required
def delete_feedback_post(current_user, post_id):
    """
    Delete a feedback post (soft delete)
    Only the author can delete
    """
    try:
        result = CommunityService.delete_feedback(post_id, current_user)
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


@bp.route('/api/community/blogs', methods=['GET'])
@token_required
def get_blogs(current_user):
    """
    Get all blog posts
    Returns: {success, blogs}
    """
    try:
        blogs = CommunityService.get_blogs()
        
        return jsonify({
            'success': True,
            'blogs': blogs
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/blogs', methods=['POST'])
@token_required
def create_blog(current_user):
    """
    Create a new blog post with optional video upload
    Accepts: multipart/form-data with fields: title, content, tags, video (file)
    Returns: {success, blog}
    """
    try:
        
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        tags_str = request.form.get('tags', '')
        
        if not title or not content:
            return jsonify({
                'success': False,
                'message': 'Title and content are required'
            }), 400
        
        # Parse tags
        tags = []
        if tags_str:
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Handle video file upload
        video_path = None
        if 'video' in request.files:
            video_file = request.files['video']
            if video_file and video_file.filename:
                # Validate file extension
                allowed_extensions = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv', 'mpeg', 'mpg'}
                filename = secure_filename(video_file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                if file_ext not in allowed_extensions:
                    return jsonify({
                        'success': False,
                        'message': f'Invalid video format. Allowed: {", ".join(allowed_extensions)}'
                    }), 400
                
                # Create unique filename
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Ensure upload directory exists
                upload_dir = VIDEO_DIR
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_dir, unique_filename)
                video_file.save(file_path)
                
                # Store relative path
                video_path = f"uploads/videos/{unique_filename}"
        
        # Create blog
        blog = CommunityService.create_blog(
            user_id=current_user,
            title=title,
            content=content,
            tags=tags,
            community_id=request.form.get('community_id'),
            video_url=video_path
        )
        
        return jsonify({
            'success': True,
            'blog': blog
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/blogs/<int:post_id>', methods=['DELETE'])
@token_required
def delete_blog_post(current_user, post_id):
    """
    Delete a blog post (soft delete)
    Only the author can delete
    """
    try:
        result = CommunityService.delete_blog(post_id, current_user)
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


@bp.route('/api/community/post', methods=['POST'])
@token_required
def create_post(current_user):
    """
    Unified endpoint to create any type of post (blog or feedback)
    
    Logic:
    - Saves user_id with content
    - Calculates read time for blogs
    - Updates community post count if applicable
    - Creates notifications for relevant users
    - Returns post data for feed ranking
    
    Accepts: {
        post_type: 'blog' | 'feedback',
        content: string (required),
        title: string (required for blogs),
        category: string (optional),
        tags: array (optional),
        community_id: int (optional)
    }
    Returns: {success, post, message}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'post_type' not in data or 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'post_type and content are required'
            }), 400
        
        # Create post using unified service method
        result = CommunityService.create_post(
            user_id=current_user,
            post_type=data['post_type'],
            content=data['content'],
            title=data.get('title'),
            category=data.get('category'),
            tags=data.get('tags'),
            community_id=data.get('community_id')
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


@bp.route('/api/community/posts', methods=['GET'])
@token_required
def get_posts(current_user):
    """
    Get posts with optional filtering
    
    Query Parameters:
    - type: Filter by post type ('blog', 'feedback', or omit for all)
    - user_id: Filter by author (optional)
    - limit: Maximum number of posts (default 50, max 100)
    
    Returns: {success, posts, count}
    """
    try:
        # Get query parameters
        post_type = request.args.get('type', None)
        user_id = request.args.get('user_id', None)
        limit = int(request.args.get('limit', 50))
        limit = min(max(limit, 1), 100)  # Clamp between 1 and 100
        
        # Convert user_id to int if provided
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid user_id format'
                }), 400
        
        # Get posts
        posts = CommunityService.get_posts(
            post_type=post_type,
            limit=limit,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'posts': posts,
            'count': len(posts)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/community/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def add_comment(current_user, post_id):
    """
    Phase 9: Add a comment to a post
    Triggers notification when someone comments
    
    Accepts: {content, parent_comment_id (optional)}
    Returns: {success, comment}
    """
    try:
        data = request.get_json()
        
        if 'content' not in data:
            return jsonify({
                'success': False,
                'message': 'Content is required'
            }), 400
        
        result = CommunityService.add_comment(
            user_id=current_user,
            post_id=post_id,
            content=data['content'],
            parent_comment_id=data.get('parent_comment_id')
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


@bp.route('/api/community/posts/<int:post_id>/like', methods=['POST'])
@token_required
def like_post(current_user, post_id):
    """
    Phase 9: Toggle like on a post
    Triggers notification when someone likes post
    
    Returns: {success, action}
    """
    try:
        result = CommunityService.toggle_like(
            user_id=current_user,
            post_id=post_id
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


@bp.route('/api/community/comments/<int:comment_id>/like', methods=['POST'])
@token_required
def like_comment(current_user, comment_id):
    """
    Phase 9: Toggle like on a comment
    Triggers notification when someone likes comment
    
    Returns: {success, action}
    """
    try:
        result = CommunityService.toggle_like(
            user_id=current_user,
            comment_id=comment_id
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
