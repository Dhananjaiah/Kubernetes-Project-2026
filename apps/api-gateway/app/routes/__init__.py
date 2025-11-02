"""
API Gateway routes registration
"""
from flask import Flask
from app.routes.gateway import gateway_bp
from app.routes.health import health_bp


def register_routes(app: Flask):
    """Register all routes"""
    app.register_blueprint(health_bp)
    app.register_blueprint(gateway_bp, url_prefix='/api')
    app.logger.info("Routes registered")
