"""
WSGI entry point for Auth Service
"""
import os
import time
from app import create_app
from app.services.database import DatabaseService
from app.services.auth_service import AuthService
from app.config import get_config

# Create Flask application
app = create_app()

# Initialize database on startup
if __name__ != '__main__':
    app.logger.info("Initializing auth service database...")
    time.sleep(5)  # Wait for database to be ready
    
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    auth_service = AuthService(db_service)
    
    if auth_service.init_users_table():
        app.logger.info("Auth database initialized successfully")
    else:
        app.logger.warning("Auth database initialization failed")

if __name__ == '__main__':
    app.logger.info("Starting auth service development server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
