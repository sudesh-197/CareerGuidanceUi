"""Application-wide error handlers and CORS pre-flight handling."""

from flask import current_app, jsonify, request


def register_error_handlers(app):
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({'success': False, 'message': 'Too many requests. Please try again later.'}), 429

    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({
            'success': False,
            'message': 'Uploaded file is too large'
        }), 413

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Endpoint not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

    # Handle OPTIONS requests for CORS preflight
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = current_app.make_default_options_response()
            return response
