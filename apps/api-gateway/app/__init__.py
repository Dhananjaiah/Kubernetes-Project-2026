"""
API Gateway - Central entry point for all microservices
"""
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os

from app.config import get_config
from app.middleware.logging import setup_logging
from app.middleware.error_handlers import register_error_handlers
from app.routes import register_routes


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per minute"]
    )
    
    setup_logging(app)
    CORS(app)
    register_error_handlers(app)
    register_routes(app)
    
    app.logger.info(f"API Gateway started in {config_name} mode")
    return app
