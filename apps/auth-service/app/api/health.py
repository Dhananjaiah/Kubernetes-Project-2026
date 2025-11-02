"""
Health check endpoints
"""
from flask import Blueprint, jsonify, current_app
import os

from app.services.database import DatabaseService
from app.config import get_config

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes probes"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    
    try:
        db_healthy = db_service.health_check()
        db_status = 'connected' if db_healthy else 'disconnected'
    except Exception as e:
        db_status = f'error: {str(e)}'
        db_healthy = False
    
    response = {
        'status': 'healthy' if db_healthy else 'unhealthy',
        'service': 'auth-service',
        'database': db_status,
        'environment': config.ENVIRONMENT,
        'version': config.API_VERSION
    }
    
    status_code = 200 if db_healthy else 503
    return jsonify(response), status_code


@health_bp.route('/ready', methods=['GET'])
def readiness():
    """Readiness probe"""
    config = get_config(os.getenv('FLASK_ENV', 'development'))
    db_service = DatabaseService(config)
    
    try:
        db_ready = db_service.health_check()
    except Exception:
        db_ready = False
    
    if db_ready:
        return jsonify({'status': 'ready'}), 200
    else:
        return jsonify({'status': 'not ready'}), 503


@health_bp.route('/live', methods=['GET'])
def liveness():
    """Liveness probe"""
    return jsonify({'status': 'alive'}), 200
