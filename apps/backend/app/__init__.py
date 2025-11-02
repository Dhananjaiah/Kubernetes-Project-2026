"""
Backend API Service
Production-grade Flask application with proper structure
"""
from flask import Flask
from flask_cors import CORS
import logging
import os

from app.config import get_config
from app.middleware.logging import setup_logging
from app.middleware.error_handlers import register_error_handlers
from app.api import register_blueprints


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(app)
    
    # Enable CORS
    CORS(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints (API routes)
    register_blueprints(app)
    
    # Log startup
    app.logger.info(f"Application started in {config_name} mode")
    
    return app
