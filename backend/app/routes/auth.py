"""Authentication: signup, login and password reset."""

import datetime
import logging
import os
import secrets

from flask import Blueprint, current_app, jsonify, request
from flask_mail import Message as MailMessage

from app.auth import create_access_token
from app.extensions import db, limiter, mail
from app.models.community import UserProfile
from app.models.user import User

bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


# In-memory store for password reset tokens: { token: { user_id, expires_at } }
_reset_tokens = {}


@bp.route('/api/signup', methods=['POST'])
@limiter.limit("10 per minute")
def signup():
    """
    User signup endpoint
    Expected JSON: {name, email, password, domain}
    Returns: {success, token, user}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'domain']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        name = data['name']
        email = data['email'].lower().strip()
        password = data['password']
        domain = data['domain']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email, is_deleted=False).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400
        
        # Create new user
        user = User(name=name, email=email, domain=domain)
        user.set_password(password)
        
        # Optional profile picture URL (set after upload via /api/upload/profile-picture)
        if data.get('profile_picture'):
            user.profile_picture = data['profile_picture']
        
        db.session.add(user)
        db.session.flush()  # Get user.id before commit
        
        # Automatically create UserProfile for Reach-Out feature
        user_profile = UserProfile(
            user_id=user.id,
            domains=[domain] if domain else [],
            skills=[],  # User can update later
            interests=[],  # User can update later
            experience_years=0,
            projects_count=0
        )
        db.session.add(user_profile)
        db.session.commit()
        
        # Generate JWT token
        token = create_access_token(user.id, email)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user.to_dict(),
            'message': 'Account created successfully! Complete your profile to get better matches.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    User login endpoint
    Expected JSON: {email, password}
    Returns: {success, token, user}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user by email
        user = User.query.filter_by(email=email, is_deleted=False, is_active=True).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        # Update last login
        user.last_login = datetime.datetime.utcnow()
        db.session.commit()
        
        # Generate JWT token
        token = create_access_token(user.id, email)
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@bp.route('/api/forgot-password', methods=['POST'])
@limiter.limit("5 per minute")
def forgot_password():
    """
    Send password reset email with a one-time token link.
    Body: { email }
    """
    try:
        data = request.get_json()
        email = (data.get('email') or '').strip().lower()
        if not email:
            return jsonify({'success': False, 'message': 'Email is required'}), 400

        user = User.query.filter_by(email=email, is_deleted=False).first()
        # Always return success to avoid email enumeration
        if not user:
            return jsonify({'success': True, 'message': 'If that email exists, a reset link has been sent.'}), 200

        # Generate a secure token valid for 15 minutes
        token = secrets.token_urlsafe(32)
        _reset_tokens[token] = {
            'user_id': user.id,
            'expires_at': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        }

        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        reset_link = f'{frontend_url}/reset-password?token={token}'

        mail_username = current_app.config.get('MAIL_USERNAME', '')
        mail_password = current_app.config.get('MAIL_PASSWORD', '')
        if not mail_username or mail_username == 'your_gmail@gmail.com' or not mail_password or mail_password == 'your_app_password_here':
            # No email configured. Only expose the link in development, otherwise anyone
            # who knows an email address could take over that account.
            if current_app.debug or current_app.config.get('ALLOW_DEV_RESET_LINK'):
                return jsonify({
                    'success': True,
                    'message': 'Reset link generated (email not configured).',
                    'dev_reset_link': reset_link
                }), 200
            logger.warning('Password reset requested but e-mail is not configured (MAIL_USERNAME/MAIL_PASSWORD)')
            return jsonify({'success': True, 'message': 'If that email exists, a reset link has been sent.'}), 200

        msg = MailMessage(
            subject='CareerAI — Reset Your Password',
            recipients=[user.email],
            html=f"""
            <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:32px;background:#1a1a2e;color:#e0e0e0;border-radius:12px;">
              <h2 style="color:#7c3aed;">Reset Your Password</h2>
              <p>Hi <strong>{user.name}</strong>,</p>
              <p>We received a request to reset your CareerAI password. Click the button below — this link expires in <strong>15 minutes</strong>.</p>
              <a href="{reset_link}" style="display:inline-block;margin:24px 0;padding:12px 28px;background:#7c3aed;color:#fff;border-radius:8px;text-decoration:none;font-weight:bold;">Reset Password</a>
              <p style="color:#888;font-size:13px;">If you didn't request this, you can safely ignore this email.</p>
            </div>
            """
        )
        mail.send(msg)

        return jsonify({'success': True, 'message': 'Password reset email sent. Check your inbox.'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/api/reset-password', methods=['POST'])
@limiter.limit("10 per minute")
def reset_password():
    """
    Reset password using the token from the email link.
    Body: { token, new_password }
    """
    try:
        data = request.get_json()
        token = (data.get('token') or '').strip()
        new_password = data.get('new_password', '')

        if not token or not new_password:
            return jsonify({'success': False, 'message': 'Token and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

        entry = _reset_tokens.get(token)
        if not entry:
            return jsonify({'success': False, 'message': 'Invalid or expired reset link'}), 400

        if datetime.datetime.utcnow() > entry['expires_at']:
            del _reset_tokens[token]
            return jsonify({'success': False, 'message': 'Reset link has expired. Please request a new one.'}), 400

        user = User.query.get(entry['user_id'])
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        user.set_password(new_password)
        db.session.commit()

        # Invalidate token after use
        del _reset_tokens[token]

        return jsonify({'success': True, 'message': 'Password reset successfully. You can now log in.'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
