"""Static media served from the uploads folder."""

from flask import Blueprint, jsonify, send_from_directory

from app.config import COMMUNITY_IMAGE_DIR, PROFILE_PICTURE_DIR, VIDEO_DIR

bp = Blueprint('media', __name__)


@bp.route('/uploads/profile_pictures/<filename>')
def serve_profile_picture(filename):
    """Serve uploaded profile pictures"""
    try:
        upload_dir = PROFILE_PICTURE_DIR
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 404


@bp.route('/api/community/videos/<path:filename>', methods=['GET'])
def serve_video(filename):
    """
    Serve uploaded video files
    """
    try:
        
        upload_dir = VIDEO_DIR
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Video not found'
        }), 404


@bp.route('/uploads/community_images/<filename>')
def serve_community_image(filename):
    """Serve uploaded community images"""
    try:
        upload_dir = COMMUNITY_IMAGE_DIR
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Image not found'
        }), 404
