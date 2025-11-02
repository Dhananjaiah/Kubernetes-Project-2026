"""
API routes registration
"""
from flask import Flask
from app.api.health import health_bp
from app.api.orders import orders_bp


def register_blueprints(app: Flask):
    """Register all API blueprints"""
    app.register_blueprint(health_bp)
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.logger.info("Blueprints registered")
