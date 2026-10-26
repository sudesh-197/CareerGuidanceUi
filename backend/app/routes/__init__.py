"""Blueprint registry: one module per feature area."""

from importlib import import_module

BLUEPRINT_MODULES = ['auth', 'profile', 'media', 'analysis', 'postmatrics', 'routine', 'progress', 'community', 'content', 'messaging', 'notifications']


def register_blueprints(app):
    for name in BLUEPRINT_MODULES:
        app.register_blueprint(import_module(f'{__name__}.{name}').bp)
