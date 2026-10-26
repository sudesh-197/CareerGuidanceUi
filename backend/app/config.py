"""
Application configuration and filesystem locations.

Every value can be overridden with an environment variable (see ``.env.example``).
Defaults match the behaviour of the original single-file backend, so existing
databases, uploads and issued login tokens keep working.
"""

import os

try:  # python-dotenv is optional
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

# backend/  (parent of the ``app`` package)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if load_dotenv:
    load_dotenv(os.path.join(BACKEND_DIR, '.env'))

# User uploads. URLs such as /uploads/profile_pictures/<file> are served from here.
UPLOAD_DIR = os.path.join(BACKEND_DIR, 'uploads')
PROFILE_PICTURE_DIR = os.path.join(UPLOAD_DIR, 'profile_pictures')
VIDEO_DIR = os.path.join(UPLOAD_DIR, 'videos')
COMMUNITY_IMAGE_DIR = os.path.join(UPLOAD_DIR, 'community_images')

DEFAULT_SECRET_KEY = 'your-secret-key-change-this-in-production'
DEFAULT_DATABASE_PATH = os.path.join(BACKEND_DIR, 'career_guidance.db')


def _env_flag(name, default='0'):
    return os.environ.get(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


class Config:
    """Flask configuration (read once at import time, after .env is loaded)."""

    SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DEFAULT_DATABASE_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail (Gmail SMTP by default)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', '')

    # Upload size guard (the original had no limit at all).
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_UPLOAD_MB', 500)) * 1024 * 1024

    # CORS: comma separated list of origins, or "*" (original behaviour).
    CORS_ORIGINS = [o.strip() for o in os.environ.get('CORS_ORIGINS', '*').split(',') if o.strip()]

    # Optional rate limit for every /api/explore route, e.g. "30 per minute".
    # The original code tried to apply one but it never took effect; empty = off.
    EXPLORE_RATE_LIMIT = os.environ.get('EXPLORE_RATE_LIMIT', '').strip()

    # Development helpers. Both are OFF unless FLASK_DEBUG=1 (the start scripts set it).
    DEBUG = _env_flag('FLASK_DEBUG')
    ALLOW_DEV_RESET_LINK = _env_flag('ALLOW_DEV_RESET_LINK')

    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')


HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
PORT = int(os.environ.get('PORT', 5000))
