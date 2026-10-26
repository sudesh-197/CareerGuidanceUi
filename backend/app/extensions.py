"""Flask extension instances, created unbound and attached in ``create_app``."""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mail = Mail()

# Protects expensive endpoints without blocking the whole app (no default limits).
limiter = Limiter(get_remote_address, default_limits=[], storage_uri='memory://')
