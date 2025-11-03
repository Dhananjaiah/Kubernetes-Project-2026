"""
Order Service - Handle order management
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
    config = get_config(config_name)
    app.config.from_object(config)
    
    setup_logging(app)
    CORS(app)
    register_error_handlers(app)
    register_blueprints(app)
    
    app.logger.info(f"Order service started in {config_name} mode")
    return app
