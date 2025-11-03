"""
Frontend routes registration
"""
from flask import Flask
from app.api.views import views_bp


def register_blueprints(app: Flask):
    """Register all blueprints"""
    app.register_blueprint(views_bp)
    app.logger.info("Blueprints registered")
