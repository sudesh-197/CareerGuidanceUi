"""Development server entry point:  ``python run.py``  (from the backend folder)."""

from app import create_app
from app.config import HOST, PORT

app = create_app()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 Flask Backend Server Starting...")
    print("=" * 60)
    print(f"📍 Backend URL: http://localhost:{PORT}")
    print(f"🗄️  Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"🐞 Debug mode: {'ON' if app.config['DEBUG'] else 'off'}")
    print("=" * 60)
    print("\n✅ Server is ready! Waiting for requests...\n")

    app.run(debug=app.config['DEBUG'], host=HOST, port=PORT, use_reloader=False)
