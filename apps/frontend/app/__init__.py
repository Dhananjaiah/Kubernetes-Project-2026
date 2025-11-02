"""
Frontend Service - User interface
"""
from flask import Flask
import logging
import os

from app.config import get_config
from app.middleware.logging import setup_logging
from app.api import register_blueprints


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    config = get_config(config_name)
    app.config.from_object(config)
    
    setup_logging(app)
    register_blueprints(app)
    
    app.logger.info(f"Frontend service started in {config_name} mode")
    return app
