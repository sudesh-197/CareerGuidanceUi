"""CareerAI backend: Flask application factory."""

import logging

from flask import Flask
from flask_cors import CORS

from app.config import Config, DEFAULT_SECRET_KEY
from app.errors import register_error_handlers
from app.extensions import db, limiter, mail
from app.routes import register_blueprints

logger = logging.getLogger(__name__)


def _create_tables(app):
    """Create any missing tables (importing the model modules registers them)."""
    with app.app_context():
        from app.models import community, explore_cache, progress, user  # noqa: F401
        db.create_all()
        logger.info("✓ Database initialized: %s", app.config['SQLALCHEMY_DATABASE_URI'])


def _register_explore(app):
    """The Explore module is optional: a failure to load it must not stop the API."""
    try:
        from app.explore.routes import explore_bp
        limit = app.config.get('EXPLORE_RATE_LIMIT')
        if limit:
            limiter.limit(limit)(explore_bp)
        app.register_blueprint(explore_bp)
        logger.info("✓ Explore blueprint registered")
    except Exception as exc:
        logger.warning("⚠ Explore blueprint not loaded: %s", exc)


def create_app(config_object=Config):
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    app = Flask(__name__)
    app.config.from_object(config_object)

    if app.config['SECRET_KEY'] == DEFAULT_SECRET_KEY:
        logger.warning("⚠ SECRET_KEY is not set - using the insecure built-in default. "
                       "Set SECRET_KEY in backend/.env before deploying.")

    mail.init_app(app)
    db.init_app(app)
    _create_tables(app)

    # CORS - must be configured before the routes handle requests
    origins = app.config['CORS_ORIGINS']
    origins = '*' if origins == ['*'] else origins
    CORS(app,
         resources={
             r"/api/*": {"origins": origins},
             r"/uploads/*": {"origins": origins}
         },
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"]
         )

    limiter.init_app(app)
    register_error_handlers(app)
    register_blueprints(app)
    _register_explore(app)
    return app
