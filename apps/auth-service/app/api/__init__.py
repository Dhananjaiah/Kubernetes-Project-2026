"""
API routes registration
"""
from flask import Flask
from app.api.health import health_bp
from app.api.auth import auth_bp


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    app.logger.info("Blueprints registered")
