"""JWT helpers shared by every blueprint."""

import datetime
from functools import wraps

import jwt
from flask import current_app, jsonify, request

TOKEN_LIFETIME = datetime.timedelta(days=7)


def create_access_token(user_id, email):
    """Return a signed JWT for the given user (valid for 7 days)."""
    return jwt.encode({
        'user_id': user_id,
        'email': email,
        'exp': datetime.datetime.utcnow() + TOKEN_LIFETIME
    }, current_app.config['SECRET_KEY'], algorithm="HS256")


def token_required(f):
    """Require a valid ``Authorization: Bearer <token>`` header.

    The wrapped view receives the authenticated user id as its first argument.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Invalid token format'
                }), 401

        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is missing'
            }), 401

        try:
            # Decode JWT token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user_id']  # Get user from token
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token has expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Invalid token'
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated
