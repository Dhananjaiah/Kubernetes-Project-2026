"""
WSGI entry point for production deployment
"""
import os
import time
from app import create_app
from app.services.database import DatabaseService
from app.config import get_config

# Create Flask application
app = create_app()

# Initialize database on startup
if __name__ != '__main__':
    # Running under gunicorn or other WSGI server
    app.logger.info("Initializing database...")
    time.sleep(5)  # Wait for database to be ready
    
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    
    if db_service.init_database():
        app.logger.info("Database initialized successfully")
    else:
        app.logger.warning("Database initialization failed")

if __name__ == '__main__':
    # Running directly for development
    app.logger.info("Starting development server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
