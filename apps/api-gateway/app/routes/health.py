"""
Health check endpoints
"""
from flask import Blueprint, jsonify, current_app
import os

# from app.services.database import DatabaseService
from app.config import get_config
import sys

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    
    response = {
        'status': 'healthy',
        'service': 'api-gateway',
        'environment': config.ENVIRONMENT,
        'version': config.API_VERSION
    }
    
    return jsonify(response), 200


@health_bp.route('/ready', methods=['GET'])
def readiness():
    """Readiness probe"""
    return jsonify({'status': 'ready'}), 200


@health_bp.route('/live', methods=['GET'])
def liveness():
    """Liveness probe"""
    return jsonify({'status': 'alive'}), 200
