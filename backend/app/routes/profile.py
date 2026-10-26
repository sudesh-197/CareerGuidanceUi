"""User profile and profile-picture upload."""

import datetime
import os
import uuid

from flask import Blueprint, jsonify, request

from app.auth import token_required
from app.config import PROFILE_PICTURE_DIR
from app.extensions import db
from app.models.community import UserProfile
from app.models.user import User

bp = Blueprint('profile', __name__)


@bp.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Get user profile (protected route)
    Requires: Authorization header with Bearer token
    Returns: {success, user, profile}
    """
    try:
        # Get user from database
        user = User.query.get(current_user)
        
        if not user or user.is_deleted or not user.is_active:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get user profile for Reach-Out feature
        user_profile = UserProfile.query.filter_by(user_id=current_user).first()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'profile': user_profile.to_dict() if user_profile else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/profile', methods=['PUT', 'PATCH'])
@token_required
def update_profile(current_user):
    """
    Update user profile for Reach-Out matching
    Requires: Authorization header with Bearer token
    Expected JSON: {
        skills: ["Python", "SQL", ...],
        interests: ["AI", "Data Science", ...],
        domains: ["Data Science", ...],
        bio: "About me...",
        location: "City, Country",
        website: "https://...",
        experience_years: 3,
        projects_count: 5
    }
    Returns: {success, profile, message}
    """
    try:
        
        data = request.get_json()
        
        # Get or create user profile
        user_profile = UserProfile.query.filter_by(user_id=current_user).first()
        
        if not user_profile:
            # Create new profile if doesn't exist
            user = User.query.get(current_user)
            user_profile = UserProfile(
                user_id=current_user,
                domains=[user.domain] if user and user.domain else []
            )
            db.session.add(user_profile)
        
        # Update fields if provided
        if 'skills' in data:
            user_profile.skills = data['skills'] if isinstance(data['skills'], list) else []
        
        if 'interests' in data:
            user_profile.interests = data['interests'] if isinstance(data['interests'], list) else []
        
        if 'domains' in data:
            user_profile.domains = data['domains'] if isinstance(data['domains'], list) else []
        
        if 'bio' in data:
            user_profile.bio = data['bio']
        
        if 'location' in data:
            user_profile.location = data['location']
        
        if 'website' in data:
            user_profile.website = data['website']
        
        if 'experience_years' in data:
            user_profile.experience_years = int(data['experience_years']) if data['experience_years'] else 0
        
        if 'projects_count' in data:
            user_profile.projects_count = int(data['projects_count']) if data['projects_count'] else 0
        
        user_profile.updated_at = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'profile': user_profile.to_dict(),
            'message': 'Profile updated successfully! You can now see matching profiles in Reach-Out.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/user', methods=['PUT', 'PATCH'])
@token_required
def update_user(current_user):
    """
    Update basic user fields: name, domain, email
    Accepts: {name, domain, email}
    Returns: {success, user}
    """
    try:
        data = request.get_json()
        user = User.query.get(current_user)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        if 'name' in data and data['name'].strip():
            user.name = data['name'].strip()
        if 'domain' in data:
            user.domain = data['domain'].strip() if data['domain'] else user.domain
        if 'email' in data and data['email'].strip():
            # Check email not taken by another user
            existing = User.query.filter(
                User.email == data['email'].lower().strip(),
                User.id != current_user,
                User.is_deleted == False
            ).first()
            if existing:
                return jsonify({'success': False, 'message': 'Email already in use'}), 400
            user.email = data['email'].lower().strip()

        user.updated_at = datetime.datetime.utcnow()
        db.session.commit()

        return jsonify({'success': True, 'user': user.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/upload/profile-picture', methods=['POST'])
@token_required
def upload_profile_picture(current_user):
    """
    Upload a profile picture for the current user.
    Accepts: multipart/form-data with 'picture' file field
    Returns: {success, profile_picture_url}
    """
    try:
        if 'picture' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400

        file = request.files['picture']
        if not file or file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        # Validate file type
        allowed = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in allowed:
            return jsonify({'success': False, 'message': 'Invalid file type. Use PNG, JPG, GIF or WEBP'}), 400

        # Save file
        unique_filename = f"{uuid.uuid4().hex}_{current_user}.{ext}"
        upload_dir = PROFILE_PICTURE_DIR
        os.makedirs(upload_dir, exist_ok=True)
        file.save(os.path.join(upload_dir, unique_filename))

        url = f"/uploads/profile_pictures/{unique_filename}"

        # Update user record
        user = User.query.get(current_user)
        if user:
            user.profile_picture = url
            db.session.commit()

        return jsonify({'success': True, 'profile_picture_url': url}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
