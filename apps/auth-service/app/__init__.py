"""
Authentication Service
User authentication and authorization with JWT
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
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
    
    # Setup JWT
    jwt = JWTManager(app)
    
    # Setup logging
    setup_logging(app)
    
    # Enable CORS
    CORS(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    app.logger.info(f"Auth service started in {config_name} mode")
    
    return app
